from Model import *
import random


class AI:
    map: list = list()
    init: bool = True
    state: str = ""
    enemy_base: Cell = None

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
            AI.our_base = self.current_position()
            AI.init = False
        # update all neighbours
        self.update_neighbour()
        self.check_for_enemy_base()
        # update the map (that is not very correct just a view)
        self.update_map()
        if self.game.antType == 1:
            self.worker()
        elif self.game.antType == 0:
            self.soldier()
        return self.message, self.value, self.direction

    def check_for_enemy_base(self):
        if AI.enemy_base is None:
            for neighbour in self.neighbours:
                if neighbour.x != self.game.baseX and neighbour.y != self.game.baseY and neighbour.type == 0:
                    self.message = f'{neighbour.x} {neighbour.y}'
                    self.value = 2
                    AI.enemy_base = neighbour

    def update_neighbour(self):
        self.neighbours = list()
        for row_counter in range(-1 * self.game.viewDistance, self.game.viewDistance + 1):
            bound = self.game.viewDistance - abs(row_counter)
            for column_counter in range(-1 * bound, bound + 1):
                self.neighbours.append(self.game.ant.getNeightbourCell(row_counter, column_counter))

    def update_map(self):
        for neighbour in self.neighbours:
            AI.map[neighbour.x][neighbour.y] = neighbour

    def current_position(self):
        return self.game.ant.getNeightbourCell(0, 0)

    def worker(self):
        if self.game.ant.currentResource.value == 0:
            resource_cells = self.find_all_resources_with_distance()
            resource_cell = self.choose_best_neighbour(resource_cells)
            shortest_path = self.find_shortest_path(self.current_position(), resource_cell)
            if shortest_path:
                self.direction = self.find_direction_from_cell(shortest_path[1])
                there_is_nothing_around = False
            else:
                there_is_nothing_around = True
        else:
            shortest_path = self.find_shortest_path(self.current_position(),
                                                    AI.map[self.game.baseX][self.game.baseY])
            if shortest_path:
                self.direction = self.find_direction_from_cell(shortest_path[1])
                there_is_nothing_around = False
            else:
                there_is_nothing_around = True
        if there_is_nothing_around:
            self.random_walk()

    @staticmethod
    def choose_best_neighbour(cells):
        resource_cell = cells[0]
        for cell in cells:
            if cell[0].resource_type == 1 and resource_cell[0].resource_type != 1:
                resource_cell = cell
            elif cell[0].resource_type == 1 and cell[1] < resource_cell[1]:
                resource_cell = cell
            elif cell[0].resource_type == 0 and resource_cell[0].resource_type == 0 and cell[1] < resource_cell[1]:
                resource_cell = cell
        return resource_cell[0]

    def random_walk(self):
        neighbours = self.find_neighbours(self.current_position())
        random.shuffle(neighbours)
        index = random.randint(0, len(neighbours) - 1)
        self.direction = self.find_direction_from_cell(neighbours[index])

    def soldier(self):
        if AI.enemy_base is None:
            all_chats = self.game.chatBox.allChats
            if all_chats:
                enemy_base_coordinate = all_chats[0].text
                if enemy_base_coordinate != '':
                    # This part maybe has bug :))))
                    enemy_base_coordinate = enemy_base_coordinate.split()
                    x, y = self.current_position().x, self.current_position().y
                    relative_x = x - int(enemy_base_coordinate[0]) % self.game.mapWidth
                    relative_y = y - int(enemy_base_coordinate[1]) % self.game.mapHeight
                    AI.enemy_base = self.game.ant.getMapRelativeCell(-1 * relative_x, -1 * relative_y)
        if AI.enemy_base is None:
            self.random_walk()
        else:
            shortest_path = self.find_shortest_path(self.current_position(), AI.enemy_base)
            if shortest_path is None:
                best_neighbour = self.find_best_neighbour(AI.enemy_base)
                shortest_path = self.find_shortest_path(self.current_position(), best_neighbour)
            self.direction = self.find_direction_from_cell(shortest_path[1])

    def find_best_neighbour(self, cell):
        distance, destination = self.manhattan_distance(cell, self.neighbours[0]), self.neighbours[0]
        for neighbour in self.neighbours:
            if self.manhattan_distance(cell, neighbour) < distance:
                distance, destination = self.manhattan_distance(cell, neighbour), neighbour
        return destination

    def find_shortest_path(self, source, dest):
        queue = [[source]]
        visited = set()
        while len(queue) != 0:
            path = queue.pop(0)
            front = path[-1]
            if front == dest:
                return path
            elif front not in visited:
                for adjacent_neighbour in self.find_neighbours(front):
                    new_path = list(path)
                    new_path.append(adjacent_neighbour)
                    queue.append(new_path)
                visited.add(front)

    def find_all_resources_with_distance(self):
        result = list()
        for neighbour in self.neighbours:
            if neighbour.resource_type != 2 and self.manhattan_distance(
                    self.current_position(), neighbour) <= self.game.ant.viewDistance:
                result.append((neighbour, self.manhattan_distance(self.current_position(), neighbour)))
        return result

    def find_neighbours(self, cell):
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
            result1 = self.game.mapWidth - abs(source.x - dest.x)
        else:
            result1 = abs(source.x - dest.x)
        if abs(source.y - dest.y) > self.game.mapHeight / 2:
            result2 = self.game.mapHeight - abs(source.y - dest.y)
        else:
            result2 = abs(source.y - dest.y)
        return result1 + result2
