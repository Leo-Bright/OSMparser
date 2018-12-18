node_coutn = set()
with open("sanfrancisco/network/highway_allNodes.network", 'r') as f:
    for line in f:
        osmids = line.strip().split(' ')

        node_coutn.add(int(osmids[0]))
        node_coutn.add(int(osmids[1]))

print(len(node_coutn))