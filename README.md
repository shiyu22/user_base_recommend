# User-based Recommendation System with Milvus



## Prerequisite

- **[Milvus 0.10.2](https://milvus.io/docs/v0.10.2/milvus_docker-cpu.md)**
- **[DGL](https://github.com/dmlc/dgl)**
- **MySQL**



## Data preparation

The data source is [MovieLens million-scale dataset (ml-1m)](http://files.grouplens.org/datasets/movielens/ml-1m.zip), created by GroupLens Research. Refer to [ml-1m-README](http://files.grouplens.org/datasets/movielens/ml-1m-README.txt) for more information.

1. Clone the project

   ```bash
   $ git clone https://github.com/milvus-io/bootcamp.git
   ```
   
2. Downland and extract the MovieLens-1M dataset

   ```bash
   # Make sure you are in the pinsage folder
   $ cd bootcamp/solutions/user_base_recommend/webserver/src/pinsage
   $ wget http://files.grouplens.org/datasets/movielens/ml-1m.zip
   $ unzip ml-1m.zip
   ```

3. Processing data as a pickle file

   ```bash
   # Install the requirements
   $ pip install -r ../../requirements.txt
   $ mkdir output
   $ python process_movielens1m.py ./ml-1m ./output
   ```

   You can see that two files are generated in the **output** directory: **data.pkl** and **mov_id.csv**.



## Run model with DGL

This model returns items embedding that are K nearest neighbors of the latest item the user has interacted. The distance between two items are measured by inner product distance of item embeddings, which are learned as outputs of [PinSAGE](https://arxiv.org/pdf/1806.01973.pdf).

```bash
$ python model.py output --num-epochs 100 --num-workers 2 --hidden-dims 256
```

It will generate the **h_item.npy** file in the **output** directory.

 

## Load data

Before running the script, please modify the parameters in **webserver/src/common/config.py**:

| Parameter     | Description               | Default setting |
| ------------- | ------------------------- | --------------- |
| MILVUS_HOST   | milvus service ip address | 127.0.0.1       |
| MILVUS_PORT   | milvus service port       | 19530           |
| PG_HOST       | postgresql service ip     | 127.0.0.1       |
| PG_PORT       | postgresql service port   | 5432            |
| PG_USER       | postgresql user name      | postgres        |
| PG_PASSWORD   | postgresql password       | postgres        |
| PG_DATABASE   | postgresql datebase name  | postgres        |
| DEFAULT_TABLE | default table name        | milvus_qa       |

Please modify the parameters of Mysql and Milvus according to your environment, then run the script:

```bash
# Make sure you are in the src folder
$ cd ..
$ python insert_milvus.py ./pinsage/output ./pinsage/ml-m1
```

> If you insert date failed, please delete the table you have inserted to Milvus and Mysql, and update the file [./pinsage/ml-m1/movies.dat]().



## Run webserver

```bash
$ python main.py
# You are expected to see the following output.
Using backend: pytorch
INFO:     Started server process [2415]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```



## Run webclient

