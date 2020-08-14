import logging as log
from common.config import DEFAULT_TABLE
from indexer.index import milvus_client, create_table, insert_vectors, create_index, has_table
from indexer.tools import connect_mysql, create_table_mysql, search_by_image_id, load_data_to_mysql
import datetime
import time
from indexer.logs import write_log
import uuid
import os

def get_img_ids(conn, cursor, ids_image, img, table_name):
    img_list = []
    ids_img = []
    info = []

    for i in range(len(ids_image)):
        has_id = search_by_image_id(conn, cursor, ids_image[i], table_name)
        if has_id:
            print("The id of image has exists:", ids_image[i])
            info.append(ids_image[i])
            continue
        else:
            img_list.append(img[i])
            ids_img.append(ids_image[i])

    return img_list, ids_img, info


def get_ids_file(ids_milvus, ids_image, file_name):
    with open(file_name,'w') as f:
        for i in range(len(ids_image)):
            line = str(ids_milvus[i]) + "," + ids_image[i] + '\n'
            f.write(line)


def init_table(index_client, conn, cursor, table_name):
    status, ok = has_table(index_client, table_name)
    if not ok:
        print("create table.")
        create_table(index_client, table_name)
        create_index(index_client, table_name)
        create_table_mysql(conn, cursor, table_name)


def insert_img(index_client, conn, cursor, img_to_vec, insert_img_list, insert_ids_list, table_name):
    time1 = time.time()
    vectors_img, insert_ids_list = img_to_vec(insert_img_list, insert_ids_list)
    time2 = time.time()
    print("-----doing vgg time-----", time2-time1)
    print(len(vectors_img),len(insert_ids_list))
    status, ids_milvus = insert_vectors(index_client, table_name, vectors_img)
    time3 = time.time()
    print("-----doing milvus insert time-----", time3-time2)

    file_name = str(uuid.uuid1()) + ".csv"
    get_ids_file(ids_milvus, insert_ids_list, file_name)
    print("load data to mysql:", file_name)
    load_data_to_mysql(conn, cursor, table_name, file_name)
    time4 = time.time()
    print("-----doing mysql insert time-----", time4-time3)
    if os.path.exists(file_name):
        os.remove(file_name)
    return status


def get_imlist(path):
    return [os.path.join(path, f) for f in os.listdir(path) if (f.endswith('.jpg') or f.endswith('.png'))]


def do_insert(index_client, conn, cursor, img_to_vec, ids_image, file, size, table_name):
    if not table_name:
        table_name = DEFAULT_TABLE
    if not size:
        size = 200
    img = get_imlist(file)
    print("table_name:", table_name, ", num of orgin ids:", len(ids_image),", num of orgin img:", len(img))

    if len(ids_image)!= len(img):
        return "The number of pictures is not consistent with the ID number, please check!", None

    init_table(index_client, conn, cursor, table_name)
    img_list, ids_img, info = get_img_ids(conn, cursor, ids_image, img, table_name)
    print("num of the insert images:", len(img_list))
    if not img_list:
        return None, "All the image id exists!"
    try:
        i = 0
        while i+size<len(ids_img):
            insert_img_list = img_list[i:i+size]
            insert_ids_img = ids_img[i:i+size]
            i = i+size
            print("doing insert, size:", size, "the num of insert vectors:", len(insert_img_list))
            time1 = time.time()
            status = insert_img(index_client, conn, cursor, img_to_vec, insert_img_list, insert_ids_img, table_name)
            time2 = time.time()
            print("-----doing insert time-----", time2-time1)
        else:
            insert_img_list = img_list[i:len(ids_image)]
            insert_ids_img = ids_img[i:len(ids_image)]
            print("doing insert, size:", size, ",the num of insert vectors:", len(insert_img_list))
            status = insert_img(index_client, conn, cursor, img_to_vec, insert_img_list, insert_ids_img, table_name)

        return status, info
    except Exception as e:
        # log.error(e)
        write_log(e, 1)
        return None, "Error with {}".format(e)
