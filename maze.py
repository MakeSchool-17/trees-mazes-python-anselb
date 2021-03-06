import pygame
import sys

# Screen size and cell size used by the maze window
# Width and height of SCREEN_SIZE should be divisible by CELL_SIZE
SCREEN_SIZE = (640, 480)
CELL_SIZE = 32

# Some useful numbers needed for the bit manipulation
# Left-most 4 bits store backtrack path, next 4 bits solution,
# next 4 bits border and last 4 bits walls knocked down.
# From left to right, each 4 bit cluster represents W, S, E, N
# NOTE: Border bits are not currently used
#                   directions
#                WSENWSENWSENWSEN
DEFAULT_CELL = 0b0000000000000000
#                |bt||s ||b ||w |
WALL_BITS = 0b0000000000001111
BACKTRACK_BITS = 0b1111000000000000
SOLUTION_BITS = 0b0000111100000000

# Indices match each other
# WALLS[i] corresponds with COMPASS[i], DIRECTION[i], and OPPOSITE_WALLS[i]
WALLS = [0b1000, 0b0100, 0b0010, 0b0001]
OPPOSITE_WALLS = [0b0010, 0b0001, 0b1000, 0b0100]
COMPASS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
DIRECTION = ['W', 'S', 'E', 'N']

# Colors
BLACK = (0, 0, 0, 255)
NO_COLOR = (0, 0, 0, 0)
WHITE = (255, 255, 255, 255)
GREEN = (0, 255, 0, 255)
RED = (255, 0, 0, 255)
BLUE = (0, 0, 255, 255)
LIGHT_BLUE = (0, 0, 255, 100)
PURPLE = (150, 0, 150, 255)


