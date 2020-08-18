# User-based Recommendation System With Milvus



## Prepare software

- #### [Milvus 0.10.2](https://milvus.io/docs/v0.10.2/milvus_docker-cpu.md)

- #### MySQL



## Prepare datasets

1. Downland and extract the MovieLens-1M dataset

   ```bash
   $ cd user_base_recommend/pinsage
   $ wget http://files.grouplens.org/datasets/movielens/ml-1m.zip
   $ unzip ml-1m.zip
   ```
   
2. Processing data as a pickle file

   ```bash
   $ mkdir output
   $ python process_movielens1m.py ./ml-1m ./output
   ```

   You can see under **output** has two file: **data.pkl** and **mov_id.csv**.



## Run model with DGL

This model returns items embedding that are K nearest neighbors of the latest item the user has interacted. The distance between two items are measured by inner product distance of item embeddings, which are learned as outputs of [PinSAGE](https://arxiv.org/pdf/1806.01973.pdf).

```bash
$ python model.py output --num-epochs 100 --num-workers 2 --hidden-dims 256
```

You can see the **h_item.npy** under **output**.

 

## Insert data to Milvus

1. Run [Milvus0.10.2](https://milvus.io/docs/milvus_docker-cpu.md)
2. Insert data

You should to change the Milvus host and port.

```bash
$ python insert_milvus.py ./pinsage/output ./pinsage/ml-m1
```



## Run webserver