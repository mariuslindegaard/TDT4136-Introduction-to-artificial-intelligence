import copy
import itertools
import collections
from functools import wraps
from dataclasses import dataclass

from typing import Dict, List


class NoUnassignedVariables(Exception):
    """No variables unassigned"""


@dataclass
class FunctionLog:
    calls: int = 0
    failures: int = 0


_function_logs = {}
def log_function(func):
    """Wrapper for backtracking function logging times called an failures

    As specified in the assignment text."""
    global _function_logs
    _function_logs[func.__name__] = FunctionLog(0, 0)

    @wraps(func)
    def logging(*args, **kwargs):
        _function_logs[func.__name__].calls += 1

        ret = func(*args, **kwargs)

        if not bool(ret):
            _function_logs[func.__name__].failures += 1

        return ret

    return logging


class CSP:
    def __init__(self):
        # self.variables is a list of the variable names in the CSP
        self.variables = []

        # self.domains[i] is a list of legal values for variable i
        self.domains = {}

        # self.constraints[i][j] is a list of legal value pairs for
        # the variable pair (i, j)
        self.constraints = {}

    def add_variable(self, name, domain):
        """Add a new variable to the CSP. 'name' is the variable name
        and 'domain' is a list of the legal values for the variable.
        """
        self.variables.append(name)
        self.domains[name] = set(domain)
        self.constraints[name] = {}

    @staticmethod
    def get_all_possible_pairs(a, b):
        """Get a list of all possible pairs (as tuples) of the values in
        the lists 'a' and 'b', where the first component comes from list
        'a' and the second component comes from list 'b'.
        """
        return itertools.product(a, b)

    def get_all_arcs(self) -> collections.deque:
        """Get a list of all arcs/constraints that have been defined in
        the CSP. The arcs/constraints are represented as tuples (i, j),
        indicating a constraint between variable 'i' and 'j'.
        """
        return collections.deque((i, j) for i in self.constraints for j in self.constraints[i])

    def get_all_neighboring_arcs(self, var) -> List[tuple]:
        """Get a list of all arcs/constraints going to/from variable
        'var'. The arcs/constraints are represented as in get_all_arcs().
        """
        return [(i, var) for i in self.constraints[var]]

    def add_constraint_one_way(self, i, j, filter_function):
        """Add a new constraint between variables 'i' and 'j'. The legal
        values are specified by supplying a function 'filter_function',
        that returns True for legal value pairs and False for illegal
        value pairs. This function only adds the constraint one way,
        from i -> j. You must ensure that the function also gets called
        to add the constraint the other way, j -> i, as all constraints
        are supposed to be two-way connections!
        """
        if j not in self.constraints[i]:
            # First, get a list of all possible pairs of values between variables i and j
            self.constraints[i][j] = self.get_all_possible_pairs(self.domains[i], self.domains[j])

        # Next, filter this list of value pairs through the function
        # 'filter_function', so that only the legal value pairs remain
        self.constraints[i][j] = list(filter(
            lambda value_pair: filter_function(*value_pair),  # filter_function = lambda values: values[0] != values[1]
            self.constraints[i][j]
        ))

    def add_all_different_constraint(self, variables):
        """Add an Alldiff constraint between all of the variables in the
        list 'variables'.
        """
        for (i, j) in self.get_all_possible_pairs(variables, variables):
            if i != j:
                self.add_constraint_one_way(i, j, lambda x, y: x != y)

    def backtracking_search(self):
        """This functions starts the CSP solver and returns the found
        solution.
        """
        # Make a so-called "deep copy" of the dictionary containing the
        # domains of the CSP variables. The deep copy is required to
        # ensure that any changes made to 'assignment' does not have any
        # side effects elsewhere.
        assert self.variables, "There are no variables to solve for. The CSP might not be initialized"
        assignment = copy.deepcopy(self.domains)

        # Run AC-3 on all constraints in the CSP, to weed out all of the
        # values that are not arc-consistent to begin with
        self.inference(assignment, self.get_all_arcs())

        # Call backtrack with the partial assignment 'assignment'
        return self.backtrack(assignment)

    @log_function
    def backtrack(self, assignment: Dict[any, set]) -> Dict[any, set]:
        """The function 'Backtrack' from the pseudocode in the
        textbook.

        The function is called recursively, with a partial assignment of
        values 'assignment'. 'assignment' is a dictionary that contains
        a list of all legal values for the variables that have *not* yet
        been decided, and a list of only a single value for the
        variables that *have* been decided.

        When all of the variables in 'assignment' have lists of length
        one, i.e. when all variables have been assigned a value, the
        function should return 'assignment'. Otherwise, the search
        should continue. When the function 'inference' is called to run
        the AC-3 algorithm, the lists of legal values in 'assignment'
        should get reduced as AC-3 discovers illegal values.

        IMPORTANT: For every iteration of the for-loop in the
        pseudocode, you need to make a deep copy of 'assignment' into a
        new variable before changing it. Every iteration of the for-loop
        should have a clean slate and not see any traces of the old
        assignments and inferences that took place in previous
        iterations of the loop.
        """

        # Try picking a new variable to "guess" (aka search)
        # If there are no unassigned variables, we have solved the CSP :D
        try:
            var = self.select_unassigned_variable(assignment)
        except NoUnassignedVariables:
            return assignment

        for val in self.order_domain_values(var, assignment):
            # Consistency check is also handled in inference, but is done shallowly first for efficiency
            if self.is_consistent_with_assignment(var, val, assignment):
                assignment_new = copy.deepcopy(assignment)
                assignment_new[var] = {val}

                is_consistent = self.inference(assignment_new, self.get_all_arcs())  # Modifies assignment_new
                if is_consistent:
                    result = self.backtrack(assignment_new)
                    if result:
                        return result

        return {}

    def is_consistent_with_assignment(self, var, val, assignment: Dict[any, set]):
        """Checks whether assignment of val to var is consistent (shallowly)

        Only checks whether the assignment would allow the immediate neighbors to have an assignment as well, according
        to 'self.constraints' and 'assignment'.

        Does not modify assignment
        """
        # As AC-3 is implemented and used, this will always return True
        """
        old_val = copy.deepcopy(assignment[var])
        assignment[var] = [val]

        is_consistent = True
        for neighbor in self.constraints[var].keys():

            for (constr_val, constr_neighbor_val) in self.constraints[var][neighbor]:
                if constr_val == val and constr_neighbor_val in assignment[neighbor]:
                    break
            else:
                is_consistent = False
                break
            if not is_consistent:
                print("Actually not consistent!")
                break

        assignment[var] = old_val
        return is_consistent
        """
        return True

    @staticmethod
    def order_domain_values(var, assignment: Dict[any, set]):
        return assignment[var]

    @staticmethod
    def select_unassigned_variable(assignment: Dict[any, set]):
        """The function 'Select-Unassigned-Variable' from the pseudocode
        in the textbook. Should return the name of one of the variables
        in 'assignment' that have not yet been decided, i.e. whose list
        of legal values has a length greater than one.
        """
        # Selects the variable with the smallest domain

        low_score, low_var = float("inf"), None

        for var in assignment.keys():
            if 1 < len(assignment[var]) < low_score:
                low_score, low_var = len(assignment[var]), var

        if low_score == float("inf"):
            raise NoUnassignedVariables(
                f"No variable with |domain|>1 found in the total of {len(assignment)} variables"
            )

        return low_var

    def inference(self, assignment: Dict[any, set], queue: collections.deque) -> bool:
        """The function 'AC-3' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'queue'
        is the initial queue of arcs that should be visited.

        Modifies: assignment
        """
        assert type(queue) is collections.deque, \
            "The queue inputted in 'inference' must be a collections.queue, not a {type(queue)}"

        while queue:
            i, j = queue.popleft()
            if self.revise(assignment, i, j):
                if not assignment[i]:
                    return False

                for neighbor in self.constraints[i].keys():
                    if neighbor is not j:  # and (neighbor, i) not in queue:  # <-- takes twice the time (because queue)
                        queue.append((neighbor, i))

        return True

    def revise(self, assignment: Dict[any, set], i, j) -> bool:
        """The function 'Revise' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'i' and
        'j' specifies the arc that should be visited. If a value is
        found in variable i's domain that doesn't satisfy the constraint
        between i and j, the value should be deleted from i's list of
        legal values in 'assignment'.

        Modifies: assignment
        """
        # Set of values in the domain that have not been verified to work yet
        unverified_domain = {val for val in assignment[i]}

        # todo; Optimize bu looping through the domain values when |domain[i]|*|domain[j]| < constraints[i][j]
        # Run through constraints and find which values are possible
        for i_val, j_val in self.constraints[i][j]:
            if i_val in unverified_domain and j_val in assignment[j]:
                unverified_domain.remove(i_val)

        # Evaluate where there are impossible values, and remove them if there are
        if unverified_domain:
            assignment[i] -= unverified_domain
            return True
        else:
            return False


