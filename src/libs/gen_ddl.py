
def mysql_alter_table(select_name=None, base_name=None, column_name=None, column_type=None,
               table_name=None, default=None, comment=None, null=None, dbtype='mysql', **kwargs) -> str:
    if default:
        if default.isdigit():
            pass
        else:
            default = f''' \'{default}\''''
    if select_name == "add":
        if default is None:
            if null == 'YES':
                if comment is None:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` " +\
                           f"ADD COLUMN `{column_name}` {column_type}"
                else:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` ADD COLUMN `{column_name}` " +\
                           f"{column_type} COMMENT '{comment}'"
            else:
                if comment is None:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` ADD COLUMN `{column_name}` " +\
                           f"{column_type} NOT NULL"
                else:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` ADD COLUMN `{column_name}` " +\
                           f"{column_type} NOT NULL COMMENT '{comment}'"
        else:
            if null == 'NO':
                if comment is None:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` ADD COLUMN `{column_name}` " +\
                           f"{column_type} NOT NULL DEFAULT {default}"
                else:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` ADD COLUMN `{column_name}` " +\
                           f"{column_type} NOT NULL DEFAULT {default} COMMENT '{comment}'"
            else:
                if comment is None:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` ADD COLUMN  `{column_name}` " +\
                           f"{column_type}  DEFAULT {default}"
                else:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` ADD COLUMN `{column_name}` " +\
                           f"{column_type}  DEFAULT {default} COMMENT '{comment}'"
    if select_name == 'edit':
        if default is None:
            if null == 'YES':
                if comment is None:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` " +\
                           f"CHANGE COLUMN `{column_name}` `{column_name}` {column_type}"
                else:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` " +\
                           f"CHANGE COLUMN `{column_name}` `{column_name}` " +\
                           f"{column_type} COMMENT '{comment}'"
            else:
                if comment == '':
                    return f"ALTER TABLE `{base_name}`.`{table_name}` " +\
                           f"CHANGE COLUMN `{column_name}` `{column_name}` {column_type} NOT NULL"
                else:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` " +\
                           f"CHANGE COLUMN `{column_name}` `{column_name}` " +\
                           f"{column_type} NOT NULL COMMENT '{comment}'"
        else:
            if null == 'NO':
                if comment is None:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` " +\
                           f"CHANGE COLUMN `{column_name}` `{column_name}` " +\
                           f"{column_type} NOT NULL DEFAULT {default}"
                else:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` " +\
                           f"CHANGE COLUMN `{column_name}` `{column_name}` " +\
                           f"{column_type} NOT NULL DEFAULT {default} COMMENT '{comment}'"
            else:
                if comment is None:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` " +\
                           f"CHANGE COLUMN `{column_name}` `{column_name}` " +\
                           f"{column_type} DEFAULT {default}"
                else:
                    return f"ALTER TABLE `{base_name}`.`{table_name}` " +\
                           f"CHANGE COLUMN `{column_name}` `{column_name}` " +\
                           f"{column_type} DEFAULT {default} COMMENT '{comment}'"

    if select_name == 'del':
        return f"ALTER TABLE `{base_name}`.`{table_name}` DROP COLUMN {column_name}"


def mysql_alter_index(key_name=None, table_name=None, non_unique=None,
          column_name=None, select_name=None, fulltext=None, dbtype='mysql'):
    if select_name == 'addindex':
        if fulltext == 'YES':
            return f'''ALTER TABLE `{table_name}` ADD FULLTEXT {key_name} ({column_name}) '''
        else:
            if non_unique is not None:
                return f'''ALTER TABLE `{table_name}` ADD \
                            UNIQUE {key_name}(`{column_name}`)'''
            else:
                return f'''ALTER TABLE `{table_name}` ADD INDEX {key_name}(`{column_name}`)'''
    if select_name == "delindex":
        return f'''ALTER TABLE `{table_name}` DROP INDEX {key_name}'''


def postgres_alter_table(select_name=None, base_name=None, column_name=None, column_type=None,
               table_name=None, default=None, comment=None, null=None, dbtype='mysql', **kwargs) -> str:
    sql = "-- Postgres 本平台不提供语句自动生成,以下仅供参考;"
    if default:
        if default.isdigit():
            pass
        else:
            default = f''' \'{default}\''''
    if select_name == "add":
        if default is None:
            if null == 'YES':
                sql = f"ALTER TABLE {table_name} " +\
                           f"ADD COLUMN {column_name} {column_type}"
            else:
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} " +\
                           f"{column_type} NOT NULL"
        else:
            if null == 'NO':
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} " +\
                      f"{column_type} NOT NULL DEFAULT {default}"
            else:
                sql = f"ALTER TABLE {table_name} ADD COLUMN  {column_name} " +\
                      f"{column_type}  DEFAULT {default}"
        if comment:
            sql += f";COMMENT ON COLUMN {table_name}.{column_name} IS '{comment}'"
        return sql

    if select_name == 'edit':
        sql = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {column_type}"
        if default is None:
            sql +=";ALTER TABLE {table_name} ALTER COLUMN {column_name} DROP DEFAULT"
        else:
            sql += f";ALTER TABLE {table_name} ALTER COLUMN {column_name} SET DEFAULT {default}"
        if null == "NO":
            sql += f";ALTER TABLE {table_name} ALTER COLUMN {column_name} SET NOT NULL"
        else:
            sql += f";ALTER TABLE {table_name} ALTER COLUMN {column_name} DROP NOT NULL"
        if comment:
            sql += f";COMMENT ON COLUMN {table_name}.{column_name} IS '{comment}'"
        return sql

    if select_name == 'del':
        sql += f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
        return sql


def postgres_alter_index(key_name=None, table_name=None, non_unique=None,
          column_name=None, select_name=None, fulltext=None, dbtype=None, **kwargs):
    sql = "-- Postgres 本平台不提供语句自动生成,以下仅供参考;"
    if select_name == 'addindex':
        if non_unique is not None:
            sql += f"CREATE UNIQUE INDEX {key_name} ON {table_name} {column_name}"
        else:
            sql += f"CREATE INDEX {key_name} ON {table_name} {column_name}"
    if select_name == "delindex":
        sql += f'''DROP INDEX {key_name}'''
    return sql

def alter_table(**kwargs):
    dbtype = kwargs.get("dbtype", 'mysql')
    if dbtype == 'mysql':
        return mysql_alter_table(**kwargs)
    elif dbtype == 'postgres':
        return postgres_alter_table(**kwargs)
    else:
        return "dbtype error：数据库类型不支持自动生成语句。"

def alter_index(**kwargs):
    dbtype = kwargs.get("dbtype", 'mysql')
    if dbtype == 'mysql':
        return mysql_alter_index(**kwargs)
    elif dbtype == 'postgres':
        return postgres_alter_index(**kwargs)
    else:
        return "dbtype error：数据库类型不支持自动生成语句。"
