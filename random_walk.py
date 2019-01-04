#!/usr/bin/python
# -*- encoding: utf8 -*-

from tools import graph
import random
import json


__author__ = 'Leo'


def main(network_input="sanfrancisco/network/sf_roadnetwork",
         intersection_input="sanfrancisco/dataset/nodes_intersection.json",
         walks_output="res/sf_roadnetwork.walks",
         node_type_output="sanfrancisco/dataset/node_type.txt",
         walk_num=10, walk_length=100):

  #  print 'Load a road Graph...'
    G = graph.load_edgelist(network_input, undirected=True)
  #  print 'Generate random walks...'

    print("Number of nodes: {}".format(len(G.nodes())))

    num_walks = len(G.nodes()) * walk_num

    print("Number of walks: {}".format(num_walks))

    data_size = num_walks * walk_length

    print("Data size (walks*length): {}".format(data_size))

    print("Walking...")
    walks = graph.build_deepwalk_corpus(G, num_paths=walk_num,
                                        path_length=walk_length, alpha=0, rand=random.Random(0))
    with open(walks_output, 'w+') as f:
        for walk in walks:
            f.write('%s\n' % ' 0 '.join(map(str, walk)))

    print("Walking done...")

    print("Generating note type...")

    with open(intersection_input, 'r') as intersection_file:
        intersection = json.loads(intersection_file.readline())

    def get_node_tyep(intersection, node):
        for (type, node_set) in intersection.items():
            if node in node_set:
                return type
        return '1'

    nodes = set()
    for walk in walks:
        for node in walk:
            nodes.add(node)

    sorted_nodes = list(nodes)
    sorted_nodes.sort()

    with open(node_type_output, 'w+') as node_type_file:
        for node in sorted_nodes:
            type = get_node_tyep(intersection, node)
            node_type_file.write(str(node) + ' ' + type + '\n')



main(network_input="tokyo/network/tokyo.network",
     intersection_input="tokyo/dataset/nodes_intersection.json",
     walks_output="tokyo/network/tokyo_random_wn10_wl640.walks",
     node_type_output="tokyo/dataset/node_type.txt",
     walk_num=10, walk_length=640
     )