def create_map_coloring_csp():
    """Instantiate a CSP representing the map coloring problem from the
    textbook. This can be useful for testing your CSP solver as you
    develop your code.
    """
    csp = CSP()
    states = ['WA', 'NT', 'Q', 'NSW', 'V', 'SA', 'T', "ML"]
    edges = {'SA': ['WA', 'NT', 'Q', 'NSW', 'V'], 'NT': ['WA', 'Q'], 'NSW': ['Q', 'V', "ML"]}
    colors = ['red', 'green', 'blue']
    for state in states:
        csp.add_variable(state, colors if state != "ML" else ["red"])
    for state, other_states in edges.items():
        for other_state in other_states:
            csp.add_constraint_one_way(state, other_state, lambda i, j: i != j)
            csp.add_constraint_one_way(other_state, state, lambda i, j: i != j)
    return csp


def create_sudoku_csp(filename):
    """Instantiate a CSP representing the Sudoku board found in the text
    file named 'filename' in the current directory.
    """
    csp = CSP()
    board = list(map(lambda x: x.strip(), open(filename, 'r')))

    for row in range(9):
        for col in range(9):
            if board[row][col] == '0':
                csp.add_variable('%d-%d' % (row, col), list(map(str, range(1, 10))))
            else:
                csp.add_variable('%d-%d' % (row, col), [board[row][col]])

    for row in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col) for col in range(9)])
    for col in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col) for row in range(9)])
    for box_row in range(3):
        for box_col in range(3):
            cells = []
            for row in range(box_row * 3, (box_row + 1) * 3):
                for col in range(box_col * 3, (box_col + 1) * 3):
                    cells.append('%d-%d' % (row, col))
            csp.add_all_different_constraint(cells)

    return csp


