from __future__ import absolute_import, unicode_literals
import logging
import functools
import threading
import ast
import time
from django.http import HttpResponse
from libs import send_email, util
from libs import call_inception
from .models import (
    DatabaseList,
    Account,
    globalpermissions,
    SqlOrder,
    SqlRecord,
    grained
)

from psycopg2 import Error as PostgresError


CUSTOM_ERROR = logging.getLogger('Yearning.core.views')


def set_auth_group(user, ddlcon = [], dmlcon = [], querycon = [], **kwargs):
    perm = {
        'ddl': '0',
        'ddlcon': [],
        'dml': '0',
        'dmlcon': [],
        'dic': '0',
        'diccon': [],
        'dicedit': '0',
        'user': '0',
        'base': '0',
        'dicexport': '0',
        'person': [],
        'query': '0',
        'querycon': []
    }
    group = Account.objects.filter(username=user).first()
    group_list = str(group.auth_group).split(',')
    for group_name in group_list:
        auth = grained.objects.filter(username=group_name).first()
        if auth:
            if ddlcon:
                tmp_ddlcon = set(auth.permissions['ddlcon'])& set(ddlcon)
                if tmp_ddlcon:
                    perm['ddlcon'] = list(set(perm['ddlcon'])| tmp_ddlcon)
                else:
                    continue
            else:
                perm['ddlcon'] = list(set(auth.permissions['ddlcon']+ perm['ddlcon']))

            if dmlcon:
                tmp_dmlcon = set(auth.permissions['dmlcon'])& set(dmlcon)
                if tmp_dmlcon:
                    perm['dmlcon'] += list(set(perm['dmlcon'])| tmp_dmlcon)
                else:
                    continue
            else:
                perm['dmlcon'] = list(set(auth.permissions['dmlcon']+ perm['dmlcon']))

            if querycon:
                tmp_querycon = set(auth.permissions['querycon'])& set(querycon)
                if tmp_querycon:
                    perm['querycon'] += list(set(perm['querycon'])| tmp_querycon)
                else:
                    continue
            else:
                perm['querycon'] = list(set(auth.permissions['querycon']+ perm['querycon']))
            perm['diccon'] = list(set(auth.permissions['diccon']+ perm['diccon']))
            perm['person'] = list(set(auth.permissions['person']+ perm['person']))
            for k, v in auth.permissions.items():
                if isinstance(v, str):
                    if int(perm[k]) or int(v):
                        perm[k] = '1'
                    else:
                        perm[k] = '0'

    return perm


def grained_permissions(func):
    '''

    :argument 装饰器函数,校验细化权限。非法请求直接返回401交由前端判断状态码

    '''

    @functools.wraps(func)
    def wrapper(self, request, args=None):
        if request.user.group == "admin":
            return func(self, request, args)
        if request.method == "PUT" and args != 'connection':
            return func(self, request, args)
        else:
            if request.method == "GET":
                permissions_type = request.GET.get('permissions_type')
            else:
                permissions_type = request.data['permissions_type']
            if permissions_type == 'own_space' or permissions_type == 'query':
                return func(self, request, args)
            else:
                group = set_auth_group(request.user)
                if group is not None and group[permissions_type] == '1':
                    return func(self, request, args)
                else:
                    return HttpResponse(status=401,content='没有该功能权限')

    return wrapper


