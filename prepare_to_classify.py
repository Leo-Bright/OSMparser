from imposm.parser import OSMParser
import json


# simple class that handles the parsed OSM data.
class OSMCounter(object):
    relationDic = {} #{osmid:(tags, refs)}
    coordDic = {} #{osmid:(lat, lon)}
    nodeDic = {} #{osmid:(tags, coordinary)}
    wayDic = {} #{osmid:(tags, refs)}
    crossing_count = 0

    # osmid : do write the way's osmid to the result file ?
    # tag : do write the tag to the result  ?
    # refs_index: select the index of refs you want
    # coordinate: write the coordinate of the refs to result file or only the refs ?
    def prepare_classify_data(self, input, output):

        for line in input.readlines():
            line = line.strip()
            osmid_vector = line.split(' ')
            osmid, node_vec = osmid_vector[0], osmid_vector[1:]
            if len(node_vec) < 10:
                output.write(line.strip() + '\n')
                continue
            if osmid not in self.nodeDic.keys():
                output.write(line + ' ' + '-1' + '\n')
                continue
            node_tags = self.nodeDic[osmid][0]
            if 'crossing' in node_tags.keys():
                print('crossing key in the tags')
                output.write(line + ' ' + '1' + '\n')
                self.crossing_count += 1
            elif 'highway' in node_tags.keys():
                if 'crossing' == node_tags['highway']:
                    print('highway key and crossing value in the tags')
                    output.write(line + ' ' + '1' + '\n')
                    self.crossing_count += 1
                else:
                    print('this is not a crossing')
                    output.write(line + ' ' + '-1' + '\n')

            else:
                print('this is not a crossing')
                output.write(line + ' ' + '-1' + '\n')

        print(self.crossing_count)

    def count_node_in_way(self):
        node_osmid_dic = {} #{osmid:count,...)
        for osmid, (tags, refs) in self.wayDic.items():
            for node_osmid in refs:
                if node_osmid not in node_osmid_dic:
                    node_osmid_dic[node_osmid] = 1
                else:
                    node_osmid_dic[node_osmid] += 1

        for osmid, count in node_osmid_dic.items():
            if count > 6:
                print(osmid)



    def ways(self, ways):
        # callback method for ways
        for osmid, tags, refs in ways:
            if 'highway' in tags:
                self.wayDic[osmid] = (tags, refs)
            # self.wayDic[osmid] = (tags, refs)

    def nodes(self, nodes):
        # callback method for nodes
        for osmid, tags, coordinary in nodes:
            self.nodeDic[osmid] = (tags, coordinary)

    def coords(self, coords):
        # callback method for coords
        for osmid, lat, lon in coords:
            self.coordDic[osmid] = (lat, lon)

    def relations(self, relations):
        # callback method for relations
        for osmid, tags, refs in relations:
            self.relationDic[osmid] = (tags, refs)


# instantiate counter and parser and start parsing Proto ways
counter = OSMCounter()
p = OSMParser(concurrency=4, ways_callback=counter.ways, nodes_callback=counter.nodes,
              coords_callback=counter.coords, relations_callback=counter.relations)
p.parse('Porto.osm.pbf')

f_input = open(r'dataset/deepwalk_highway_64d.embeddings', 'r')
f_output = open(r'dataset/deepwalk_highway_64d_labeled.embeddings', 'w+')

counter.prepare_classify_data(f_input, f_output)
counter.count_node_in_way()

f_input.close()
f_output.close()
