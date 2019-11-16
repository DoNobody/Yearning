import json
import logging
import datetime
import re
import threading
import simplejson
import ast
from django.http import HttpResponse
from rest_framework.response import Response
from libs.serializers import Query_review, Query_list
from libs import baseview, send_email, util
from libs import con_database
from core.models import DatabaseList, Account, querypermissions, query_order, globalpermissions, Q

CUSTOM_ERROR = logging.getLogger('Yearning.core.views')


def exclued_db_list():
    try:
        from core.models import globalpermissions

        setting = globalpermissions.objects.filter(authorization='global').first()
        exclued_database_name = setting.other.get('exclued_db_list', [])
    except Exception:
        logging.error("exclued_database_name配置错误.")
        exclued_database_name = []
    finally:
        return exclued_database_name


class DateEncoder(simplejson.JSONEncoder):  # 感谢的凉夜贡献

    def default(self, o):
        if isinstance(o, datetime.datetime) or isinstance(o, datetime.date) or isinstance(o, datetime.time):
            return o.__str__()
        return simplejson.JSONEncoder.default(self, o)


class search(baseview.BaseView):
    '''
    :argument   sql查询接口, 过滤非查询语句并返回查询结果。
                可以自由limit数目 当limit数目超过配置文件规定的最大数目时将会采用配置文件的最大数目

    '''

    def post(self, request, args=None):
        un_init = util.init_conf()
        limit = ast.literal_eval(un_init['other'])
        sql = request.data['sql']
        address = json.loads(request.data['address'])
        check = str(sql).strip().split(';\n')
        user = query_order.objects.filter(username=request.user, connection_name=address['dbcon'], query_per=1).first()
        gperm = globalpermissions.objects.filter(authorization='global').first()
        sql_first_key_list = [ i.upper() for i in gperm.other.get('query_keywd_list', [])] + ['SELECT']
        un_init = util.init_conf()
        custom_com = ast.literal_eval(un_init['other'])
        if user:
            if not all([checkStartK(item, sql_first_key_list) for item in check[-1].strip().split(';') if item]):
                return Response('只支持查询功能或删除不必要的空白行！')
            else:
                conn = DatabaseList.objects.filter(
                    connection_name=user.connection_name,
                    computer_room=user.computer_room,
                    delete_yn=1
                ).first()
                _conn = conn.get_conn(database=address['basename'], dictCursor=True)
                with _conn as f:
                    try:
                        if limit.get('limit').strip() == '':
                            CUSTOM_ERROR.error('未设置全局最大limit值，系统自动设置为1000')
                            query_sql = replace_limit(check[-1].strip(), 1000)
                        else:
                            query_sql = replace_limit(check[-1].strip(), limit.get('limit'))
                        data_set = f.search(sql=query_sql)
                    except Exception as e:
                        CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                        return HttpResponse(e)
                    else:
                        for l in data_set['data']:
                            for k, v in l.items():
                                if isinstance(v, bytes):
                                    for n in range(data_set['len']):
                                        data_set['data'][n].update({k: 'blob字段为不可呈现类型'})
                                for i in custom_com['sensitive_list']:
                                    if k == i:
                                        for n in range(data_set['len']):
                                            data_set['data'][n].update({k: '********'})
                        querypermissions.objects.create(
                            work_id=user.work_id,
                            username=request.user,
                            statements=query_sql
                        )
                    return HttpResponse(simplejson.dumps(data_set, cls=DateEncoder, bigint_as_string=True))
        else:
            return Response('非法请求,账号无查询权限！')

    def put(self, request, args: str = None):
        base = request.data.get('base','')
        table = request.data.get('table', '')
        dbcon = request.data.get('dbcon', '')
        delaytime = request.data.get('delaytime', 0)
        query_per = query_order.objects.filter(username=request.user, connection_name=dbcon, query_per=1).first()
        if query_per and query_per.query_per == 1:
            conn = DatabaseList.objects.filter(
                connection_name=query_per.connection_name,
                computer_room=query_per.computer_room,
                delete_yn = 1
            ).first()
            _conn = conn.get_conn(database=base, dictCursor=True)
            try:
                with _conn as f:
                    if delaytime and conn.dbtype == 'mysql' and conn.is_slave:
                        data_set = f.search(sql='show slave status')
                    else:
                        data_set = f.desc_table(table)
                return Response(data_set)
            except Exception as e:
                return Response({'error': '{}'.format(e)})
        else:
            return Response({'error': '非法请求,账号无查询权限！'})


def checkStartK(item, setK):
    return str(item).split('\n')[0].split(' ')[0].upper() in setK


