import maze
import random

# Create maze using Pre-Order DFS maze creation algorithm
def create_dfs(m):
    unvisited_neighbors = []
    current_cell = random.randint(0, m.total_cells - 1)
    visited_cells = 1

    while visited_cells < m.total_cells:
        current_neighbors = m.cell_neighbors(current_cell)
        if len(current_neighbors) >= 1:
            # Choose a random neighbor and separate the tuple
            new_cell_tuple = random.choice(current_neighbors)
            new_cell = new_cell_tuple[0]
            direction = new_cell_tuple[1]

            # Break the wall between celss
            m.connect_cells(current_cell, new_cell, direction)
            # Append the cell with unvisited neighbors to stack to revisit
            unvisited_neighbors.append(current_cell)
            # Move to the neighbor cell
            current_cell = new_cell
            visited_cells += 1
        else:
            current_cell = unvisited_neighbors.pop()
        m.refresh_maze_view()
    print('Maze generated')
    m.state = 'solve'

def main():
    current_maze = maze.Maze('create')
    create_dfs(current_maze)
    while 1:
        maze.check_for_exit()
    return

if __name__ == '__main__':
    main()
