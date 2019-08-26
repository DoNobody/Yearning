import logging
import json
from libs import baseview, util
from libs import call_inception
from core.task import submit_push_messages
from rest_framework.response import Response
from django.http import HttpResponse
from core.models import (
    DatabaseList,
    SqlOrder
)

CUSTOM_ERROR = logging.getLogger('Yearning.core.views')

conf = util.conf_path()
addr_ip = conf.ipaddress


class sqlorder(baseview.BaseView):
    '''

    :argument 手动模式工单提交相关接口api

    put   美化sql  测试sql

    post 提交工单

    '''

    def put(self, request, args=None):
        if args == 'beautify':
            try:
                data = request.data['data']
            except KeyError as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
            else:
                try:
                    res = call_inception.Inception.BeautifySQL(sql=data)
                    return HttpResponse(res)
                except Exception as e:
                    CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                    return HttpResponse(status=500)

        elif args == 'test':
            try:
                id = request.data['id']
                base = request.data['basename']
                sql = request.data['sql']
                sql = str(sql).strip('\n').strip().rstrip(';')
                data = DatabaseList.objects.filter(id=id).first()
            except KeyError as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
            else:
                try:
                    _Inception = data.get_inception(database = base)
                    with _Inception as test:
                        res = test.Check(sql=sql)
                        return Response({'result': res, 'status': 200})
                except Exception as e:
                    CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                    return HttpResponse(e)

    def post(self, request, args=None):
        try:
            data = json.loads(request.data['data'])
            tmp = json.loads(request.data['sql'])
            type_str = request.data['type']
            real_name = request.data['real_name']
            id = request.data['id']
            user = request.user
            if str(user.username) == str(data['assigned']):
                return HttpResponse("审核人不能是自己",status=401)
        except KeyError as e:
            CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
            return HttpResponse(status=500)
        else:
            try:
                x = [x.rstrip(';') for x in tmp]
                if str(x[0]).lstrip().startswith('use'):
                    del x[0]
                sql = ';'.join(x)
                sql = sql.strip(' ').rstrip(';')
                workId = util.workId()
                SqlOrder.objects.get_or_create(
                    username=request.user,
                    date=util.date(),
                    work_id=workId,
                    status=2,
                    basename=data['basename'],
                    sql=sql,
                    type=type_str,
                    text=data['text'],
                    backup=data['backup'],
                    bundle_id=id,
                    assigned=data['assigned'],
                    delay=data['delay'],
                    real_name=real_name
                )
                submit_push_messages(
                    workId=workId,
                    user=request.user,
                    addr_ip=addr_ip,
                    text=data['text'],
                    assigned=data['assigned'],
                    id=id
                ).start()
                return HttpResponse('已提交，请等待管理员审核!')
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                return HttpResponse(status=500)
