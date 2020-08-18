# User-based Recommendation System With Milvus



## Prepare datasets

1. Downland and extract the MovieLens-1M dataset

   ```bash
   $ cd user_base_recommend/pinsage
   $ wget http://files.grouplens.org/datasets/movielens/ml-1m.zip
   $ unzip ml-1m.zip
   ```
   
2. Processing data as a pickle file

## Run model with DGL

This model returns items embedding that are K nearest neighbors of the latest item the user has interacted. The distance between two items are measured by inner product distance of item embeddings, which are learned as outputs of [PinSAGE](https://arxiv.org/pdf/1806.01973.pdf).

   