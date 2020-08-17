from webserver.src.common.config import DEFAULT_TABLE
from webserver.src.indexer.index import milvus_client, insert_vectors
from webserver.src.indexer.tools import connect_mysql, load_data_to_mysql
import time


def init_table(index_client, conn, cursor, table_name):
    status, ok = has_table(index_client, table_name)
    if not ok:
        print("create table.")
        create_table(index_client, table_name)
        create_index(index_client, table_name)
        create_table_mysql(conn, cursor, table_name)


def insert_data(index_client, conn, cursor, table_name, dataset_path):
    vectors = np.load(dataset_path + '/h_item.npy')
    vectors = vectors.tolist()
    ids = [i for i in range(len(vectors))]
    status, _ = insert_vectors(index_client, table_name, vectors, ids)
    print("insert status:", status)
    load_data_to_mysql(conn, cursor, table_name, dataset_path+'/mov_id.csv')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_path', type=str)
    args = parser.parse_args()

    if not table_name:
        table_name = DEFAULT_TABLE
    index_client = milvus_client()
    conn = connect_mysql()
    cursor = conn.cursor()
    init_table(index_client, conn, cursor, table_name)
    insert_data(index_client, conn, cursor, table_name, args.dataset_path)


if __name__ == '__main__':
    main()