class order_push_message(threading.Thread):
    '''

    :argument 同意执行工单调用该方法异步处理数据

    '''

    def __init__(self, addr_ip, work_id, from_user, to_user):
        super().__init__()
        self.work_id= work_id
        self.addr_ip = addr_ip
        self.order = SqlOrder.objects.filter(work_id= work_id).first()
        self.from_user = from_user
        self.to_user = to_user
        self.title = f'工单:{self.order.work_id}审核通过通知'

    def run(self):
        self.execute()
        self.agreed()

    def execute(self):

        '''

        :argument 将获得的sql语句提交给inception执行并将返回结果写入SqlRecord表,最后更改该工单SqlOrder表中的status

        :param
                self.order
                self.id

        :return: none

        '''
        time.sleep(self.order.delay * 60)
        try:
            res = None
            detail = DatabaseList.objects.filter(id=self.order.bundle_id).first()
            _inception = detail.get_inception(database = self.order.basename)
            with _inception as f:
                res = f.Execute(sql=self.order.sql, backup=self.order.backup)
                for i in res:
                    if i['errlevel'] not in [0, 1]:
                        SqlOrder.objects.filter(work_id=self.order.work_id).update(status=4)
                    SqlRecord.objects.get_or_create(
                        state=i['stagestatus'],
                        sql=i['sql'],
                        error=i['errormessage'],
                        workid=self.order.work_id,
                        affectrow=i['affected_rows'],
                        sequence=i['sequence'],
                        execute_time=i['execute_time'],
                        SQLSHA1=i['SQLSHA1'],
                        backup_dbname=i['backup_dbname']
                    )
        except Exception as e:
            CUSTOM_ERROR.error(f'{e.__class__.__name__}--SQL执行失败: {e}')
        finally:
            check = SqlOrder.objects.filter(work_id=self.order.work_id).first()
            if check.status != 4:
                SqlOrder.objects.filter(work_id=self.order.work_id).update(status=5)

    def agreed(self):

        '''

        :argument 将执行的结果通过站内信,email,dingding 发送

        :param   self.from_user
                 self.to_user
                 self.title
                 self.order
                 self.addr_ip

        :return: none

        '''
        t = threading.Thread(target=order_push_message.con_close, args=(self,))
        t.start()
        t.join()

    def con_close(self):

        content = DatabaseList.objects.filter(id=self.order.bundle_id).first()
        mail = Account.objects.filter(username=self.to_user).first()
        tag = globalpermissions.objects.filter(authorization='global').first()

        if tag.message['ding']:
            try:
                util.dingding(
                    content='工单执行通知\n工单编号:%s\n发起人:%s\n地址:%s\n工单备注:%s\n状态:已执行\n备注:%s'
                            % (
                                self.order.work_id, self.order.username, self.addr_ip, self.order.text,
                                content.after),
                    url=ding_url())
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}--钉钉推送失败: {e}')

        if tag.message['mail']:
            try:
                if mail.email:
                    mess_info = {
                        'workid': self.order.work_id,
                        'to_user': self.order.username,
                        'addr': self.addr_ip,
                        'text': self.order.text,
                        'note': content.after}
                    put_mess = send_email.send_email(to_addr=mail.email, ssl=tag.message['ssl'])
                    put_mess.send_mail(mail_data=mess_info, type=0)
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}--邮箱推送失败: {e}')


class rejected_push_messages(threading.Thread):
    '''

    :argument 驳回工单调用该方法异步处理数据

    '''

    def __init__(self, _tmpData, to_user, addr_ip, text):
        super().__init__()
        self.to_user = to_user
        self._tmpData = _tmpData
        self.addr_ip = addr_ip
        self.text = text

    def run(self):
        self.execute()

    def execute(self):

        '''

        :argument 更改该工单SqlOrder表中的status

        :param
                self._tmpData
                self.addr_ip
                self.text
                self.to_user

        :return: none

        '''
        mail = Account.objects.filter(username=self.to_user).first()
        tag = globalpermissions.objects.filter(authorization='global').first()
        if tag.message['ding']:
            try:
                util.dingding(
                    content='工单驳回通知\n工单编号:%s\n发起人:%s\n地址:%s\n驳回说明:%s\n状态:驳回'
                            % (self._tmpData['work_id'], self.to_user, self.addr_ip, self.text), url=ding_url())
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}--钉钉推送失败: {e}')
        if tag.message['mail']:
            try:
                if mail.email:
                    mess_info = {
                        'workid': self._tmpData['work_id'],
                        'to_user': self.to_user,
                        'addr': self.addr_ip,
                        'rejected': self.text}
                    put_mess = send_email.send_email(to_addr=mail.email, ssl=tag.message['ssl'])
                    put_mess.send_mail(mail_data=mess_info, type=1)
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}--邮箱推送失败: {e}')


class submit_push_messages(threading.Thread):
    '''

    :argument 提交工单调用该方法异步处理数据

    '''

    def __init__(self, workId, user, addr_ip, text, assigned, id):
        super().__init__()
        self.workId = workId
        self.user = user
        self.addr_ip = addr_ip
        self.text = text
        self.assigned = assigned
        self.id = id

    def run(self):
        self.submit()

    def submit(self):
        '''

        :argument 更改该工单SqlOrder表中的status

        :param
                self.workId
                self.user
                self.addr_ip
                self.text
                self.assigned
                self.id
        :return: none

        '''
        content = DatabaseList.objects.filter(id=self.id).first()
        mail = Account.objects.filter(username=self.assigned).first()
        tag = globalpermissions.objects.filter(authorization='global').first()
        if tag.message['ding']:
            try:
                util.dingding(
                    content='工单提交通知\n工单编号:%s\n发起人:%s\n地址:%s\n工单说明:%s\n状态:已提交\n备注:%s'
                            % (self.workId, self.user, self.addr_ip, self.text, content.before), url=ding_url())
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}--钉钉推送失败: {e}')
        if tag.message['mail']:
            if mail.email:
                mess_info = {
                    'workid': self.workId,
                    'to_user': self.user,
                    'addr': self.addr_ip,
                    'text': self.text,
                    'note': content.before}
                try:
                    put_mess = send_email.send_email(to_addr=mail.email, ssl=tag.message['ssl'])
                    put_mess.send_mail(mail_data=mess_info, type=99)
                except Exception as e:
                    CUSTOM_ERROR.error(f'{e.__class__.__name__}--邮箱推送失败: {e}')


def ding_url():
    un_init = util.init_conf()
    webhook = ast.literal_eval(un_init['message'])
    return webhook['webhook']
