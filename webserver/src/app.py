import os
import logging
from service.insert import do_insert
from service.search import do_search
from service.count import do_count
from service.delete import do_delete_images, do_delete_table
from flask_cors import CORS
from flask import Flask, request, send_file, jsonify
from flask_restful import reqparse
from werkzeug.utils import secure_filename
from encoder.encode import Img2Vec
from indexer.index import milvus_client
from indexer.tools import connect_mysql
from indexer.logs import write_log
import time


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

img_to_vec = Img2Vec()
# img_to_vec = Img2Vec(model_path="./src/model/vgg_triplet.pth")


def init_conn():
    conn = connect_mysql()
    cursor = conn.cursor()
    index_client = milvus_client()
    return index_client, conn, cursor


@app.route('/addImages', methods=['POST'])
def do_insert_images_api():
    time1 = time.time()
    args = reqparse.RequestParser(). \
        add_argument('Id', type=str). \
        add_argument('File', type=str). \
        add_argument('Size', type=int). \
        add_argument('Table', type=str). \
        parse_args()
    ids = args['Id']
    file = args['File']
    size = args['Size']
    table_name = args['Table']
    file_id = request.files.get('FileId', "")
    if file_id:
        ids = str(file_id.read().decode("utf-8")).strip().split(",")
        ids = ids[:-1]
    else:
        ids = args['Id'].split(",")

    time2 = time.time()
    print("-------insert params time-------", time2-time1)
    try:
        index_client, conn, cursor = init_conn()
        status, info = do_insert(index_client, conn, cursor, img_to_vec, ids, file, size, table_name)
        time3 = time.time()
        print("-------do insert time-------", time3-time2)
        print("-------insert total time-------", time3-time1)
        return "{0},{1}".format(status, info)
    except Exception as e:
        write_log(e, 1)
        return "Error with {}".format(e), 400


@app.route('/deleteImages', methods=['POST'])
def do_delete_images_api():
    args = reqparse.RequestParser(). \
        add_argument('Table', type=str). \
        add_argument('Id', type=str). \
        parse_args()

    table_name = args['Table']
    file_id = request.files.get('FileId', "")

    if file_id:
        ids = str(file_id.read().decode("utf-8")).strip().split(",")
        ids = ids[:-1]
    else:
        ids = args['Id'].split(",")

    try:
        index_client, conn, cursor = init_conn()
        status, info = do_delete_images(index_client, conn, cursor, ids, table_name)
        return "{0},{1}".format(status, info), 200
    except Exception as e:
        write_log(e, 1)
        return "Error with {}".format(e), 400


@app.route('/countImages', methods=['POST'])
def do_count_images_api():
    args = reqparse.RequestParser(). \
        add_argument('Table', type=str). \
        parse_args()
    table_name = args['Table']
    try:
        index_client, conn, cursor = init_conn()
        rows_milvus, rows_mysql = do_count(index_client, conn, cursor, table_name)
        return "{0},{1}".format(rows_milvus, rows_mysql), 200
    except Exception as e:
        write_log(e, 1)
        return "Error with {}".format(e), 400


@app.route('/deleteTable', methods=['POST'])
def do_delete_table_api():
    args = reqparse.RequestParser(). \
        add_argument('Table', type=str). \
        parse_args()
    try:
        index_client, conn, cursor = init_conn()
        table_name = args['Table']
        status = do_delete_table(index_client, conn, cursor, table_name)
        return "{}".format(status)
    except Exception as e:
        write_log(e, 1)
        return "Error with {}".format(e), 400


@app.route('/getSimilarImages', methods=['POST'])
def do_search_images_api():
    time1 = time.time()
    args = reqparse.RequestParser(). \
        add_argument('Id', type=str). \
        add_argument('Table', type=str). \
        parse_args()

    file_id = request.files.get('FileId', "")
    table_name = args['Table']
    file = request.files.get('File', "")
    if file_id:
        ids = str(file_id.read().decode("utf-8")).strip().split(",")
        ids = ids[:-1]
    else:
        ids = args['Id'].split(",")

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('/tmp/search_pic', filename)
        file.save(file_path)

    time2 = time.time()
    print("-------search params time-------", time2-time1)
    try:
        index_client, conn, cursor = init_conn()
        result = do_search(index_client, conn, cursor, img_to_vec, [file_path], ids, table_name)
        time3 = time.time()
        print("-------do search time-------", time3-time2)
        print("-------search total time-------", time3-time1)

        return "{0},{1}".format(ids, result), 200

    except Exception as e:
        write_log(e, 1)
        return "Error with {}".format(e), 400


if __name__ == "__main__":
    app.run(threaded=True, host="0.0.0.0", port=5000)
