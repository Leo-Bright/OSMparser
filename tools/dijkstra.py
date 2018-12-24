import time
import heapq
import copy


def dijkstra(G, start):     # dijkstra algorithm
    INF = float("inf")

    dis = dict((key, INF) for key in G)    # distance of start to end
    dis[start] = 0
    vis = dict((key, False) for key in G)     # whether is visited, 1 is true , 0 is false
    # heap optimise
    pq = []    # store values in heap
    heapq.heappush(pq, [dis[start], start])

    t3 = time.time()
    path = dict((key, [start]) for key in G)    # record every shortest path from start to end
    while len(pq) > 0:
        v_dis, v = heapq.heappop(pq)    # get the shortest path and node in unvisited nodes.
        if vis[v] == True:
            continue
        vis[v] = True
        # p = path[v].copy()    # the shortest path from start to v node
        p = copy.copy(path[v])
        for node in G[v]:    # the nodes directly link to v
            new_dis = dis[v] + float(G[v][node])
            if new_dis < dis[node] and (not vis[node]):    # if the nodes directly link to v have a better distance,than update
                dis[node] = new_dis    # update the new distance of the node
              #  dis_un[node][0] = new_dis    # update the distance of start to unvisited nodes
                heapq.heappush(pq, [dis[node], node])
                # temp = p.copy()
                temp = copy.copy(p)
                temp.append(node)    # update the path of start to node
                path[node] = temp

    t4 = time.time()
    print('Dijkstra start form ' + str(start) + ' use time :', t4-t3)
    return dis, path