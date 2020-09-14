import PathFinder
import handout.Map

def task(i):
    map_obj = handout.Map.Map_Obj(task=i)
    
    if i == 0:
        print("Showing my own map")
        map_obj.show_map()
        input("Press enter to solve")

    solver = PathFinder.PathFinder(map_obj.get_maps()[0], map_obj.start_pos, map_obj.goal_pos)

    print("Solution:\n", list(solver.solution_path))

    map_obj.draw_path(solver.solution_path)
    map_obj.show_map()
    
    

def main():
    for i in range(0, 5):
        print(f'Running task {i}')
        task(i)
        input("Press enter to begin next task\n\n")


if __name__ == '__main__':
    main()