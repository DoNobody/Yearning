'''
serializers 
'''
from rest_framework import serializers
from core.models import DatabaseList
from core.models import SqlDictionary
from core.models import SqlRecord
from core.models import Account
from core.models import SqlOrder, query_order, querypermissions, globalpermissions, grained


class Globalpermissions(serializers.HyperlinkedModelSerializer):
    '''
    站内信列表serializers
    '''

    class Meta:
        model = globalpermissions
        fields = ('inception', 'ldap', 'other', 'message')


class UserINFO(serializers.HyperlinkedModelSerializer):
    '''
    平台用户信息列表serializers
    '''

    class Meta:
        model = Account
        fields = ('id', 'username', 'group', 'department', 'email', 'auth_group', 'real_name')


class SQLGeneratDic(serializers.HyperlinkedModelSerializer):
    '''
    数据库字典信息serializers
    '''

    class Meta:
        model = SqlDictionary
        fields = (
            'BaseName', 'TableName', 'Field', 'Type', 'Extra', 'TableComment'
        )


class DBlist(serializers.HyperlinkedModelSerializer):
    '''
    数据库连接信息serializers
    '''

    class Meta:
        model = DatabaseList
        fields = ('id', 'connection_name', 'ip', 'computer_room', 'port', 'username', 'dbtype', 'has_super_perm', 'has_repl_perm')


class query_con(serializers.HyperlinkedModelSerializer):
    '''
    查询连接信息serializers
    '''

    class Meta:
        model = DatabaseList
        fields = ('connection_name', 'computer_room')


class Area(serializers.HyperlinkedModelSerializer):
    '''
    SQL提交及表结构修改页面数据库连接信息返回serializers
    '''

    class Meta:
        model = DatabaseList
        fields = ('id', 'connection_name', 'ip', 'computer_room')


class Record(serializers.HyperlinkedModelSerializer):
    '''
    执行工单的详细信息serializers
    '''

    class Meta:
        model = SqlRecord
        fields = ('sql', 'state', 'error', 'affectrow', 'sequence', 'execute_time', 'updatetime')


class Getdingding(serializers.HyperlinkedModelSerializer):
    '''
    dingding webhook serializers
    '''

    class Meta:
        model = DatabaseList
        fields = ('id', 'before', 'after')


class SqlOrderSerializer(serializers.ModelSerializer):
    '''

    执行记录 返回

    '''

    class Meta:
        model = SqlOrder
        fields = '__all__'


class Query_review(serializers.HyperlinkedModelSerializer):
    '''

    查询审计

    '''

    class Meta:
        model = query_order
        fields = (
            'work_id', 'username', 'date', 'instructions', 'query_per', 'connection_name', 'computer_room',
            'export', 'time', 'real_name')


class Query_list(serializers.HyperlinkedModelSerializer):
    '''

    查询审计

    '''

    class Meta:
        model = querypermissions
        fields = ('id', 'statements', 'updatetime')


class AuthGroup_Serializers(serializers.HyperlinkedModelSerializer):
    """
    序列化权限组
    """

    class Meta:
        model = grained
        fields = ('id', 'username', 'permissions',)
