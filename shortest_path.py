#!/usr/bin/python
# -*- encoding: utf8 -*-

from tools import graph
import random
import json
import sys


__author__ = 'Leo'


def main(network_input="sanfrancisco/network/sf_roadnetwork",
         intersection_input="sanfrancisco/dataset/nodes_intersection.json",
         walks_output="res/sf_roadnetwork.walks",
         node_type_output="sanfrancisco/dataset/node_type.txt",
         walk_num=10, walk_length=100):

    print 'Load a road Graph...'
    G = graph.load_edgelist(network_input, undirected=True)
    print 'Generate random walks...'

    print("Number of nodes: {}".format(len(G.nodes())))

    num_walks = len(G.nodes()) * walk_num

    print("Number of walks: {}".format(num_walks))

    data_size = num_walks * walk_length

    print("Data size (walks*length): {}".format(data_size))

    print("Walking...")
    # walks = graph.build_deepwalk_corpus(G, num_paths=walk_num,
    #                                     path_length=walk_length, alpha=0, rand=random.Random(0))

    everynode_walks = graph.build_shortest_path(G, num_paths=walk_num, rand=random.Random(0))

    random_walk_json = network_input.rsplit('/', 1)[0] + '/tmp_walk_fname.json'

    # with open(random_walk_json, 'w+') as tmp_walks:
    #     tmp_walks.write(json.dumps(walks))


    with open(walks_output, 'w+') as f:
        count = 0
        for node_walks in everynode_walks:
            for walk in node_walks:
                f.write('%s\n' % ' 0 '.join(map(str, walk)))
            count += 1
            if count % 100 == 0:
                ratio = float(count * walk_num) / num_walks
                sys.stdout.write(("\rwalking ratio is :"
                                  "%d/%d (%.2f%%) "
                                  "" % (count,
                                        num_walks / walk_num,
                                        ratio * 100,
                                        )))
                sys.stdout.flush()

    print("Walking done...")

    print("Generating note type...")


    with open(intersection_input, 'r') as intersection_file:
        intersection = json.loads(intersection_file.readline())
        intersection_2 = intersection["2"]
        intersection_3 = intersection["3"]
        intersection_4 = intersection["4"]

    nodes = set()
    for node_walks in everynode_walks:
        for walk in node_walks:
            for node in walk:
                nodes.add(node)

    sorted_nodes = list(nodes)
    sorted_nodes.sort()

    with open(node_type_output, 'w+') as node_type_file:
        for node in sorted_nodes:
            if node in intersection_2:
                node_type_file.write(str(node) + ' 2\n')
            elif node in intersection_3:
                node_type_file.write(str(node) + ' 3\n')
            elif node in intersection_4:
                node_type_file.write(str(node) + ' 4\n')
            else:
                node_type_file.write(str(node) + ' 1\n')


main(network_input="sanfrancisco/network/sf_roadnetwork",
     intersection_input="sanfrancisco/dataset/nodes_intersection.json",
     walks_output="sanfrancisco/network/sf_shortest_path.walks",
     node_type_output="sanfrancisco/dataset/node_type.txt",
     walk_num=10)