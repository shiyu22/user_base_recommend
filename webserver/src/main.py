import os
import logging
from service.insert import do_insert
from service.search import do_search
from service.count import do_count
from service.delete import do_delete_table
from indexer.index import milvus_client
from indexer.tools import connect_mysql
import time
from fastapi import FastAPI

app = FastAPI()

def init_conn():
    conn = connect_mysql()
    cursor = conn.cursor()
    index_client = milvus_client()
    return index_client, conn, cursor


@app.get('/countTable')
async def do_count_images_api(table_name: str=None):
    try:
        index_client, conn, cursor = init_conn()
        rows_milvus, rows_mysql = do_count(index_client, conn, cursor, table_name)
        return "{0},{1}".format(rows_milvus, rows_mysql), 200
    except Exception as e:
        logging.ERROR(e)
        return "Error with {}".format(e), 400


@app.delete('/deleteTable')
async def do_delete_table_api(table_name: str=None):
    try:
        index_client, conn, cursor = init_conn()
        table_name = args['Table']
        status = do_delete_table(index_client, conn, cursor, table_name)
        return "{}".format(status)
    except Exception as e:
        logging.ERROR(e)
        return "Error with {}".format(e), 400


@app.post('/getSimilarUser')
def do_search_images_api(id: int, table_name: str=None):
    try:
        index_client, conn, cursor = init_conn()
        results = do_search(index_client, conn, cursor, search_id)

        return "{0}".format(results), 200

    except Exception as e:
        logging.ERROR(e)
        return "Error with {}".format(e), 400


if __name__ == '__main__':
    uvicorn.run(app=app, host='127.0.0.1', port=8000)