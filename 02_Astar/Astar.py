'''A general implementation of the A-star algorithm for static environments

Node object requirements:
    has the following properties:
        Node.priority: The A* priority. Lowest is prioritized first
        Node.id: A unique sortable id (used in a set) to check for identical nodes
        Node.expand(visited_ids: set): Return a list of all neighboring
            nodes with ids not in visited_ids. Sets Node.parent
        Node.parent: The parent node to be used in finding the path after completion
            It is expected that this value is set during Node.expand by the user.
        Node.is_goal: True iff the node is the goal node
'''
import queue

def _inf_range():
    '''Generaes an infinite sequence from 0'''
    n = 0
    while True:
        yield n
        n += 1


def find_goal(start_node):
    '''Takes in a start node and returns a goal-node.
       
    Returns None if no path to goal was found.'''
    frontier = queue.PriorityQueue()  # The nodes at the frontier
    expanded_ids = set()  # A set of id of all expanded nodes
    initialized_ids = set()  # A set of ids of all nodes in or behind frintier 
    
    enumeration = _inf_range()

    initialized_ids.add(start_node.id)
    this_node = start_node

    while not this_node.is_goal:
        # Check that the node position is not already expanded, and if it is destroy this node
        if this_node.id in expanded_ids and True:
            print(f"Removed node at {this_node.id}")
            this_node.parent._children.remove(this_node)
            if frontier.empty():
                return None
            this_node = frontier.get()[-1]
            continue

        expanded_ids.add(this_node.id)
        print("Expanding node at", this_node.id,
              "with priority", this_node.priority)
        # Expand to new nodes not yet expanded
        new_nodes = this_node.expand(expanded_ids)
        
        # Add new nodes to the frointier and initialized nodes
        for node in new_nodes:
            assert this_node.priority <= node.priority, \
                "The A* assumption is not upheld"

            frontier.put(
                (
                    node.priority,  # The A* priority heuristic for the node 
                                    # (by which the queue is sorted)
                    next(enumeration),  # An enumeration of each explored node
                                        # used for tie-breaking
                    node  # The node itself
                )
            )
        initialized_ids |= {node.id for node in new_nodes}
        # Get the next node from the frontier according to priority
        if frontier.empty():
            return None
        this_node = frontier.get()[-1]

    return this_node
