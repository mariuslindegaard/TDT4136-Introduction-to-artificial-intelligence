import PathFinder
import handout.Map
import matplotlib.pyplot as plt
import numpy as np

def task(i):
    map_obj = handout.Map.Map_Obj(task=i)
    
    if i == 0:
        map_obj.show_map()
        input("Enter to solve")
    solver = PathFinder.PathFinder(map_obj.get_maps()[0], map_obj.start_pos, map_obj.goal_pos)

    print("Solution:\n", list(solver.solution_path))

    map_obj.draw_path(solver.solution_path)
    map_obj.show_map()
    
    

def main():
    for i in range(0, 6):

        task(i)
        input(f"Enter for {i}")

if __name__ == '__main__':
    main()