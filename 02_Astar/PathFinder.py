import Astar
import numpy as np
import Node

class PathFinder():
    def __init__(self, maze_map: np.ndarray, start: tuple, goal: tuple):
        '''Note that map must have a border of -1'''
        self.map_array = maze_map
        self.goal = tuple(goal)
        self.start = tuple(start)

        self.start_node = Node.Node(
            parent=None, location=self.start,
            goal=self.goal, maze_map=self.map_array
            )
        self.solved = False
        self._final_node = None

    
    @property
    def final_node(self) -> Node.Node:
        '''Find the final node of the path
        
        Under the hood does all the hard work of pathfinding using A*'''
        if self.solved:
            if self._final_node is None:
                print("Warning: No solution was found.")
            return self._final_node

        # Do the A* magic
        self._final_node = Astar.find_goal(self.start_node)

        self.solved = True
        return self.final_node
    
    @property
    def solution_path(self) -> list:
        '''Get the solution path as a list of node locations visited'''
        path = []
        current_child = self.final_node  # Get the final node in the path

        # Iterate through the parents back to the root, add all visited notes to the path list
        while current_child is not None:
            path.append(current_child.location)
            current_child = current_child.parent
        
        return reversed(path)
    
    @property
    def all_children(self):
        '''Get all the nodes in the explored tree'''
        found_nodes = [self.start_node]
        idx = 0

        while idx < len(found_nodes):
            if found_nodes[idx]._expanded:
                found_nodes.extend(found_nodes[idx]._children)
            idx += 1
        
        return found_nodes
    