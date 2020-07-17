import json


def get_missing_tag_node(network_file_path, node2tags, increament_tag_file_path):
    with open(increament_tag_file_path) as increament:
        pass

    with open(network_file_path) as network:
        for line in network:
            node1_node2 = line.split(' ')
            node1, node2 = node1_node2[0], node1_node2[1]



if __name__ == '__main__':

    network_file_path = "sanfrancisco/network/sf_roadnetwork"

    node2tags = json.load(open("sanfrancisco/dataset/node_tags.json"))

    increament_tag_file_path = "sanfrancisco/dataset/node_with_crossing_increament_stop.tag"

    increament_nodes = get_missing_tag_node(network_file_path, node2tags, increament_tag_file_path)