def replace_limit(sql, limit):
    '''

    :argument 根据正则匹配分析输入信息 当limit数目超过配置文件规定的最大数目时将会采用配置文件的最大数目

    '''

    if sql[-1] != ';':
        sql += ';'
    gperm = globalpermissions.objects.filter(authorization='global').first()
    sql_first_key_list = [ i.upper() for i in gperm.other.get('query_keywd_list', [])]

    if all([checkStartK(item, sql_first_key_list) for item in sql.split(';') if item]):
        return sql
    sql_re = re.search(r'limit\s.*\d.*;', sql.lower())
    length = ''
    if sql_re is not None:
        c = re.search(r'\d.*', sql_re.group())
        if c is not None:
            if c.group().find(',') != -1:
                length = c.group()[-2]
            else:
                length = c.group().rstrip(';')
        if int(length) <= int(limit):
            return sql
        else:
            sql = re.sub(r'limit\s.*\d.*;', 'limit %s;' % limit, sql)
            return sql
    else:
        sql = sql.rstrip(';') + ' limit %s;' % limit
        return sql


class query_worklf(baseview.BaseView):

    def get(self, request, args: str = None):
        page = request.GET.get('page')
        page_number = query_order.objects.filter(delete_yn=1).count()
        start = int(page) * 20 - 20
        end = int(page) * 20
        info = query_order.objects.filter(delete_yn=1).all().order_by('-id')[start:end]
        serializers = Query_review(info, many=True)
        return Response({'page': page_number, 'data': serializers.data})

    def post(self, request, args: str = None):

        work_id = request.data['workid']
        user = request.data['user']
        data = querypermissions.objects.filter(work_id=work_id, username=user).all().order_by('-id')
        serializers = Query_list(data, many=True)
        return Response(serializers.data)

    def put(self, request, args: str = None):
        
        c_user = request.user

        if request.data['mode'] == 'put':
            instructions = request.data['instructions']
            connection_name = request.data['connection_name']
            computer_room = request.data['computer_room']
            real = request.data['real_name']
            export = request.data['export']
            audit = request.data['audit']
            un_init = util.init_conf()
            query_switch = ast.literal_eval(un_init['other'])
            query_per = 2
            work_id = util.workId()
            if not query_switch['query']:
                query_per = 2
            else:
                audit_user = Account.objects.filter(Q(username=audit)&(Q(group='admin')|Q(group='manager'))).first()
                try:
                    thread = threading.Thread(
                        target=push_message,
                        args=(
                            {'to_user': c_user.username, 'workid': work_id}, 5, c_user.username, audit_user.email, work_id,
                            '提交')
                    )
                    thread.start()
                except Exception as e:
                    CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
            query_order.objects.create(
                work_id=work_id,
                instructions=instructions,
                username=c_user,
                date=util.date(),
                query_per=query_per,
                connection_name=connection_name,
                computer_room=computer_room,
                export=export,
                audit=audit,
                time=util.date(),
                real_name=real
            )
            if not query_switch['query']:
                query_order.objects.filter(work_id=work_id).update(query_per=1)
            ## 钉钉及email站内信推送
            return Response('查询工单已提交，等待管理员审核！')

        elif request.data['mode'] == 'agree':
            try:
                work_id = request.data['work_id']
                if c_user.group == "admin":
                    sql_str = Q(work_id=work_id)
                else:
                    sql_str = Q(work_id=work_id)& Q(audit=request.user.username)
                query_info = query_order.objects.filter(sql_str).order_by('-id').first()
                query_order.objects.filter(sql_str).update(query_per=1)
                userinfo = Account.objects.filter(username=query_info.username).first()
                thread = threading.Thread(target=push_message, args=(
                    {'to_user': query_info.username, 'workid': query_info.work_id}, 6, query_info.username,
                    userinfo.email,
                    work_id, '同意'))
                thread.start()
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
            return Response('查询工单状态已更新！')

        elif request.data['mode'] == 'disagree':
            try:            
                work_id = request.data['work_id']
                if c_user.group == "admin":
                    sql_str = Q(work_id=work_id)
                else:
                    sql_str = Q(work_id=work_id)& Q(audit=request.user.username)
                query_info = query_order.objects.filter(sql_str).order_by('-id').first()
                query_order.objects.filter(sql_str).update(query_per=0)
                userinfo = Account.objects.filter(username=query_info.username).first()
                thread = threading.Thread(target=push_message, args=(
                    {'to_user': query_info.username, 'workid': query_info.work_id}, 7, query_info.username,
                    userinfo.email,
                    work_id, '驳回'))
                thread.start()
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
            return Response('查询工单状态已更新！')

        elif request.data['mode'] == 'status':
            try:
                status = query_order.objects.filter(username=request.user, query_per=1, delete_yn=1).order_by('-id').first()
                if status:
                    return Response(status.query_per)
                else:
                    status = query_order.objects.filter(username=request.user, query_per=2, delete_yn=1).order_by('-id').first()
                    return Response(status.query_per)
            except:
                return Response(0)

        elif request.data['mode'] == 'end':
            try:
                if c_user.group == "admin":
                    sql_str = Q(work_id=request.data['work_id'])
                else:
                    sql_str = Q(work_id=request.data['work_id'])&(Q(username = c_user.username)|Q(audit = c_user.username))
                query_order.objects.filter(sql_str).update(query_per=3)
                return Response('已结束查询！')
            except Exception as e:
                return HttpResponse(e)

        elif request.data['mode'] == 'info':
            data = []
            highlist = {}
            error_list = []
            databaseSet = query_order.objects.filter(username=request.user, query_per=1, delete_yn=1).all()
            for dbcon in databaseSet:
                try:
                    tablelist = []
                    conn = DatabaseList.objects.filter(connection_name=dbcon.connection_name, delete_yn=1).first()
                    if conn:
                        _conn = conn.get_conn(dictCursor=True)
                        with _conn as f:
                            db_list = f.get_dbs()
                            dataname = db_list.get('data',[])
                        children = []
                        ignore = exclued_db_list()
                        for index, uc in sorted(enumerate(dataname), reverse=True):
                            for cc in ignore:
                                if uc['Database'] == cc:
                                    del dataname[index]
                        for i in dataname:
                            _conn = conn.get_conn(database= i['Database'], dictCursor=True)
                            with _conn as f:
                                table_list = f.get_tables()
                                tablename = table_list.get('data', [])
                            highlist[i['Database']] = [{'vl': i['Database'], 'meta': '库名'}]
                            for c in tablename:
                                key = 'Tables_in_%s' % i['Database']
                                highlist[i['Database']].append({'vl': c[key], 'meta': '表名'})
                                children.append({
                                    'title': c[key]
                                })
                            tablelist.append({
                                'title': i['Database'],
                                'children': children
                            })
                            children = []
                        db_info_tree = {
                            'title': dbcon.connection_name,
                            'expand': 'true',
                            'children': tablelist,
                            'export': dbcon.export
                        }
                        data.append(db_info_tree)
                except Exception as e:
                    CUSTOM_ERROR.error(e)
                    error_list.append(str(e))
            return Response({'info': json.dumps(data), 'status': 'status', 'highlight': highlist, 'error_list': error_list})

    def delete(self, request, args: str = None):

        data = query_order.objects.filter(username=request.user, delete_yn = 1).order_by('-id').first()
        query_order.objects.filter(work_id=data.work_id).update(delete_yn = 0)
        return Response('delete Success')


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
            util.dingding(content='查询申请通知\n工单编号:%s\n发起人:%s\n状态:%s' % (work_id, user, status),
                          url=webhook['webhook'])
    except Exception as e:
        CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')


