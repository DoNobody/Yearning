
from abc import abstractmethod, ABCMeta

import json
import pymysql
import psycopg2
import logging
CUSTOM_ERROR = logging.getLogger('Yearning.core.views')


class DbOpter(metaclass=ABCMeta):
    """
    基础的db操作类
    """
    @abstractmethod
    def get_con(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_dbs(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_tables(self, *args, **kwargs):
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def get_dicts(self, *args, **kwargs):
        pass


    @abstractmethod
    def desc_table(self, *args, ** kwargs):
        pass







class MysqlOpter(DbOpter):
    """
    mysql 的操作实现类
    """
    con = object
    

    def __init__(self, host=None, user=None, password=None, db=None, port=None, **kwargs):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.port = int(port)
        self.conn_kwargs = kwargs

    def __enter__(self):
        self.con = pymysql.connect(
            host=self.host,
            user=self.user,
            passwd=self.password,
            db=self.db,
            charset='utf8mb4',
            port=self.port, 
            **self.conn_kwargs
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def execute(self, sql=None):
        data_dict = []
        id = 0
        with self.con.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            sqllist = sql
            cursor.execute(sqllist)
            result = cursor.fetchall()
            for field in cursor.description:
                if id == 0:
                    head_info = {'title': field[0], "key": field[0]}
                    id += 1
                else:
                    head_info = {'title': field[0], "key": field[0]}
                data_dict.append(head_info)
            len = cursor.rowcount
        return {'data': result, 'title': data_dict, 'len': len}


    def get_con(self):
        return self.con
    
    def get_dbs(self):
        return self.execute('show databases;')

    def get_dicts(self):
        pass

    def get_schemas(self):
        return self.get_dbs()
    
    def get_tables(self, db=None):
        if db:
            self.db = db
        return self.execute('show tables;')

    def desc_table(self, table_name, db=None, **kwargs):
        if db:
            self.db=db
        desc_sql="""
        SELECT a.COLUMN_NAME "COLUMN_NAME", 
            a.COLUMN_TYPE "COLUMN_TYPE", 	
            a.IS_NULLABLE "IS_NULLABLE", 
            a.COLUMN_KEY "COLUMN_KEY",
            a.COLUMN_DEFAULT "COLUMN_DEFAULT",
            b.TABLE_COMMENT "TABLE_COMMENT", 
            CONCAT(a.COLUMN_COMMENT,a.COLUMN_KEY, a.EXTRA) "COLUMN_COMMENT",
            a.CHARACTER_SET_NAME "CHARACTER_SET_NAME",
            a.COLLATION_NAME  "COLLATION_NAME"
        FROM information_schema.COLUMNS a,information_schema.TABLES b
        WHERE a.TABLE_SCHEMA=b.TABLE_SCHEMA 
        AND a.TABLE_NAME=b.TABLE_NAME
        AND a.TABLE_SCHEMA='{}'
        AND a.TABLE_NAME='{}';
        """.format(self.db, table_name)
        return self.execute(desc_sql)

    def get_index(self, table_name, db=None, **kwargs):
        if db:
            self.db=db
        index_sql="""SELECT
                TABLE_NAME,
                NON_UNIQUE,
                INDEX_NAME,
                SEQ_IN_INDEX,
                COLUMN_NAME,
                INDEX_TYPE,
                CONCAT(COMMENT,INDEX_COMMENT)    INDEX_COMMENT
        FROM  INFORMATION_SCHEMA.STATISTICS
        WHERE  TABLE_SCHEMA = '{}'
        AND Table_name = '{}'""".format(self.db, table_name)
        return self.execute(index_sql)

class PostgresOpter(DbOpter):
    """
    postgres 的操作实现类
    """
    
    def __init__(self, host=None, user=None, password=None, db=None, port=None, **kwargs):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.port = int(port)
        self.conn_kwargs = kwargs
    
    def __enter__(self):
        #psycopg2.connect(database="testdb", user="postgres", password="pass123", host="127.0.0.1", port="5432")
        self.con = psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.db,
            port=self.port,
            **self.conn_kwargs
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def get_con(self):
        return self.con

    def execute(self, sql=None):
        data_dict = []
        id = 0
        with self.con.cursor() as cursor:
            sqllist = sql
            cursor.execute(sqllist)
            result = cursor.fetchall()
            for field in cursor.description:
                head_info = {'title': field[0], "key": field[0]}
                data_dict.append(head_info)
            len = cursor.rowcount
        return {'data': result, 'title': data_dict, 'len': len}


    def get_con(self):
        return self.con
    
    def get_dbs(self):
        return self.execute('SELECT * FROM pg_database;')

    def get_dicts(self):
        pass
    
    def get_tables(self, db=None, schema=None):
        if db:
            self.db = db
        return self.execute("select CONCAT(schemaname, '.', tablename) as Tables_in_{} FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';".format(self.db))

    def desc_table(self, table_name, db=None, **kwargs):
        if db:
            self.db = db
        tab_name = table_name
        schemaname='public'
        if "." in table_name:
            tab_name = table_name.split('.')[-1]
            schemaname = table_name.split('.')[0]
        
        desc_sql = """SELECT
            cols.column_name "COLUMN_NAME",
            cols.udt_name "COLUMN_TYPE",
            cols.is_nullable "IS_NULLABLE",
            '' as "COLUMN_KEY", 
            cols.column_default "COLUMN_DEFAULT",
            (select pg_catalog.obj_description(cols.table_name ::regclass)) AS "TABLE_COMMENT",
            (SELECT
                pg_catalog.col_description(c.oid, cols.ordinal_position::int)
                FROM
                pg_catalog.pg_class c
                WHERE
                c.oid = (SELECT ('"' || cols.table_name || '"')::regclass::oid)
                AND c.relname = cols.table_name
            ) AS "COLUMN_COMMENT"
        FROM
            information_schema.columns cols
        WHERE
            cols.table_catalog    = '{}'
            AND cols.table_name   = '{}'
            AND cols.table_schema = '{}';""".format(self.db, tab_name, schemaname)
        return self.execute(desc_sql)


    def get_index(self, table_name, db=None, **kwargs):
        if db:
            self.db = db
        tab_name = table_name
        schemaname='public'
        if "." in table_name:
            tab_name = table_name.split('.')[-1]
            schemaname = table_name.split('.')[0]
        index_sql="""SELECT
            concat(n.nspname,'.',t.relname) as "TABLE_NAME"
            ,c.relname  as "INDEX_NAME"
                ,CASE  
                        WHEN i.indisunique = 't' THEN 1  
                        ELSE 0  
                END AS NON_UNIQUE
                ,am.amname as "INDEX_TYPE"
            ,array_to_string(array_agg(a.attname), ', ') as "COLUMN_NAME"
        FROM pg_catalog.pg_class c
            JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_catalog.pg_index i ON i.indexrelid = c.oid
            JOIN pg_catalog.pg_class t ON i.indrelid   = t.oid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(i.indkey)
                JOIN pg_am am ON am.oid=c.relam
        WHERE c.relkind = 'i'
            and n.nspname = '{}'
                    and t.relname = '{}'
            and pg_catalog.pg_table_is_visible(c.oid)
        GROUP BY
            n.nspname
            ,t.relname
            ,c.relname
            ,i.indisunique
            ,i.indexrelid
                ,am.amname;""".format(schemaname, table_name)
        return self.execute(index_sql)


if __name__ == "__main__":
    m_con = MysqlOpter(host="127.0.0.1", user='root', password='root', db="test", port=3306)
    with m_con as con:
        info = con.get_index('auth_permission')
        print(json.dumps(info))

    p_con = PostgresOpter(host='127.0.0.1', user='postgres', password='example', db='mydb', port=5432)
    with p_con as con:
        info = con.get_index('items')
        print(json.dumps(info,indent=2))