import math
import networkx as nx
import random
import time
import numpy as np

__all__ = ["ADA_star"]

class ADA_star:
    def __init__(self, s_start, s_goal, G, heursistic, weight = "weight", initial_epsilon = 1000):
        """Returns a search object, which can be used to find a path from a
        start state to a goal state in a graph. The search object can be 
        used to iteratively improve the path over time, as well as being
        called to update the graph with new weights. The search object, will
        then use previous work to find a new path in the updated graph.
        
        Class is responsible for the implementation of the Dynamic Anytime
        A* algorithm. This algorithm returns a path from a start state to a
        goal state. The algorithm is able to return a suboptimal path in a
        short amount of time. The algorithm is able to iteratively improve 
        the path over time by calling the compute_or_improve_path function.
        The algorithm is also able to cope with dynamic environments by 
        calling the update_graph function, which updates the graph with new
        weights. The algorithm makes use of previous work done when there
        are changes to the graph.


        Parameters
        ----------
        s_start : node
            Starting node for the path
        
        s_goal : node
            Goal node for the path
        
        G : networkx graph
            Graph to find the path in

        heursistic : function
            A function to evaluate the estimate of the distance
        from the a node to the target.  The function takes
        two node labels as arguments and must return a number.
        If the heuristic is inadmissible (if it might
        overestimate the cost of reaching the goal from a node),
        the result may not be a shortest path.

        weight : string
            The edge weights will be accessed via the edge attribute with 
        this key (that is, the weight of the edge joining `u` to `v` 
        will be ``G.edges[u, v][weight]``). If no such edge attribute
        exists, the weight of the edge is assumed to be one.
        
        Examples
        --------
        >>> random.seed(1)
        >>> G = nx.random_geometric_graph(100, 0.20, seed=896803)
        >>> for (u, v, w) in G.edges(data=True): #Euclidean distance between nodes
        ...     w['weight'] = np.sqrt((G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0])**2 + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1])**2)
        >>> s_start, s_goal = 42, 25       
        >>> def heursistic(u, v): #Euclidean distance between nodes
        >>> return np.sqrt((G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0])**2 + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1])**2)
         
        >>> # A* search for comparison
        >>> start_time = time.time()
        >>> path = nx.astar_path(G, s_start, s_goal, heursistic)
        >>> print("A* time: ", time.time() - start_time)
        A* time:  0.00012803077697753906
        >>> print("A* path: ", path)
        A* path:  [42, 32, 19, 72, 49, 29, 31, 94, 35, 25]

        >>> #create search object
        >>> search = ADA_star(s_start, s_goal, G, heursistic)
 
        >>> #compute first suboptimal path epsilon = 2
        >>> start_time = time.time()
        >>> search.compute_or_improve_path(epsilon=2)
        >>> path = search.extract_path()
        >>> print("ADA* epsilon = 2 time: ", time.time() - start_time)
        ADA* epsilon = 2 time:  0.0009984970092773438
        >>> print("epsilon = 2 path: ", path)
        epsilon = 2 path:  [42, 32, 24, 40, 59, 4, 66, 27, 35, 25]
        >>> print("epsilon = 2 path_weight: ", nx.path_weight(G, search.extract_path(), "weight"))
        epsilon = 2 path_weight:  1.4679609830956495

        >>> #compute second (better) suboptimal path
        >>> search.compute_or_improve_path(epsilon=1.2)
        >>> path = search.extract_path()
        >>> print("epsilon = 1.2 path: ", path)
        epsilon = 1.2 path:  [42, 32, 24, 12, 59, 4, 1, 27, 35, 25]
        >>> print("epsilon = 1.2 path_weight: ", nx.path_weight(G, path, "weight"))
        epsilon = 1.2 path_weight:  1.3335657361796027

        >>> #compute third (best) suboptimal path
        >>> search.compute_or_improve_path(epsilon=1)
        >>> path = search.extract_path()
        >>> print("epsilon = 1 path: ", path)
        epsilon = 1 path:  [42, 32, 19, 72, 49, 29, 31, 94, 35, 25]
        >>> print("epsilon = 1 path_weight: ", nx.path_weight(G, path, "weight"))
        epsilon = 1 path_weight:  1.29129785933092
 
        >>> #change graph edge weight
        >>> print("changing graph weight for edge (49, 97)")
        changing graph weight for edge (49, 97)
        >>> search.update_graph([[49, 97, 0]]) #add edge between 77 and 15 with weight 0
        >>> search.compute_or_improve_path(epsilon=1)
        >>> path = search.extract_path()
        >>> print("changed epsilon = 1 path: ", path)
        changed epsilon = 1 path:  [42, 32, 19, 72, 49, 97, 11, 31, 94, 35, 25]
        >>> print("changed epsilon = 1 path_weight: ", nx.path_weight(G, path, "weight"))
        changed epsilon = 1 path_weight:  1.1428811257616596
        """
        if s_start not in G or s_goal not in G:
            msg = f"Either source {s_start} or target {s_goal} is not in G"
            raise nx.NodeNotFound(msg)
        
        self.s_start, self.s_goal = s_start, s_goal

        self.heursistic = heursistic
        self.weight = weight
        self.G = G

        self.g, self.rhs, self.OPEN = {}, {}, {}

        # estimate g(s) of the cost from each state to the goal
        self.g = {s:math.inf for s in G.nodes()}

        # one-step lookahead cost
        self.rhs = {s:math.inf for s in G.nodes()}

        self.rhs[self.s_goal] = 0.0
        self.epsilon = initial_epsilon
        self.OPEN[self.s_goal] = self.key(self.s_goal)
        self.CLOSED, self.INCONS = set(), dict()

        self.visited = set()
        self.initialize = True
        self.compute_or_improve_path(self.epsilon)

    
    def compute_or_improve_path(self, epsilon) -> None:
        """
        Computes or 


        """
        if self.initialize: 
            self.epsilon = epsilon
            self.initialize = False
        
        else: #Do not update INCONS and OPEN on first call
            self.epsilon = epsilon
            #move states from INCONS to OPEN
            for state in self.INCONS:
                self.OPEN[state] = self.key(state)
            self.INCONS = dict()
            for state in self.OPEN:
                #update keys
                self.OPEN[state] = self.key(state)
            self.CLOSED = set()

        while True:
            s, v = self.smallest_key()
            
            if  (not ADA_star.key_lt(v, self.key(self.s_start))) and self.rhs[self.s_start] == self.g[self.s_start]:
                break

            self.OPEN.pop(s)
            self.visited.add(s)

            if self.g[s] > self.rhs[s]:
                self.g[s] = self.rhs[s]
                self.CLOSED.add(s)
                for sn in self.get_neighbor(s):
                    self.update_state(sn)
            else:
                self.g[s] = float("inf")
                for sn in self.get_neighbor(s):
                    self.update_state(sn)
                self.update_state(s)


    def update_state(self, s) -> None:

        if s != self.s_goal:
            self.rhs[s] = float("inf")
            for x in self.get_neighbor(s):
                self.rhs[s] = min(self.rhs[s], self.g[x] + self.cost(s, x))

        if s in self.OPEN:
            self.OPEN.pop(s)

        if self.g[s] != self.rhs[s]:
            if s not in self.CLOSED:
                self.OPEN[s] = self.key(s)
            else:
                self.INCONS[s] = 0


    def key(self, s):
        #return the key of a state
        if self.g[s] > self.rhs[s]:
            return [self.rhs[s] + (self.epsilon * self.heursistic(self.s_start, s)), self.rhs[s]]
        return [self.g[s] + self.heursistic(self.s_start, s), self.g[s]]


    def key_lt(key1, key2)-> bool:
        #compare two keys
        if key1[0] < key2[0]:
            return True
        if key1[0] == key2[0] and key1[1] < key2[1]:
            return True
        return False
    

    def smallest_key(self):
        # return the smallest key, smallest being the one with the lowest first element as priority, 
        # if the first elements are equal, the one with the lowest second element is chosen

        min_primary = math.inf
        min_secondary = math.inf
        min_index = None
        for key, value in self.OPEN.items():
            if value[0] <= min_primary:
                min_primary = value[0]
                min_index = key
                if value[1] < min_secondary:
                    min_secondary = value[1]
                    min_index = key

        return min_index, [min_primary, min_secondary]


    def cost(self, s, s_prime):
        return self.G[s][s_prime][self.weight]


    def get_neighbor(self, s):
        return self.G[s].keys()


    def extract_path(self):
        """
        Extract the path based on the PARENT set.
        :return: The planning path
        """

        path = [self.s_start]
        s = self.s_start

        while True:
            neighbours = self.get_neighbor(s)
            # find neighbour with lowest g value
            s = min(neighbours, key=lambda x: self.g[x] + self.cost(s, x))
            path.append(s)
            if s == self.s_goal:
                break

        return list(path)


    def update_graph(self, changes):
        """
        Update the graph with new edge weights
        :param changes: list of changes, each change is a list of [node1, node2, new_weight]
        :return: None        
        """
        for change in changes:
            self.G[change[0]][change[1]][self.weight] = change[2]
            self.G[change[1]][change[0]][self.weight] = change[2]
            self.update_state(change[0])
            self.update_state(change[1])
        #move states from INCONS to OPEN
        for state in self.INCONS:
            self.OPEN[state] = self.key(state)
        self.INCONS = dict()
        for state in self.OPEN:
            #update keys
            self.OPEN[state] = self.key(state)
        self.CLOSED = set()