class Query_order(baseview.BaseView):

    def get(self, request, args: str = None):
        page = int(request.GET.get('page'))
        page_size = int(request.GET.get('page_size', 10))
        query_type = request.GET.get('type','0')
        if query_type == '1':
            sql_str = Q(delete_yn=1)&Q(username=request.user.username)
        elif request.user.group == "admin":
            sql_str = Q()&Q(delete_yn=1)
        elif request.user.group == "manager":
            sql_str = Q(delete_yn=1)&(Q(audit=request.user.username) | Q(username=request.user.username))
        else:
            sql_str = Q(delete_yn=1)&Q(username=request.user.username)
        pn = query_order.objects.filter(sql_str).count()
        start = (page -1) * page_size
        end = page * page_size
        user_list = query_order.objects.filter(sql_str).all().order_by('-id')[start:end]
        serializers = Query_review(user_list, many=True)
        return Response({'data': serializers.data, 'pn': pn})

    def post(self, request, args: str = None):
        work_id_list = json.loads(request.data['work_id'])
        if request.user.group == "admin":
            for i in work_id_list:
                query_order.objects.filter(work_id=i).update(delete_yn=0)
        elif request.user.group == "manager":
            for i in work_id_list:
                query_order.objects.filter(Q(work_id=i) & (Q(username=request.user.username) | Q(audit=request.user.username))).update(delete_yn=0)
        return Response('申请记录已删除!')
