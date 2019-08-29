import logging
import json
import ast
import threading
from libs import baseview, call_inception, util, serializers, send_email
from rest_framework.response import Response
from django.http import HttpResponse
from core.models import (
    SqlOrder,
    DatabaseList,
    SqlRecord,
    Account,
    globalpermissions,
    Q
)

from django.core.paginator import Paginator
from core.task import order_push_message, rejected_push_messages

conf = util.conf_path()
addr_ip = conf.ipaddress
CUSTOM_ERROR = logging.getLogger('Yearning.core.views')


class audit(baseview.BaseView):
    '''

    :argument 审核页面相关操作api接口

    '''

    def get(self, request, args: str = None):

        '''

        :argument 审核页面数据展示请求接口

        :param None

        :return 数据条数, 数据

        '''

        try:
            page = int(request.GET.get('page'))
            username = request.user.username
            request_name = request.GET.get('username', '')
        except KeyError as e:
            CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
            return HttpResponse(status=500)
        else:
            try:
                un_init = util.init_conf()
                custom_com = ast.literal_eval(un_init['other'])
                conn_info = DatabaseList.objects.filter(delete_yn=1).all()
                conn_id_name = [{'id':con.id, 'connection_name':con.connection_name, 'computer_room':con.computer_room} for con in conn_info ]
                if request.user.group == 'admin':
                    if request_name:
                        page_sql = Q(username=username)&Q(delete_yn=1)
                    else:
                        page_sql = Q(delete_yn=1)
                else:
                    if request_name:
                        page_sql = Q(username=username)&Q(delete_yn=1)
                    else:
                        page_sql = (Q(assigned=username)|Q(username=username)|Q(exceuser=username))&Q(delete_yn=1)
                all_data = SqlOrder.objects.filter(page_sql).order_by('-id').all()
                count = len(all_data)
                start = max(0, (page - 1 ) * 20)
                end = min(count, page * 20)
                page_data = all_data[start:end]
                data = []
                for recd in page_data:
                    tmp_result = {}
                    tmp_data = serializers.SqlOrderSerializer(recd)
                    tmp_result = dict(tmp_data.data) 
                    info = [{'connection_name':con['connection_name'], 'computer_room':con['computer_room']} for con in conn_id_name if con['id'] == tmp_data.data['bundle_id']]
                    if info:
                        tmp_result.update(info[0])
                    data.append(tmp_result)
                users = Account.objects.filter(Q(group = 'perform') | Q(group = 'manager')).all()
                ser = serializers.UserINFO(users, many=True)
                return Response(
                    {'page': count, 'data': data, 'multi': custom_com['multi'], 'multi_list': ser.data})
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                return HttpResponse(status=500)

    def put(self, request, args: str = None):

        '''

        :argument 工单确认执行,驳回,二次检测接口。

        :param category 根据获得的category值执行具体的操作逻辑

        :return 提交结果信息

        '''

        try:
            work_id = request.data['work_id']
            status = request.data['status']
            c_user = request.user
        except KeyError as e:
            CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
        else:
            try:
                if c_user.group == "admin":
                    sql_str = Q(work_id=work_id)
                else:
                    sql_str = Q(work_id=work_id)&(Q(username=c_user.username)|Q(assigned=c_user.username)|Q(exceuser=c_user.username))
                order = SqlOrder.objects.filter(sql_str).first()
            except KeyError as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                return HttpResponse(status=500)
            # 驳回
            if status == 0:
                try:
                    text = request.data['text']
                    SqlOrder.objects.filter(work_id=work_id).update(status=0,rejected=text)
                    _tmpData = SqlOrder.objects.filter(work_id=work_id).values(
                        'work_id',
                        'bundle_id'
                    ).first()
                    rejected_push_messages(_tmpData, order.username, addr_ip, text).start()
                    return Response('操作成功，该请求已驳回！')
                except Exception as e:
                    CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                    return HttpResponse(status=500)
            # 同意
            elif status == 1:
                to_user = None
                try:
                    to_user = Account.objects.filter(username = request.data['to_user']).first()
                except KeyError as e:
                    CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                    return HttpResponse(status=500)
                else:
                    try:
                        if order.status != 2:
                            return Response('非法传参，触发幂等操作')
                        else:
                            if to_user:
                                SqlOrder.objects.filter(work_id=work_id).update(status=1)
                                SqlOrder.objects.filter(work_id=work_id).update(exceuser=to_user.username)
                                mail = Account.objects.filter(username=to_user.username).first()
                                threading.Thread(target=push_message, args=(
                                    {'to_user': to_user.username, 'workid': work_id, 'addr': addr_ip}, 9, request.user, mail.email,
                                    work_id,
                                    '已提交执行人')).start()
                                return Response('工单已提交执行人！')
                        return HttpResponse(status=401, content="没有权限操作")
                    except Exception as e:
                        CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                        return HttpResponse(status=500)
            #直接执行
            elif status == 3:
                if ((order.status == 2 and order.assigned == c_user.username) or
                    (order.status == 1 and order.exceuser == c_user.username)):
                    order_push_message(addr_ip, work_id, c_user.username, order.username).start()
                    SqlOrder.objects.filter(work_id=work_id).update(status=3)
                    return Response('工单审核成功!请通过记录页面查看具体执行结果')
                return HttpResponse(status=401, content="没有权限操作")

            elif status == 'test':
                if not order.sql:
                    return Response({'status': '工单内无sql语句!'})
                data = DatabaseList.objects.filter(id=order.bundle_id).first()
                try:
                    _Inception = data.get_inception(database = order.basename)
                    with _Inception as test:
                        res = test.Check(sql=order.sql)
                        return Response({'result': res, 'status': 200})
                except Exception as e:
                    CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                    return Response({'status': '请检查inception信息是否正确!'})


class del_order(baseview.BaseView):
    '''

    :argument 审核页面工单删除操作请求api

    :param data_id 根据data_id['status'] 值执行相应的删除逻辑

    :return 删除结果信息

    '''

    def post(self, request, args: str = None):
        try:
            data_id = json.loads(request.data['id'])
        except KeyError as e:
            CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
            return HttpResponse(status=500)
        else:
            try:
                for i in data_id:
                    SqlOrder.objects.filter(Q(id=i['id'])&(Q(status=0)|Q(status=4)|Q(status=5))).update(delete_yn = 0)
                return Response('工单数据删除成功!')
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                return HttpResponse(status=500)


def push_message(message=None, type=None, user=None, to_addr=None, work_id=None, status=None):
    try:
        tag = globalpermissions.objects.filter(authorization='global').first()
        if tag.message['mail']:
            try:
                put_mess = send_email.send_email(to_addr=to_addr)
                put_mess.send_mail(mail_data=message, type=type)
            except:
                pass

        if tag.message['ding']:
            un_init = util.init_conf()
            webhook = ast.literal_eval(un_init['message'])
            util.dingding(content='工单转移通知\n工单编号:%s\n发起人:%s\n状态:%s' % (work_id, user, status),
                          url=webhook['webhook'])
    except Exception as e:
        CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
