import PathFinder
import handout.Map
import matplotlib.pyplot as plt
import numpy as np

def prettyPlot(solved_maze: PathFinder.PathFinder):
    assert solved_maze.solved, "Maze is not solved"
    maze_map = solved_maze.map_array

    image = np.zeros((maze_map.shape[0], maze_map.shape[1], 3))

    image[maze_map == -1] = np.array((255, 255, 0))
    
    plt.imshow(image)
    plt.show()
    

def task(i):
    map_obj = handout.Map.Map_Obj(task=i)
    
    map_obj.show_map()
    input("Enter to solve")
    solver = PathFinder.PathFinder(map_obj.get_maps()[0], map_obj.start_pos, map_obj.goal_pos)

    print("Solution:\n", list(solver.solution_path))

    if False:
        prettyPlot(solver)
    else:
        map_obj.draw_path(solver.solution_path)
        map_obj.show_map()
    
    return 
    

def main():
    for i in range(0, 6):

        task(i)
        input(f"Enter for {i}")

if __name__ == '__main__':
    main()