import maze
import generate_maze
import sys
import random


# Solve maze using Pre-Order DFS algorithm, terminate with solution
def solve_dfs(m):
    # Implement solve_dfs
    cells_to_backtrack = []
    current_cell = 0
    visited_cells = 0

    # Search for solution while the current cell is not at the solution cell
    while current_cell != m.total_cells - 1:
        unvisited_neighbors = m.cell_neighbors(current_cell)
        if len(unvisited_neighbors) >= 1:
            # Choose a random neighbor and separate the tuple
            new_cell_tuple = random.choice(unvisited_neighbors)
            new_cell = new_cell_tuple[0]
            direction = new_cell_tuple[1]

            # Visit the new cell
            m.visit_cell(current_cell, new_cell, direction)
            # Append the cell to stack in case it needs to be backtracked later
            cells_to_backtrack.append(current_cell)
            # Move to the neighbor cell
            current_cell = new_cell
            visited_cells += 1
        else:
            # Blank out solution bits so it is no longer on the solution path
            m.backtrack(current_cell)
            current_cell = cells_to_backtrack.pop()
        m.refresh_maze_view()
    print('Maze solved')
    m.state = 'idle'

# Solve maze using BFS algorithm, terminate with solution
def solve_bfs(m):
    # TODO: Implement solve_bfs
    pass


def print_solution_array(m):
    solution = m.solution_array()
    print('Solution ({} steps): {}'.format(len(solution), solution))


def main(solver='dfs'):
    current_maze = maze.Maze('create')
    generate_maze.create_dfs(current_maze)
    if solver == 'dfs':
        solve_dfs(current_maze)
    elif solver == 'bfs':
        solve_bfs(current_maze)
    while 1:
        maze.check_for_exit()
    return

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
