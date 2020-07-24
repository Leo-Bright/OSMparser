import json


def get_missing_tag_node(network_file_path, node2tags, increament_tag_file_path, output):

    result = set()

    nodes_in_increament_file = set()
    with open(increament_tag_file_path) as increament_file:
        for line in increament_file:
            node_tag = line.strip().split(' ')
            node, tag = node_tag[0], node_tag[1]
            if tag == '6':
                nodes_in_increament_file.add(node)

    nodes_in_network = set()
    with open(network_file_path) as network:
        for line in network:
            node1_node2 = line.split(' ')
            node1, node2 = node1_node2[0], node1_node2[1]
            nodes_in_network.add(node1)
            nodes_in_network.add(node2)

    for node in nodes_in_increament_file:
        if node in nodes_in_network:
            if node in node2tags:
                origin_tags = node2tags[node]
            else:
                result.add(node)
                continue
            if 'highway' not in origin_tags or origin_tags['highway'] != 'stop':
                result.add(node)

    with open(output, 'w+') as output_file:
        for item in result:
            output_file.write(item + '\n')
    return result


if __name__ == '__main__':

    network_file_path = "sanfrancisco/network/sf_roadnetwork"

    node2tags = json.load(open("sanfrancisco/dataset/node_tags.json"))

    increament_tag_file_path = "sanfrancisco/dataset/node_with_crossing_increament_stop.tag"

    increament_nodes = get_missing_tag_node(network_file_path, node2tags, increament_tag_file_path,
                                            'sanfrancisco/dataset/increament_nodes.txt')

    print len(increament_nodes), increament_nodes