import json
import logging
import ast
from django.http import HttpResponse
from rest_framework.response import Response
from libs import baseview, con_database, util
from core.task import grained_permissions, set_auth_group
from core.api import serachsql
from core.models import (
    DatabaseList,
    Account,
    SqlDictionary,
    Q
)
from libs.serializers import (
    Area,
    UserINFO,
    DBlist
)

CUSTOM_ERROR = logging.getLogger('Yearning.core.views')


class addressing(baseview.BaseView):
    '''

    :argument 连接名 库名 表名 字段名 索引名 api接口


    '''

    @grained_permissions
    def put(self, request, args=None):

        if args == 'connection':
            try:
                un_init = util.init_conf()
                custom_com = ast.literal_eval(un_init['other'])
                permission_spec = set_auth_group(request.user, **request.data)
                if request.data['permissions_type'] == 'user' or request.data['permissions_type'] == 'own_space':
                    info = DatabaseList.objects.filter(delete_yn=1).all()
                    con_name = Area(info, many=True).data
                    dic = SqlDictionary.objects.all().values('Name')
                    dic.query.distinct = ['Name']

                elif request.data['permissions_type'] == 'query':
                    con_name = []
                    if permission_spec['query'] == '1':
                        # 过滤
                        for i in permission_spec['querycon']:
                            con_instance = DatabaseList.objects.filter(connection_name=i, delete_yn=1).first()
                            if con_instance:
                                serial_db = DBlist(con_instance)
                                con_name.append(serial_db.data)
                    return Response({'assigend': permission_spec['person'], 'connection': con_name,
                                     'custom': custom_com['con_room']})
                else:
                    con_name = []
                    _type = request.data['permissions_type'] + 'con'
                    for i in permission_spec[_type]:
                        con_instance = DatabaseList.objects.filter(connection_name=i, delete_yn=1).first()
                        if con_instance:
                            serial_db = DBlist(con_instance)
                            con_name.append(serial_db.data)
                    dic = ''
                info = Account.objects.filter(Q(group='admin') | Q(group='manager')).all()
                serializers = UserINFO(info, many=True)
                return Response(
                    {
                        'connection': con_name,
                        'person': serializers.data,
                        'dic': dic,
                        'assigend': permission_spec['person'],
                        'custom': custom_com['con_room'],
                        'multi': custom_com['multi']
                    }
                )
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                return HttpResponse(status=500)

        elif args == "basename":
            try:
                con_id = request.data['id']
            except KeyError as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                return HttpResponse(status=500)
            else:
                _connection = DatabaseList.objects.filter(id=con_id).first()
                try:
                    _c = _connection.get_conn()
                    with _c as f:
                        ret = f.get_dbs()
                        res = [item[0] for item in ret['data']]
                        exclude_db = serachsql.exclued_db_list()
                        for db in exclude_db:
                            if db in res:
                                res.remove(db)
                        return Response(list(set(res)))
                except Exception as e:
                    CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                    return HttpResponse(status=500)

        elif args == 'tablename':
            try:
                data = json.loads(request.data['data'])
                basename = data['basename']
                con_id = request.data['id']
            except KeyError as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
            else:
                _connection = DatabaseList.objects.filter(id=con_id).first()
                try:
                    _c = _connection.get_conn(database=basename)
                    with _c as f:
                        ret = f.get_tables()
                        res = [item[0] for item in ret["data"]]
                        return Response(res)
                except Exception as e:
                    CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                    return HttpResponse(status=500)

        elif args == 'field':
            try:
                connection_info = json.loads(request.data['connection_info'])
                table = connection_info['tablename']
                basename = connection_info['basename']
                con_id = request.data['id']
            except KeyError as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
            else:
                try:
                    _connection = DatabaseList.objects.filter(id=con_id).first()
                    _c = _connection.get_conn(database=basename,dictCursor=True)
                    with _c as f:
                        desc_table = f.desc_table(table_name=table)
                        create_table_sql = f.get_create_table_sql(table_name=table)
                        table_index = f.get_index(table_name=table)
                        return Response({"field":desc_table['data'],"sql":create_table_sql['data'], 'index':table_index['data']})
                except Exception as e:
                    CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                    return HttpResponse(status=500)

