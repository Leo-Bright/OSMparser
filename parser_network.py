import parser
import pickle as pkl


def print_osm_network(osm_parsed_obj, output_file_path, highway=True, allNodes=False, onlyNode=False, forLINE=False):

    with open(output_file_path, 'w+') as output_file:

        if highway:
            target_way = osm_parsed_obj.highwayDic.items()
        else:
            target_way = osm_parsed_obj.wayDic.items()

        for item in target_way:
            refs = item[1][-1]

            # filter the way that don't match the condition
            if len(refs) < 2:
                continue

            nodes = []
            if allNodes:
                if not onlyNode:
                    nodes = refs
                else:
                    nodes.append(refs[0])
                    for ref_index in range(1, len(refs)-1):
                        if refs[ref_index] in osm_parsed_obj.nodeDic:
                            nodes.append(refs[ref_index])
                    nodes.append(refs[-1])
            else:
                nodes.append(refs[0])
                nodes.append(refs[-1])

            for node_index in range(len(nodes)-1):
                if forLINE:
                    output_file.write(str(nodes[node_index]) + ' ' + str(nodes[node_index+1]) + ' ' + '1' + '\n')
                    output_file.write(str(nodes[node_index+1]) + ' ' + str(nodes[node_index]) + ' ' + '1' + '\n')
                else:
                    output_file.write(str(nodes[node_index]) + ' ' + str(nodes[node_index+1]) + '\n')


def print_osm_tag(osm_parsed_obj, output_file_path, osmid=False):

    with open(output_file_path, 'w+') as output_file:

        for item in osm_parsed_obj.highwayDic.items():
            tag = str(item[1][0])
            if osmid:
                output_file.write(str(item[0]) + ' ')
            output_file.write(tag + '\n')


with open('london/dataset/london_parsed_obj.pkl', 'rb') as f:
    parsed_obj = pkl.load(f)

# highways road network with all nodes
highway_network_path = 'london/network/london_highway.network'
print_osm_network(parsed_obj, highway_network_path, highway=True, allNodes=False, onlyNode=False, forLINE=False)