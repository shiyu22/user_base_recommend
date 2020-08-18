from webserver.src.common.config import MILVUS_TABLE, IDS_TABLE, MOVIES_TABLE
from webserver.src.indexer.index import milvus_client, insert_vectors
from webserver.src.indexer.tools import connect_mysql, create_tables_mysql, load_ids_to_mysql, load_movies_to_mysql, join_movies_ids_mysql
import time


def init_table(index_client, conn, cursor, milvus_table=MILVUS_TABLE, ids_table=IDS_TABLE, movies_table=MOVIES_TABLE):
    status, ok = has_table(index_client, table_name)
    if not ok:
        print("create table.")
        create_table(index_client, table_name)
        create_index(index_client, table_name)
        create_tables_mysql(conn, cursor, ids_table, movies_table)


def insert_data(index_client, conn, cursor, dataset_path, movies_path, milvus_table=MILVUS_TABLE, ids_table=IDS_TABLE, movies_table=MOVIES_TABLE):
    vectors = np.load(dataset_path + '/h_item.npy')
    vectors = vectors.tolist()
    ids = [i for i in range(len(vectors))]
    status, _ = insert_vectors(index_client, milvus_table, vectors, ids)
    print("milvus insert status:", status)

    print("load data to mysql:\n1.load ids")
    load_ids_to_mysql(conn, cursor, ids_table, dataset_path+'/mov_id.csv')

    print("2.load movies")
    load_movies_to_mysql(conn, cursor, movies_table, movies_path+'/movies.dat')

    print("3.join info")
    join_movies_ids_mysql(conn, cursor, milvus_table, ids_table, movies_table)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_path', type=str)
    parser.add_argument('movies_path', type=str)
    args = parser.parse_args()

    index_client = milvus_client()
    conn = connect_mysql()
    cursor = conn.cursor()
    init_table(index_client, conn, cursor, table_name)
    insert_data(index_client, conn, cursor, table_name, args.dataset_path, args.movies_path)


if __name__ == '__main__':
    main()
