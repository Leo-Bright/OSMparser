from imposm.parser import OSMParser

# simple class that handles the parsed OSM data.
class HighwayCounter(object):
    wayList = []
    wayCount = 0

    def ways(self, ways):
        # callback method for ways
        for osmid, tags, refs in ways:
          # self.highways += 1
          #   self.wayCount += 1
          #   self.wayList.append(refs)
            self.wayList.append((osmid, tags, refs))

# instantiate counter and parser and start parsing
counter = HighwayCounter()
p = OSMParser(concurrency=4, ways_callback=counter.ways)
p.parse('Porto.osm.pbf')

# done
print counter.wayCount
f = open(r'way_network.result', 'w+')

for osmid, tags, refs  in counter.wayList:
    # nodes = str(refs[0]) + " " + str(refs[-1])
    nodes = str(osmid) + " " + str(tags) + " " + str(refs)
    print(nodes)
    f.write(nodes + '\n')
f.close()