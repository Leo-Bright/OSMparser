# -*- coding:utf-8 -*-
from sklearn.datasets.samples_generator import make_blobs
from sklearn.cluster import MeanShift, estimate_bandwidth
import numpy as np
from itertools import cycle  ##python自带的迭代器模块


input_X = []
stations_coordinate_file_path = 'sanfrancisco/dataset/flow_data/tmas2012_stations.coordinate'
with open(stations_coordinate_file_path) as f:
    for line in f:
        id_lat_lon = line.strip().split(' ')
        lat = float(id_lat_lon[-2])
        lon = float(id_lat_lon[-1])
        input_X.append([lat, lon])

X = np.array(input_X)

bandwidth = estimate_bandwidth(X, quantile=0.3, n_samples=5000)

ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)

ms.fit(X)

labels = ms.labels_
print(labels)

cluster_centers = ms.cluster_centers_
print('cluster_centers:', cluster_centers)
##总共的标签分类
labels_unique = np.unique(labels)

n_clusters_ = len(labels_unique)
print("number of estimated clusters : %d" % n_clusters_)