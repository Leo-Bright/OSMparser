from imposm.parser import OSMParser
import json


# simple class that handles the parsed OSM data.
class OSMCounter(object):
    coordDic = {} #{osmid:(lat, lon)}
    nodeDic = {} #{osmid:(tag, coordinary)}
    selected_node_dic = {} #{osmid:(tag, coordinary)}
    highwayDic = {} #{osmid:(tag, refs)}
    wayDic = {} #{osmid:(tag, refs)}

    # osmid : do write the way's osmid to the result file ?
    # tag : do write the tag to the result  ?
    # refs_index: select the index of refs you want
    def print_ways_result(self, output_file, osmid=False, tag=False, allNodes=False, forLINE=False):

        for item in self.highwayDic.items():
            refs = item[1][-1]

            # filter the way that don't match the condition
            if len(refs) < 2:
                continue

            nodes = []
            if allNodes:
                nodes = refs
            else:
                nodes.append(refs[0])
                nodes.append(refs[-1])
            if osmid:
                output_file.write(str(item[0]) + ' ')
            if tag:
                output_file.write(str(item[1][0]) + ' ')
            else:
                for node_index in range(len(nodes)-1):
                    if forLINE:
                        output_file.write(str(nodes[node_index]) + ' ' + str(nodes[node_index+1]) + ' ' + '1' + '\n')
                        output_file.write(str(nodes[node_index+1]) + ' ' + str(nodes[node_index]) + ' ' + '1' + '\n')
                    else:
                        output_file.write(str(nodes[node_index]) + ' ' + str(nodes[node_index+1]) + '\n')

            #add choice nodes to dic:
            for node in nodes:
                if node in self.nodeDic:
                    self.selected_node_dic[node] = self.nodeDic[node]

    def ways(self, ways):
        # callback method for ways
        for osmid, tags, refs in ways:
            if 'highway' in tags:
                self.highwayDic[osmid] = (tags, refs)
            self.wayDic[osmid] = (tags, refs)

    def nodes(self, nodes):
        # callback method for nodes
        for osmid, tags, coordinary in nodes:
            self.nodeDic[osmid] = (tags, coordinary)

    def coords(self, coords):
        # callback method for coords
        for osmid, lat, lon in coords:
            self.coordDic[osmid] = (lat, lon)


# instantiate counter and parser and start parsing Proto ways
counter = OSMCounter()
p = OSMParser(concurrency=4, ways_callback=counter.ways, nodes_callback=counter.nodes, coords_callback=counter.coords)
p.parse('dataset/Porto.osm.pbf')


# highways road network with all nodes
f_highway_network = open(r'network/highway_allNodes.network', 'w+')
counter.print_ways_result(f_highway_network, allNodes=True, forLINE=False)
f_highway_network.close()

# selected nodes in the network
f_selected_nodes = open(r'network/selected_nodes.json', 'w+')
f_selected_nodes.write(json.dumps(counter.selected_node_dic))
f_selected_nodes.close()