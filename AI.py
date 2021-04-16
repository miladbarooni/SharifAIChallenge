# java -jar server-v1.2.8.jar --run-manually

from Model import *
import random


class AI:
    def __init__(self):
        # Current Game State
        self.game: Game = None
        # Answer
        self.message: str = ''
        self.direction: int = 0
        self.value: int = 0
        self.map: list = list()
        self.neighbours: list = list()
        self.type: str = ""
        self.init: bool = True
        self.state: str = "explore"

    @staticmethod
    def manhattan_distance(source, dest):
        return abs(source.x - dest.x) + abs(source.y - dest.y)

    def turn(self) -> (str, int, int):
        # initial the map
        if self.init:
            print(self.game.baseX, self.game.baseY)
            self.map: list = [[0 for _ in range(self.game.mapHeight)] for _ in range(self.game.mapWidth)]
            self.init = False
        # update all neighbours
        self.update_neighbour()
        # update the map (that is not very correct just a view)
        self.update_map()
        if self.game.antType == 1:
            self.worker()
        elif self.game.antType == 0:
            self.soldier()
        return self.message, self.value, self.direction

    def update_neighbour(self):
        self.neighbours = list()
        for row_counter in range(-1 * self.game.viewDistance, self.game.viewDistance + 1):
            for column_counter in range(-1 * self.game.viewDistance, self.game.viewDistance + 1):
                if abs(row_counter) + abs(column_counter) <= self.game.viewDistance:
                    neighbour = self.game.ant.getNeightbourCell(row_counter, column_counter)
                    self.neighbours.append(neighbour)

    def update_map(self):
        for neighbour in self.neighbours:
            self.map[neighbour.x][neighbour.y] = neighbour

    def worker(self):
        print("Worker")
        there_is_nothing_around = True
        base_neighbour = self.neighbour_with_cell_type(CellType.BASE.value)
        if base_neighbour:
            if base_neighbour[0].x != self.game.baseX and base_neighbour[0].y != self.game.baseY:
                self.message = f'I see the enemy base at({base_neighbour[0].x}, {base_neighbour[0].y})'
                print(self.message)
            # can see the base you have to report it with high priority ask for attack
        empty_neighbours = self.neighbour_with_cell_type(CellType.EMPTY.value)
        if empty_neighbours:
            # required_resource = self.what_resource_is_required()
            required_resource = 1
            for neighbour in empty_neighbours:
                if neighbour.resource_type == 0:
                    self.message = f'Bread({neighbour.resource_value}) at ({neighbour.x}, {neighbour.y})'
                elif neighbour.resource_type == 1:
                    self.message = f'Grass({neighbour.resource_value}) at ({neighbour.x}, {neighbour.y})'
                print(self.message)
            resource_cell = self.find_nearest_resource(required_resource)
            print("nearest_resource:", resource_cell)
            shortest_path = self.find_shortest_path(self.game.ant.getNeightbourCell(0, 0), resource_cell)
            print("shortest path:", shortest_path)
        if there_is_nothing_around:
            self.random_walk()
        self.random_walk()

    def random_walk(self):
        self.direction = random.choice(list(Direction)).value

    def soldier(self):
        print(f"Soldier {self.message}")

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

    def find_nearest_resource(self, resource_type):
        best_dist = self.game.mapHeight + self.game.mapWidth + 1
        best_result = None
        for neighbour in self.neighbours:
            if neighbour.resource_type == resource_type and self.manhattan_distance(
                    self.game.ant.getNeightbourCell(0, 0), neighbour) < best_dist:
                best_result = neighbour
                best_dist = self.manhattan_distance(self.game.ant.getNeightbourCell(0, 0), neighbour)
        return best_result

    def adjacent_neighbour_finder_map(self, cell):
        up, down, left, right = list(), list(), list(), list()
        if self.map[cell.x + 1][cell.y].type:
            down = self.map[cell.x + 1][cell.y]
        if self.map[cell.x - 1][cell.y].type == 1:
            up = self.map[cell.x - 1][cell.y]
        if self.map[cell.x][cell.y + 1].type:
            right = self.map[cell.x][cell.y + 1]
        if self.map[cell.x][cell.y - 1].type:
            left = self.map[cell.x][cell.y - 1]
        return [direction for direction in [up, down, right, left] if direction != []]

    def what_resource_is_required(self):
        pass

    def neighbour_with_cell_type(self, cell_type):
        return_list = list()
        for neighbour in self.neighbours:
            if neighbour.type == cell_type:
                return_list.append(neighbour)
        return return_list
