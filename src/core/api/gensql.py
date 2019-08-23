import json
import logging
from django.http import HttpResponse
from rest_framework.response import Response
from libs import gen_ddl, baseview

from core.models import DatabaseList
CUSTOM_ERROR = logging.getLogger('Yearning.core.views')


class gen_sql(baseview.BaseView):
    '''

    :argument 调用gen_ddl库 生成DDL语句 生成索引语句。并将生成的sql返回

    :param

    :return 生成的sql语句

    '''

    def put(self, request, args=None):

        try:
            data = json.loads(request.data['data'])
            base = request.data['basename']
            # default mysql
            dbtype = 'mysql'
            connection_name = request.data['connection_name']
            _connection = DatabaseList.objects.filter(connection_name=connection_name).first()
            if _connection:
                dbtype = _connection.dbtype
        except KeyError as e:
            CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
        
        if args == "sql":
            gen_sql = []
            try:
                for i in data:
                    if 'edit' in i.keys():
                        info = gen_ddl.alter_table(select_name='edit',
                                                    column_name=i['edit']['COLUMN_NAME'],
                                                    column_type=i['edit']['COLUMN_TYPE'],
                                                    default=i['edit']['COLUMN_DEFAULT'],
                                                    comment=i['edit']['COLUMN_COMMENT'],
                                                    null=i['edit']['IS_NULLABLE'],
                                                    table_name=i['table_name'],
                                                    base_name=base,
                                                    dbtype= dbtype)
                        gen_sql.append(info)

                    elif 'del' in i.keys():
                        info = gen_ddl.alter_table(select_name='del',
                                                    column_name=i['del']['COLUMN_NAME'],
                                                    table_name=i['table_name'],
                                                    base_name=base,
                                                    dbtype=dbtype)
                        gen_sql.append(info)
                    elif 'add' in i.keys() and i['add'] != []:
                        for n in i['add']:
                            info = gen_ddl.alter_table(select_name='add',
                                                        column_name=n['COLUMN_NAME'],
                                                        base_name=base,
                                                        column_type=n['COLUMN_TYPE'],
                                                        default=n['COLUMN_DEFAULT'],
                                                        comment=n['COLUMN_COMMENT'],
                                                        null=n['IS_NULLABLE'],
                                                        table_name=i['table_name'],
                                                        dbtype=dbtype)

                            gen_sql.append(info)
                return Response(gen_sql)
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                return HttpResponse(status=500)

        elif args == "index":
            gen_sql = []
            try:
                for i in data:
                    if 'delindex' in i.keys():
                        info = gen_ddl.alter_index(select_name='delindex',
                                                key_name=i['delindex']['INDEX_NAME'],
                                                table_name=i['table_name'],
                                                dbtype= dbtype)
                        gen_sql.append(info)
                    elif 'addindex' in i.keys() and i['addindex'] != []:
                        for n in i['addindex']:
                            if n['FULLTEXT'] == "YES":
                                info = gen_ddl.alter_index(table_name=i['table_name'],
                                                        column_name=n['COLUMN_NAME'],
                                                        key_name=n['INDEX_NAME'],
                                                        fulltext=n['FULLTEXT'],
                                                        select_name='addindex',
                                                        dbtype= dbtype)
                                gen_sql.append(info)
                            elif n['NON_UNIQUE'] == "YES":
                                info = gen_ddl.alter_index(select_name='addindex',
                                                        key_name=n['INDEX_NAME'],
                                                        non_unique='unique',
                                                        column_name=n['COLUMN_NAME'],
                                                        table_name=i['table_name'],
                                                        dbtype= dbtype)
                                gen_sql.append(info)
                            else:
                                info = gen_ddl.alter_index(select_name='addindex',
                                                        key_name=n['INDEX_NAME'],
                                                        column_name=n['COLUMN_NAME'],
                                                        table_name=i['table_name'],
                                                        dbtype= dbtype)
                                gen_sql.append(info)
                return Response(gen_sql)
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                return HttpResponse(status=500)
