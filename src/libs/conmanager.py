
from abc import abstractmethod, ABCMeta

import json
import pymysql
import psycopg2
import psycopg2.extras
import logging
import subprocess

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
    def search(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def get_dicts(self, *args, **kwargs):
        pass


    @abstractmethod
    def desc_table(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_create_table_sql(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_index(self, *args, **kwargs):
        pass



class MysqlOpter(DbOpter):
    """
    mysql 的操作实现类
    """
    con = object
    

    def __init__(self, host=None, user=None, password=None, db=None, port=None, dictCursor=False, **kwargs):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.port = int(port)
        self.conn_kwargs = kwargs
        self.dictCursor=dictCursor

    def __enter__(self):
        self.con = pymysql.connect(
            host=self.host,
            user=self.user,
            passwd=self.password,
            db=self.db,
            charset='utf8mb4',
            port=self.port,
            connect_timeout=5,
            read_timeout = 55,
            write_timeout = 55,
            **self.conn_kwargs
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.con:
            self.con.close()

    def search(self, sql=None):
        data_dict = []
        id = 0
        if self.dictCursor:
            self.cursor = self.con.cursor(cursor=pymysql.cursors.DictCursor)
        else:
            self.cursor = self.con.cursor()
        with self.cursor as cursor:
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
        return self.search('show databases;')

    def get_dicts(self):
        pass
    
    def get_tables(self, datanames=[]):
        sql = """SELECT table_schema, table_name, group_concat(column_name) cols FROM information_schema.columns group by table_schema,table_name"""
        if datanames:
            sql = """SELECT table_schema, table_name, group_concat(column_name) cols FROM information_schema.columns where table_schema in ('{}') group by table_schema,table_name""".format("','".join(datanames))
        return self.search(sql)

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
        return self.search(desc_sql)

    def get_index(self, table_name, **kwargs):
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
        return self.search(index_sql)

    def get_create_table_sql(self, table_name):
        create_table_sql = 'show create table `%s`.`%s`;' % (self.db, table_name)
        ret = self.search(create_table_sql)
        if self.dictCursor:
            for inf in ret['data']:
                keys = [item for item in inf.keys() if item.startswith("Create")]
                if keys:
                    inf["Create Sql"] = inf[keys[0]]
                    del inf[keys[0]]
                for old_k in ret['title']:
                    if old_k['title'] == keys[0]:
                        old_k['title'] = "Create Sql"
                        old_k['key'] = "Create Sql"
        else:
            for inf in ret['title']:
                if inf['key'].startswith("Create"):
                    inf['key'] = "Create Sql"
                    inf['title'] = "Create Sql"
        return ret


class PostgresOpter(DbOpter):
    """
    postgres 的操作实现类
    """
    
    def __init__(self, host=None, user=None, password=None, db=None, port=None, dictCursor=False, **kwargs):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.port = int(port)
        self.conn_kwargs = kwargs
        self.dictCursor = dictCursor
    
    def __enter__(self):
        #psycopg2.connect(database="testdb", user="postgres", password="pass123", host="127.0.0.1", port="5432")
        if self.db is None:
            self.db = "postgres"
        self.con = psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.db,
            port=self.port,
            connect_timeout=5,
            **self.conn_kwargs
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.con:
            self.con.close()

    def get_con(self):
        return self.con

    def search(self, sql=None):
        data_dict = []
        if self.dictCursor:
            self.cursor = self.con.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        else:
            self.cursor = self.con.cursor()
        with self.cursor as cursor:
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
        return self.search("""SELECT datname as "Database" FROM pg_database where datname not like 'template%';""")


    def get_dicts(self):
        pass
    

    def get_tables(self, datanames=[]):
        sql = """select table_schema, table_name, array_to_string(array_agg(column_name), ',') cols
                from 
                (SELECT table_catalog as table_schema,CONCAT(table_schema, '.', table_name) as table_name, column_name
                FROM information_schema.columns 
                where table_schema not in ('pg_catalog','information_schema') ) tmp
                group by table_schema,table_name"""
        if datanames:
            sql = """select table_schema, table_name, array_to_string(array_agg(column_name), ',') cols
                from 
                (SELECT table_catalog as table_schema,CONCAT(table_schema, '.', table_name) as table_name, column_name
                FROM information_schema.columns 
                where table_schema not in ('pg_catalog','information_schema') and table_schema in ('{}')) tmp
                group by table_schema,table_name""".format("','".join(datanames))
        return self.search(sql)


    def desc_table(self, table_name, **kwargs):
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
        return self.search(desc_sql)


    def get_index(self, table_name,**kwargs):
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
                    ,am.amname;""".format(schemaname, tab_name)
        return self.search(index_sql)


    def get_create_table_sql(self, table_name):
        tab_name = table_name
        schemaname='public'
        if "." in table_name:
            tab_name = table_name.split('.')[-1]
            schemaname = table_name.split('.')[0]
        dumps_shell = """export PGPASSWORD={password};pg_dump -h {host} -U {user} -p {port} --schema-only -t "{schema}.{table}" {db}|grep -vE "^--|^$"
        """.format(password=self.password, host=self.host, user= self.user, port=self.port, schema=schemaname, table=tab_name, db=self.db)
        result_info = "Some Error"
        call_shell_ret = subprocess.Popen(dumps_shell, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output, errors = call_shell_ret.communicate()
        if call_shell_ret.returncode == 0:
            result_info = output
        else:
            result_info = errors
        return {"data":[{"Table": table_name, "Create Sql": result_info}], "title": [{"title": "Table", "key": "Table"}, {"title": "Create Table", "key": "Create Table"}], "len": 1}


if __name__ == "__main__":
    # m_con = MysqlOpter(host="127.0.0.1", user='root', password='root', db="test", port=3306, dictCursor=False)
    # with m_con as con:
    #     info = con.get_create_table_sql('auth_permission')
    #     print(json.dumps(info))

    p_con = PostgresOpter(host='127.0.0.1', user='postgres', password='example', db='mydb', port=5432, dictCursor=True)
    with p_con as con:
        # info = con.search('ALTER TABLE public.items DROP COLUMN sdfsd')
        # info = con.search("ALTER TABLE public.test1 ADD COLUMN test char(11) DEFAULT 'cc';")
        print(json.dumps(info,indent=2, ensure_ascii=False))