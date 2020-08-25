import logging as log
from common.config import MILVUS_TABLE, OUT_PATH, OUT_DATA
from indexer.index import milvus_client, search_vectors, get_vector_by_ids
from indexer.tools import connect_mysql, search_by_milvus_id
import numpy as np
import torch
import pickle
import dgl
import json
import random


def get_list_info(conn, cursor, table_name, host, list_ids):
    if not table_name:
        table_name = MILVUS_TABLE
    list_info = {}
    list_img = []
    for ids in list_ids:
        ids = ids[:-4]
        info, img = get_ids_info(conn, cursor, table_name, host, ids)
        try:
            info = json.loads(info.replace("\\", ""))
        except:
            info = json.loads(info.replace("\\\"", "").replace("\\", ""))

        title = info["Title"]
        year = info["Year"]
        list_info[ids] = [title, year, img]
    return list_info


def get_ids_info(conn, cursor, table_name, host, ids):
    if not table_name:
        table_name = MILVUS_TABLE
    info = search_by_milvus_id(conn, cursor, table_name, ids)
    # print("===========", info)
    img = "http://"+ str(host) + "/getImage?img=" + str(ids)
    print("============", img)
    return info[1], img


def do_search(index_client, conn, cursor, img_list, search_id, table_name):
    if not table_name:
        table_name = MILVUS_TABLE

    _, vector_item = get_vector_by_ids(index_client, table_name, search_id)
    status, results = search_vectors(index_client, table_name, vector_item)
    print("-----milvus search status------", status)

    results_ids = []
    for results_id in results.id_array:
        for i in results_id:
            img = i +'.jpg'
            if img in img_list:
                results_ids.append(i)
    try:
        list_ids = random.sample(results_ids, 100)
    except:
        list_ids = results_ids
    return list_ids
