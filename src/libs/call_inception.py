'''

INCEPTION operation

2017-11-23

cookie

'''
from abc import abstractmethod, ABCMeta

from libs import util
import pymysql
import sqlparse
import ast

import psycopg2
import psycopg2.extras

from datetime import datetime

pymysql.install_as_MySQLdb()
import logging
CUSTOM_ERROR = logging.getLogger('Yearning.core.views')


class Inception(metaclass=ABCMeta):
    
    @abstractmethod
    def Execute(self, *args, **kwargs):
        pass

    @abstractmethod
    def Check(self, *args, **kwargs):
        pass

    @staticmethod
    def BeautifySQL(sql):
        return sqlparse.format(sql, reindent=True, keyword_case='upper')
    


class MysqlInception(Inception):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.con = object

    def __enter__(self):
        un_init = util.init_conf()
        inception = ast.literal_eval(un_init['inception'])
        self.con = pymysql.connect(host=inception['host'],
                                   user=inception['user'],
                                   passwd=inception['password'],
                                   port=int(inception['port']),
                                   db='',
                                   charset="utf8",
                                   connect_timeout=5,
                                   read_timeout = 28800,
                                   write_timeout = 28800)
        return self

    def GenerateStatements(self, Sql: str = '', Type: str = '', backup=None):
        if Sql[-1] == ';':
            Sql = Sql.rstrip(';')
        elif Sql[-1] == '；':
            Sql = Sql.rstrip('；')
        if backup is not None:
            InceptionSQL = '''
             /*--user=%s;--password=%s;--host=%s;--port=%s;%s;%s;*/ \
             inception_magic_start;\
             use `%s`;\
             %s; \
             inception_magic_commit;
            ''' % (self.__dict__.get('user'),
                   self.__dict__.get('password'),
                   self.__dict__.get('host'),
                   self.__dict__.get('port'),
                   Type,
                   backup,
                   self.__dict__.get('db'),
                   Sql)
            return InceptionSQL
        else:
            InceptionSQL = '''
                        /*--user=%s;--password=%s;--host=%s;--port=%s;%s;*/ \
                        inception_magic_start;\
                        use `%s`;\
                        %s; \
                        inception_magic_commit;
                       ''' % (self.__dict__.get('user'),
                              self.__dict__.get('password'),
                              self.__dict__.get('host'),
                              self.__dict__.get('port'),
                              Type,
                              self.__dict__.get('db'),
                              Sql)
            return InceptionSQL

    def Execute(self, sql, backup: int):
        if backup == '0' or backup == 0:
            Inceptionsql = self.GenerateStatements(Sql=sql, Type='--execute=1')
        else:
            Inceptionsql = self.GenerateStatements(
                Sql=sql,
                Type='--execute=1',
                backup='--backup=1')
        with self.con.cursor() as cursor:
            cursor.execute(Inceptionsql)
            result = cursor.fetchall()
            Dataset = [
                {
                    'ID': row[0],
                    'stage': row[1],
                    'errlevel': row[2],
                    'stagestatus': row[3],
                    'errormessage': row[4],
                    'sql': row[5],
                    'affected_rows': row[6],
                    'sequence': row[7],
                    'backup_dbname': row[8],
                    'execute_time': row[9],
                    'SQLSHA1': row[10]
                }
                for row in result
            ]
        return Dataset

    def Check(self, sql=None):
        Inceptionsql = self.GenerateStatements(Sql=sql, Type='--check=1')
        with self.con.cursor() as cursor:
            cursor.execute(Inceptionsql)
            result = cursor.fetchall()
            Dataset = [
                {
                    'ID': row[0],
                    'stage': row[1],
                    'errlevel': row[2],
                    'stagestatus': row[3],
                    'errormessage': row[4],
                    'sql': row[5],
                    'affected_rows': row[6],
                    'SQLSHA1': row[10]
                }
                for row in result
            ]
        return Dataset

    def oscstep(self, sql=None):
        with self.con.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
        return result

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def __str__(self):
        return '''

        InceptionSQL Class

        '''

class PostgreIncetion(Inception):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.con = None
    
    def __enter__(self):
        if self.db is None:
            self.db = "postgres"
        self.con = psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.db,
            port=self.port,
            connect_timeout=5,
            )
        return self

    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.con:
            self.con.close()
    
    def __str__(self):
        return '''
        Postgres InceptionSQL Class
        '''
    
    def Check(self, sql=None):
        return [
                {
                    'ID': 1,
                    'stage': 'UNCHECKED',
                    'errlevel': 0,
                    'stagestatus': 'SQL 正确性由Leader/DBA进行人工审核',
                    'errormessage': 'Postgres 不提供自动的SQL语法检查',
                    'sql': sql,
                    'affected_rows': 'UNKNOWN',
                    'SQLSHA1': 'NULL'
                }
            ]
    
    def Execute(self, sql=None, *args, **kwargs):
        self.cursor = self.con.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        with self.cursor as cursor:
            result = []
            try:
                sqllist =[ item for item in sql.split(';') if not item.strip().startswith('--')]
                for idx, sql in enumerate(sqllist):
                    tmp_result = {
                        'ID': idx,
                        'stage': '',
                        'errlevel': 0,
                        'stagestatus': "Execute Successfully",
                        'errormessage': "",
                        'sql': sql,
                        'affected_rows': 0,
                        'sequence': "",
                        'backup_dbname': "",
                        'execute_time': str(datetime.now()),
                        'SQLSHA1': ""
                    }
                    try:
                        cursor.execute(sql)
                        tmp_result['stage'] = cursor.statusmessage
                        tmp_result['affected_rows'] = cursor.rowcount
                        tmp_result['sql'] = cursor.query
                        result.append(tmp_result)
                    except psycopg2.Error as e:
                        [ item.update({'stagestatus':'Execute RollBack'}) for item in result]
                        tmp_result.update({'errlevel': 2, 'stagestatus': "Execute Error", 'errormessage': str(e)})
                        result.append(tmp_result)
                        cursor.close()
                        self.con.rollback()
                        return result
                self.con.commit()
                return result
            except Exception as e:
                self.con.rollback()
                raise e
    
    def GenerateStatements(self, *args, **kwargs):
        return super().GenerateStatements(*args, **kwargs)