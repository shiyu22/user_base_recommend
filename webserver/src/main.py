import os
import logging
from service.search import do_search
from service.count import do_count
from service.delete import do_delete_table
from indexer.index import milvus_client
from indexer.tools import connect_mysql
from common.config import OUT_PATH
import time
from fastapi import FastAPI
import uvicorn
from starlette.responses import FileResponse
from starlette.requests import Request

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


@app.get('/getImage/<img>')
def image_endpoint(img: str):
    try:
        img_path = OUT_PATH + '/' + img + '.jpg'
        return FileResponse(img_path), 200
    except Exception as e:
        logging.error(e)
        return None, 200


@app.post('/getSimilarUser')
def do_search_images_api(request:Request, search_id: list, table_name: str=None):
    try:
        index_client, conn, cursor = init_conn()
        host = request.headers['host']
        results = do_search(index_client, conn, cursor, host, search_id, table_name)
        return results, 200

    except Exception as e:
        logging.error(e)
        return "Error with {}".format(e), 400


if __name__ == '__main__':
    uvicorn.run(app=app, host='192.168.1.85', port=8000)