def print_sudoku_solution(solution):
    """Convert the representation of a Sudoku solution as returned from
    the method CSP.backtracking_search(), into a human readable
    representation.
    """
    for row in range(9):
        for col in range(9):
            (elem, ) = solution['%d-%d' % (row, col)]
            print(f" {elem} ", end="")
            if col == 2 or col == 5:
                print('|', end="")
        print(r"")
        if row == 2 or row == 5:
            print(r' -  -  - + -  -  - + -  -  - ')


def solve_case(sudoku_filename=None):
    if sudoku_filename:
        print("Solving sudoku", sudoku_filename)

        csp = create_sudoku_csp(sudoku_filename)
        solution = csp.backtracking_search()

        if solution:
            print_sudoku_solution(solution)
        else:
            print("Unable to solve")

    else:
        print("Solving custom map coloring")

        csp = create_map_coloring_csp()
        solution = csp.backtracking_search()

        if solution:
            print(solution)
        else:
            print("Unable to solve")

    print(f"Backtrack called {_function_logs[csp.backtrack.__name__].calls} times, "
          f"failed {_function_logs[csp.backtrack.__name__].failures} times.")
    _function_logs[csp.backtrack.__name__] = FunctionLog(0, 0)


def main():
    for sudoku in ["easy.txt", "medium.txt", "hard.txt", "veryhard.txt", "extreme.txt"]:
        solve_case(sudoku)
        print()
    solve_custom_map_coloring = True
    if solve_custom_map_coloring:
        solve_case()


if __name__ == "__main__":
    main()

