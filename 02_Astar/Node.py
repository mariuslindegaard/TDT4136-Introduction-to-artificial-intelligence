class Node():
    def __init__(self, parent, location, goal=None, maze_map=None):
        '''If no parent, the node is expected to provide the goal and maze_map'''
        if parent is None:
            self.static_map = maze_map
            self.static_goal = tuple(goal)
        else:
            self.static_map = parent.static_map
            self.static_goal = parent.static_goal
        
        self.location = location
        self.id = self.location  # Unique id used in expand

        self.parent = parent
        self._update_metrics()

        # Used for plotting:
        self._expanded = False
        self._children = []
    
    def _update_metrics(self):
        if self.parent is None:
            self.path_dist = 0
        else:
            self.path_dist = self.parent.path_dist + self.static_map[self.location]
        self.priority = self.metric(self.location, self.static_goal) + self.path_dist
    
    
    @staticmethod
    def metric(a, b):
        '''Implementation of the L1 norm'''
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def expand(self, seen_ids: set) -> list:
        '''Returns a list of neighboring nodes not in "seen_ids"
        
        As specified in Astar.py'''
        new_nodes = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            new_location = (self.location[0] + dx, self.location[1] + dy)

            if self.static_map[new_location] == -1 or new_location in seen_ids:
                continue
            else:
                new_nodes.append(
                    Node(parent=self, location=new_location)
                )
        
        self._children = new_nodes
        self._expanded = True
        
        return new_nodes
    
    @property
    def is_goal(self) -> bool:
        return self.location == self.static_goal


    def propagate_path_enhancement(self, new_parent):
        '''When an enhancing path is found, propagate to all children'''
        assert self.parent.path_dist > new_parent.path_dist, "New path is not shorter when updating!"

        self.parent = new_parent
        self._update_metrics()

        if new_parent in self._children:
            self._children.remove(new_parent)

        for child in self._children:
            child.propagate_path_enhancement()
