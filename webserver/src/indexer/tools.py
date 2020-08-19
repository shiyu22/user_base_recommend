import logging
from common.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD, MYSQL_DB
import pymysql


def connect_mysql():
    try:
        # conn = pymysql.connect(host="127.0.0.1",user="root",port=3306,password="123456",database="mysql", local_infile=True)
        conn = pymysql.connect(host=MYSQL_HOST,user=MYSQL_USER,port=MYSQL_PORT,password=MYSQL_PWD,database=MYSQL_DB, local_infile=True)
        return conn
    except Exception as e:
        print("MYSQL ERROR: connect failed")
        logging.error(e)


def create_tables_mysql(conn,cursor, ids_table, movies_table):
    ids_sql = "create table if not exists " + ids_table + "(milvus_id int, movies_id int);"
    movies_sql = "create table if not exists " + movies_table + "(movies_id int, movies_title varchar(100), genre varchar(100));"
    sqls = [ids_sql, movies_sql]
    try:
        print("----sqls:", sqls)
        for sql in sqls:
            cursor.execute(sql)
            conn.commit()
            print("------sql:", sql)
    except Exception as e:
        print("MYSQL ERROR:", sqls)
        logging.error(e)


def load_ids_to_mysql(conn, cursor, table_name, file_name):
    sql = "load data local infile '" + file_name + "' into table " + table_name + " fields terminated by ',';"
    try:
        cursor.execute(sql)
        conn.commit()
        print("MYSQL load ids table.")
    except Exception as e:
        print("MYSQL ERROR:", sql)
        logging.error(e)


def load_movies_to_mysql(conn, cursor, table_name, file_name):
    sql = "load data local infile '" + file_name + "' into table " + table_name + " fields terminated by '::';"
    try:
        cursor.execute(sql)
        conn.commit()
        print("MYSQL load movies table.")
    except Exception as e:
        print("MYSQL ERROR:", sql)
        logging.ERROR(e)


def join_movies_ids_mysql(conn, cursor, milvus_table, ids_table, movies_table):
    sql = "create table " + milvus_table + "(select " + ids_table + ".milvus_id as milvus_id, " + movies_table + ".* from " + ids_table + "," + movies_table +" where " + ids_table + ".movies_id=" + movies_table + ".movies_id);"
    print("---join", sql)
    try:
        cursor.execute(sql)
        conn.commit()
        print("MYSQL join table.")
    except Exception as e:
        print("MYSQL ERROR:", sql)
        logging.ERROR(e)


def search_by_milvus_ids(conn, cursor, movies_table, ids):
    str_ids = str(ids)
    str_ids = str(str_ids).replace('[','').replace(']','')
    sql = "select * from " + movies_table + " where milvus_id in (" + str_ids + ") order by field (milvus_id," + str_ids + ");"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        # results = [res[0] for res in results]
        print("MYSQL search by milvus id.")
        return results
    except Exception as e:
        print("MYSQL ERROR:", sql)
        logging.error(e)


def delete_data(conn, cursor, image_id, table_name):
    str_ids = [str(_id) for _id in image_id]
    str_ids = str(str_ids).replace('[','').replace(']','')
    sql = "delete from " + table_name + " where images_id in (" + str_ids + ");"
    try:
        cursor.execute(sql)
        conn.commit()
        print("MYSQL delete data.")
    except Exception as e:
        print("MYSQL ERROR:", sql)
        logging.error(e)


def delete_table(conn, cursor, table_name):
    sql = "drop table if exists " + table_name + ";"
    try:
        cursor.execute(sql)
        print("MYSQL delete table.")
    except:
        print("MYSQL ERROR:", sql)
        logging.error(e)


def count_table(conn, cursor, table_name):
    sql = "select count(milvus_id) from " + table_name + ";"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        print("MYSQL count table.")
        return results[0][0]
    except Exception as e:
        print("MYSQL ERROR:", sql)
        logging.error(e)