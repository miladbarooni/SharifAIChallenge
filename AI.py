from Model import *
import random


class AI:
    map: list = list()
    init: bool = True
    state: str = ""
    our_base: Cell = None

    def __init__(self):
        # Current Game State
        self.game: Game = None
        # Answer
        self.message: str = ''
        self.direction: int = 0
        self.value: int = 0
        self.neighbours: list = list()
        self.type: str = ""

    def turn(self) -> (str, int, int):
        # initial the map
        if AI.init:
            AI.map = [[0 for _ in range(self.game.mapHeight)] for _ in range(self.game.mapWidth)]
            AI.our_base = self.game.ant.getNeightbourCell(0, 0)
            AI.init = False
        # update all neighbours
        self.update_neighbour()
        # update the map (that is not very correct just a view)
        self.update_map()
        if self.game.antType == 1:
            self.worker()
        # elif self.game.antType == 0:
        #     self.soldier()
        self.message = ""
        self.value = 1
        return self.message, self.value, self.direction

    def update_neighbour(self):
        self.neighbours = list()
        for row_counter in range(-1 * self.game.viewDistance, self.game.viewDistance + 1):
            bound = self.game.viewDistance - abs(row_counter)
            for column_counter in range(-1 * bound, bound + 1):
                self.neighbours.append(self.game.ant.getNeightbourCell(row_counter, column_counter))

    def update_map(self):
        for neighbour in self.neighbours:
            AI.map[neighbour.x][neighbour.y] = neighbour

    def worker(self):
        there_is_nothing_around = True
        if self.game.ant.currentResource.value >= 1:
            shortest_path = self.find_shortest_path(self.game.ant.getNeightbourCell(0, 0), AI.map[self.game.baseX][self.game.baseY])
            if shortest_path:
                self.direction = self.find_direction_from_cell(shortest_path[1])
                there_is_nothing_around = False
            else:
                there_is_nothing_around = True
        else:
            resource_cell = self.find_nearest_resource()
            shortest_path = self.find_shortest_path(self.game.ant.getNeightbourCell(0, 0), resource_cell)
            if shortest_path:
                self.direction = self.find_direction_from_cell(shortest_path[1])
                there_is_nothing_around = False
            else:
                there_is_nothing_around = True
        if there_is_nothing_around:
            self.random_walk()

    def random_walk(self):
        neighbours = self.adjacent_neighbour_finder_map(self.game.ant.getNeightbourCell(0, 0))
        index = random.randint(0, len(neighbours))
        self.direction = self.find_direction_from_cell(neighbours[index])

    def soldier(self):
        self.random_walk()

    def find_shortest_path(self, source, dest):
        queue = [[source]]
        visited = set()
        while len(queue) != 0:
            path = queue.pop(0)
            front = path[-1]
            if front == dest:
                return path
            elif front not in visited:
                for adjacent_neighbour in self.adjacent_neighbour_finder_map(front):
                    new_path = list(path)
                    new_path.append(adjacent_neighbour)
                    queue.append(new_path)
                visited.add(front)
        return None

    def find_nearest_resource(self):
        best_dist = 10000
        best_result = None
        for neighbour in self.neighbours:
            if neighbour.resource_type != 2 and self.manhattan_distance(
                    self.game.ant.getNeightbourCell(0, 0), neighbour) < best_dist:
                best_result = neighbour
                best_dist = self.manhattan_distance(self.game.ant.getNeightbourCell(0, 0), neighbour)
        return best_result

    def adjacent_neighbour_finder_map(self, cell):
        up, down, left, right = list(), list(), list(), list()
        if AI.map[(cell.x + 1) % self.game.mapWidth][cell.y] != 0 \
                and AI.map[(cell.x + 1) % self.game.mapWidth][cell.y].type != 2:
            right = AI.map[(cell.x + 1) % self.game.mapWidth][cell.y]
        if AI.map[(cell.x - 1) % self.game.mapWidth][cell.y] != 0 \
                and AI.map[(cell.x - 1) % self.game.mapWidth][cell.y].type != 2:
            left = AI.map[(cell.x - 1) % self.game.mapWidth][cell.y]
        if AI.map[cell.x][(cell.y + 1) % self.game.mapHeight] != 0 \
                and AI.map[cell.x][(cell.y + 1) % self.game.mapHeight].type != 2:
            down = AI.map[cell.x][(cell.y + 1) % self.game.mapHeight]
        if AI.map[cell.x][(cell.y - 1) % self.game.mapHeight] != 0 \
                and AI.map[cell.x][(cell.y - 1) % self.game.mapHeight].type != 2:
            up = AI.map[cell.x][(cell.y - 1) % self.game.mapHeight]
        return [direction for direction in [up, down, right, left] if direction != []]

    def what_resource_is_required(self):
        pass

    def find_direction_from_cell(self, cell):
        current_x = self.game.ant.currentX
        current_y = self.game.ant.currentY
        if cell.x == (current_x - 1) % self.game.mapWidth and cell.y == current_y:
            return Direction.LEFT.value
        elif cell.x == (current_x + 1) % self.game.mapWidth and cell.y == current_y:
            return Direction.RIGHT.value
        elif cell.x == current_x and cell.y == (current_y - 1) % self.game.mapHeight:
            return Direction.UP.value
        elif cell.x == current_x and cell.y == (current_y + 1) % self.game.mapHeight:
            return Direction.DOWN.value

    def neighbour_with_cell_type(self, cell_type):
        return_list = list()
        for neighbour in self.neighbours:
            if neighbour.type == cell_type:
                return_list.append(neighbour)
        return return_list

    def manhattan_distance(self, source, dest):
        if abs(source.x - dest.x) > self.game.mapWidth / 2:
            res1 = self.game.mapWidth - abs(source.x - dest.x)
        else:
            res1 = abs(source.x - dest.x)
        if abs(source.y - dest.y) > self.game.mapHeight / 2:
            res2 = self.game.mapHeight - abs(source.y - dest.y)
        else:
            res2 = abs(source.y - dest.y)
        return res1 + res2