if __name__ == "__main__":
    random.seed(1)
    G = nx.random_geometric_graph(100, 0.20, seed=896803)
    for (u, v, w) in G.edges(data=True): #Euclidean distance between nodes
        w['weight'] = np.sqrt((G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0])**2 + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1])**2)
    s_start, s_goal = 42, 25       
    def heursistic(u, v): #Euclidean distance between nodes
       return np.sqrt((G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0])**2 + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1])**2)
    
    # A* search for comparison
    start_time = time.time()
    path = nx.astar_path(G, s_start, s_goal, heursistic)
    print("A* time: ", time.time() - start_time)
    print("A* path: ", path)

    #create search object
    search = ADA_star(s_start, s_goal, G, heursistic)

    #compute first suboptimal path epsilon = 2
    start_time = time.time()
    search.compute_or_improve_path(epsilon=2)
    path = search.extract_path()
    print("ADA* epsilon = 2 time: ", time.time() - start_time)
    print("epsilon = 2 path: ", path)
    print("epsilon = 2 path_weight: ", nx.path_weight(G, search.extract_path(), "weight"))

    #compute second (better) suboptimal path
    search.compute_or_improve_path(epsilon=1.2)
    path = search.extract_path()
    print("epsilon = 1.2 path: ", path)
    print("epsilon = 1.2 path_weight: ", nx.path_weight(G, path, "weight"))

    #compute third (best) suboptimal path
    search.compute_or_improve_path(epsilon=1)
    path = search.extract_path()
    print("epsilon = 1 path: ", path)
    print("epsilon = 1 path_weight: ", nx.path_weight(G, path, "weight"))

    #change graph edge weight
    print("changing graph weight for edge (49, 97)")
    search.update_graph([[49, 97, 0]]) #add edge between 77 and 15 with weight 0
    search.compute_or_improve_path(epsilon=1)
    path = search.extract_path()
    print("changed epsilon = 1 path: ", path)
    print("changed epsilon = 1 path_weight: ", nx.path_weight(G, path, "weight"))