class Maze:
    def __init__(self, initial_state='idle'):
        # Maze set up
        self.state = initial_state
        self.w_cells = int(SCREEN_SIZE[0] / CELL_SIZE)
        self.h_cells = int(SCREEN_SIZE[1] / CELL_SIZE)
        self.total_cells = self.w_cells * self.h_cells
        self.maze_array = [DEFAULT_CELL] * self.total_cells

        # Pygame set up
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.background = pygame.Surface(self.screen.get_size())
        self.m_layer = pygame.Surface(self.screen.get_size())
        self.s_layer = pygame.Surface(self.screen.get_size())
        self.setup_maze_window()

    # Return cell neighbors within bounds of the maze
    # Use self.state to determine which neighbors should be included
    def cell_neighbors(self, cell):
        # Logic for getting neighbors based on self.state
        # Get the location of the current cell
        x, y = self.x_y(cell)
        neighbors_list = []
        for direction in range(4):
            # Find location of neighbor cell based on current cell
            neighbor_x = x + COMPASS[direction][0]
            neighbor_y = y + COMPASS[direction][1]
            # If a cell is within the maze, get the index of that cell
            if self.cell_in_bounds(neighbor_x, neighbor_y):
                neighbor_cell = self.cell_index(neighbor_x, neighbor_y)
                # If the maze is generating, and the all the neighbor's
                # walls are still up, add the neighbor's cell index and
                # relative cell location to the list of neighbors
                if self.state == 'create':
                    if not (self.maze_array[neighbor_cell] & WALL_BITS):
                        neighbors_list.append((neighbor_cell, direction))
                # If the maze is getting solved, return all the neighbors that
                # are accessible and unvisited
                elif self.state == 'solve':
                    if (self.maze_array[cell] & WALLS[direction]):
                        if not (self.maze_array[neighbor_cell] &
                                (BACKTRACK_BITS | SOLUTION_BITS)):
                            neighbors_list.append((neighbor_cell, direction))
        return neighbors_list

    # Connect two cells by knocking down the wall between them
    # Update wall bits of from_cell and to_cell
    def connect_cells(self, from_cell, to_cell, compass_index):
        # Logic for updating cell bits
        # Knock down the walls between two cells by flipping the bits of
        # adjacent walls
        self.maze_array[from_cell] |= WALLS[compass_index]
        self.maze_array[to_cell] |= OPPOSITE_WALLS[compass_index]
        # Updates maze visualization
        self.draw_connect_cells(from_cell, compass_index)

    # Visit a cell along a possible solution path
    # Update solution bits of from_cell and backtrack bits of to_cell
    def visit_cell(self, from_cell, to_cell, compass_index):
        # Logic for updating cell bits
        # Clear solution bits out of from_cell
        self.maze_array[from_cell] &= ~SOLUTION_BITS
        # Update solution bits in from_cell using WALLS[compass_index]
        self.maze_array[from_cell] |= (WALLS[compass_index] << 8)
        # Upate backtrack bits in to_cell using OPPOSITE_WALLS[compass_index]
        self.maze_array[to_cell] |= (OPPOSITE_WALLS[compass_index] << 12)
        # Updates maze visualization
        self.draw_visited_cell(from_cell)

    # Backtrack from cell
    # Blank out the solution bits so it is no longer on the solution path
    def backtrack(self, cell):
        # Logic for updating cell bits
        # Clear solution bits of cell
        self.maze_array[cell] &= ~SOLUTION_BITS
        # Updates maze visualization
        self.draw_backtracked_cell(cell)

    # Visit cell in BFS search
    # Update backtrack bits for use in reconstruct_solution
    def bfs_visit_cell(self, cell, from_compass_index):
        # Logic for updating cell bits
        # Set backtrack bits for cell to point towards the cell it came from
        self.maze_array[cell] |= (OPPOSITE_WALLS[from_compass_index] << 12)
        # Updates maze visualization
        self.draw_bfs_visited_cell(cell)

    # Reconstruct path to start using backtrack bits
    def reconstruct_solution(self, cell):
        self.draw_visited_cell(cell)
        # Logic for reconstructing solution path in BFS
        # Get the direction for the previous cell based on current cell bits
        previous_cell_bits = (self.maze_array[cell] >> 12)
        try:
            direction = WALLS.index(previous_cell_bits)
        except ValueError:
            print('ERROR - BACKTRACK BITS INVALID!')

        # Calculate previous cell index using dirction towards previous cell
        x, y = self.x_y(cell)
        previous_x = x + COMPASS[direction][0]
        previous_y = y + COMPASS[direction][1]
        previous_cell = self.cell_index(previous_x, previous_y)

        # Update solution bits of previous cell to point towards current cell
        self.maze_array[previous_cell] |= (OPPOSITE_WALLS[direction] << 8)
        self.refresh_maze_view()

        # Reconstruct solution until reaching the start of maze
        if previous_cell != 0:
            self.reconstruct_solution(previous_cell)

    # Check if x, y values of cell are within bounds of maze
    def cell_in_bounds(self, x, y):
        return ((x >= 0) and (y >= 0)
                and (x < self.w_cells) and (y < self.h_cells))

    # Cell index from x, y values
    def cell_index(self, x, y):
        return y * self.w_cells + x

    # x, y values from a cell index
    def x_y(self, index):
        x = index % self.w_cells
        y = int(index / self.w_cells)
        return x, y

    # x, y point values from a cell index
    def x_y_pos(self, index):
        x, y = self.x_y(index)
        x_pos = x * CELL_SIZE
        y_pos = y * CELL_SIZE
        return x_pos, y_pos

    # Build solution array using solution bits
    # Use DIRECTION to return cardinal directions representing solution path
    def solution_array(self):
        solution = []

        # TODO: Logic to return cardinal directions representing solution path

        return solution

    # 'Knock down' wall between two cells, use in creation as walls removed
    def draw_connect_cells(self, from_cell, compass_index):
        x_pos, y_pos = self.x_y_pos(from_cell)
        if compass_index == 0:
            pygame.draw.line(self.m_layer, NO_COLOR, (x_pos, y_pos + 1),
                             (x_pos, y_pos + CELL_SIZE - 1))
        elif compass_index == 1:
            pygame.draw.line(self.m_layer, NO_COLOR, (x_pos + 1,
                             y_pos + CELL_SIZE), (x_pos + CELL_SIZE - 1,
                             y_pos + CELL_SIZE))
        elif compass_index == 2:
            pygame.draw.line(self.m_layer, NO_COLOR, (x_pos + CELL_SIZE,
                             y_pos + 1), (x_pos + CELL_SIZE,
                             y_pos + CELL_SIZE - 1))
        elif compass_index == 3:
            pygame.draw.line(self.m_layer, NO_COLOR, (x_pos + 1, y_pos),
                             (x_pos + CELL_SIZE - 1, y_pos))

    # Draw green square at cell, use to visualize solution path being explored
    def draw_visited_cell(self, cell):
        x_pos, y_pos = self.x_y_pos(cell)
        pygame.draw.rect(self.s_layer, GREEN, pygame.Rect(x_pos, y_pos,
                         CELL_SIZE, CELL_SIZE))

    # Draws a red square at cell, use to change cell to visualize backtrack
    def draw_backtracked_cell(self, cell):
        x_pos, y_pos = self.x_y_pos(cell)
        pygame.draw.rect(self.s_layer, RED, pygame.Rect(x_pos, y_pos,
                         CELL_SIZE, CELL_SIZE))

    # Draw green square at cell, use to visualize solution path being explored
    def draw_bfs_visited_cell(self, cell):
        x_pos, y_pos = self.x_y_pos(cell)
        pygame.draw.rect(self.s_layer, LIGHT_BLUE, pygame.Rect(x_pos, y_pos,
                         CELL_SIZE, CELL_SIZE))

    # Process events, add each layer to screen (blip) and refresh (flip)
    # Call this at the end of each traversal step to watch the maze as it is
    # generated. Skip call until end of creation/solution to make faster.
    def refresh_maze_view(self):
        check_for_exit()
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.s_layer, (0, 0))
        self.screen.blit(self.m_layer, (0, 0))
        pygame.display.flip()

    def setup_maze_window(self):
        # Set up window and layers
        pygame.display.set_caption('Maze Generation and Solving')
        pygame.mouse.set_visible(0)
        self.background = self.background.convert()
        self.background.fill(WHITE)
        self.m_layer = self.m_layer.convert_alpha()
        self.m_layer.fill(NO_COLOR)
        self.s_layer = self.s_layer.convert_alpha()
        self.s_layer.fill(NO_COLOR)

        # Draw grid lines (will be whited out as walls knocked down)
        for y in range(self.h_cells + 1):
            pygame.draw.line(self.m_layer, BLACK, (0, y * CELL_SIZE),
                             (SCREEN_SIZE[0], y * CELL_SIZE))
        for x in range(self.w_cells + 1):
            pygame.draw.line(self.m_layer, BLACK, (x * CELL_SIZE, 0),
                             (x * CELL_SIZE, SCREEN_SIZE[1]))

        # Color start cell blue and exit cell purple.
        # Assumes start at top-left and exit at bottom-right
        pygame.draw.rect(self.s_layer, BLUE,
                         pygame.Rect(0, 0, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(self.s_layer, PURPLE, pygame.Rect(
                         SCREEN_SIZE[0] - CELL_SIZE, SCREEN_SIZE[1] -
                         CELL_SIZE, CELL_SIZE, CELL_SIZE))


def check_for_exit():
    # Aims for 60fps, checks for events.
    # Without event check every frame, window will not exit!
    clock = pygame.time.Clock()
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit(0)
