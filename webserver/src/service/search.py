import logging as log
from common.config import MILVUS_TABLE, IDS_TABLE, MOVIES_TABLE, OUT_PATH, OUT_DATA
from indexer.index import milvus_client, search_vectors, get_vector_by_ids
from indexer.tools import connect_mysql, search_by_milvus_ids
import numpy as np
import torch
import pickle
import dgl


def get_posters_by_ids(host, ids):
    imgs = []
    for i in ids:
        img = "http://"+ str(host) + "/getImage?img=" + str(i)
        imgs.append(img)
    return imgs


def do_search(index_client, conn, cursor, host, search_id, table_name):
    if not table_name:
        table_name = MILVUS_TABLE

    _, vector_item = get_vector_by_ids(index_client, table_name, search_id)
    status, results = search_vectors(index_client, table_name, vector_item)
    print("-----milvus search status------", status)

    infos = []
    posters = []
    for results_id in results.id_array:
        info = search_by_milvus_ids(conn, cursor, table_name, results_id)
        poster = get_posters_by_ids(host, results_id)
        infos.append(info)
        posters.append(poster)

    return infos, posters
