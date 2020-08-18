import logging as log
from common.config import MILVUS_TABLE, IDS_TABLE, MOVIES_TABLE
from indexer.index import milvus_client, search_vectors, get_vector_by_ids
from indexer.tools import connect_mysql, search_by_milvus_ids
import numpy as np
import torch
import pickle
import dgl


def get_latest_item(search_id):
    with open(OUT_PATH, 'rb') as f:
        dataset = pickle.load(f)
    g = dataset['train-graph']
    val_matrix = dataset['val-matrix'].tocsr()
    test_matrix = dataset['test-matrix'].tocsr()
    item_texts = dataset['item-texts']
    user_ntype = dataset['user-type']
    item_ntype = dataset['item-type']
    user_to_item_etype = dataset['user-to-item-type']
    timestamp = dataset['timestamp-edge-column']

    graph_slice = g.edge_type_subgraph([self.user_to_item_etype])
    latest_interactions = dgl.sampling.select_topk(graph_slice, 1, self.timestamp, edge_dir='out')
    user, latest_items = latest_interactions.all_edges(form='uv', order='srcdst')

    latest_item = latest_items[[search_id]].to(device=h_item.device)
    return latest_item.numpy().tolist()[0]


def do_search(index_client, conn, cursor, search_id):
    if not table_name:
        table_name = DEFAULT_TABLE
    latest_item = get_latest_item(search_id)
    print("-----latest_items-----", latest_item)

    _, vector_item = get_vector_by_ids(index_client, table_name, latest_item)
    status, results = search_vectors(index_client, table_name, vector_item)

    print("-----milvus search status------", status)
    results = search_by_milvus_ids(conn, cursor, table_name, results.id_array[0])

    return results
