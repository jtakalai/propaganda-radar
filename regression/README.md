# Data sciencing

Serbian stop words from https://github.com/UlfetaMarovac/stopwordsSerbian

Stop words shouldn't be filtered out, instead, they should become another label in word descriptor vector, along with labels

## Experiments

The experiments use only `../viljami/propaganda-radar/data/data.csv` as project
data. `SSWdictionary.csv` is used as an optional Serbian stopword list; its
first, headerless column contains the words.

Run from this directory with:

```sh
.venv/bin/python main.py
```

`regression.ipynb` compares TF-IDF plus logistic regression with and without
stopword labels. In the labelled condition, every Serbian stopword is replaced
by the shared `stopword` token, so stopword presence remains a feature without
giving each stopword a separate feature. TF-IDF produces one feature-vector row
per headline, and logistic regression learns the mapping from those vectors to
labels.

`tsne-example.ipynb` compares the same two TF-IDF representations visually.
It applies `TruncatedSVD` before t-SNE because TF-IDF is sparse and
high-dimensional. t-SNE is exploratory and is not a classifier metric.

The split keeps rows with the same `cluster_id` together. Rows without a
cluster ID are treated as their own groups. The dataset is small and
imbalanced, so inspect per-class metrics rather than relying on accuracy.

