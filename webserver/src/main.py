import os
import logging
from service.search import do_search
from service.count import do_count
from service.delete import do_delete_table
from indexer.index import milvus_client
from indexer.tools import connect_mysql
import time
from fastapi import FastAPI
import uvicorn

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
        logging.error(e)
        return "Error with {}".format(e), 400


@app.delete('/deleteTable')
async def do_delete_table_api(table_name: str=None):
    try:
        index_client, conn, cursor = init_conn()
        table_name = args['Table']
        status = do_delete_table(index_client, conn, cursor, table_name)
        return "{}".format(status)
    except Exception as e:
        logging.error(e)
        return "Error with {}".format(e), 400


@app.post('/getSimilarUser')
def do_search_images_api(search_id: int, table_name: str=None):
    try:
        index_client, conn, cursor = init_conn()
        results = do_search(index_client, conn, cursor, search_id, table_name)
        recommends = []
        for re in results:
            recommend = {
                "num" : re[0],
                "movie_id" : re[1],
                "title" : re[2],
                "genre" : re[3]
            }
            recommends.append(recommend)
        return recommends, 200

    except Exception as e:
        logging.error(e)
        return "Error with {}".format(e), 400


if __name__ == '__main__':
    uvicorn.run(app=app, host='192.168.1.85', port=8000)