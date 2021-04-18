from Model import *
import random
import json
from typing import *

class AI:
    map = list()
    init = True
    state = ""
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
            AI.map: list = [[0 for _ in range(self.game.mapHeight)] for _ in range(self.game.mapWidth)]
            AI.init = False
        # update all neighbours
        self.update_neighbour()
        # update the map (that is not very correct just a view)
        self.update_map()
        if self.game.antType == 1:
            self.worker()
        elif self.game.antType == 0:
            self.soldier()
        self.message = ""
        self.value = 1
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
            AI.map[neighbour.x][neighbour.y] = neighbour

    def worker(self):
        print("Worker")
        there_is_nothing_around = True
        base_neighbour = self.neighbour_with_cell_type(CellType.BASE.value)
        if base_neighbour:
            if base_neighbour[0].x != self.game.baseX and base_neighbour[0].y != self.game.baseY:
                self.message = f'base at({base_neighbour[0].x}, {base_neighbour[0].y})'
                # print(self.message)
            # can see the base you have to report it with high priority ask for attack
        
        # empty_neighbours = self.neighbour_with_cell_type(CellType.EMPTY.value)
        # if empty_neighbours:
            # required_resource = self.what_resource_is_required()
            # required_resource = 1
            # for neighbour in empty_neighbours:
                # if neighbour.resource_type == 0:
                #     self.message = f'Bread({neighbour.resource_value}) at ({neighbour.x}, {neighbour.y})'
                # elif neighbour.resource_type == 1:
                #     self.message = f'Grass({neighbour.resource_value}) at ({neighbour.x}, {neighbour.y})'
                # print(self.message)
        resource_cell = self.find_nearest_resource()
        print("nearest_resource:", resource_cell)
        first_node_shortest_path = self.find_shortest_path(self.game.ant.getNeightbourCell(0, 0), resource_cell)
        print (first_node_shortest_path)
        first_cell_to_go = first_node_shortest_path[-1]
        self.direction = self.find_direction_from_cell(first_cell_to_go)
        there_is_nothing_around = False
        if self.game.ant.currentResource == 5:
            first_node_shortest_path = self.find_shortest_path(self.game.ant.getNeightbourCell(0,0), AI.map[self.game.baseX][self.game.baseY])
            self.direction = self.find_direction_from_cell(first_node_shortest_path)
        if there_is_nothing_around:
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

    def find_nearest_resource(self):
        best_dist = self.game.mapHeight + self.game.mapWidth + 1
        best_result = None
        for neighbour in self.neighbours:
            if neighbour.resource_type != 2 and self.manhattan_distance(
                    self.game.ant.getNeightbourCell(0, 0), neighbour) < best_dist:
                best_result = neighbour
                best_dist = self.manhattan_distance(self.game.ant.getNeightbourCell(0, 0), neighbour)
        return best_result

    def adjacent_neighbour_finder_map(self, cell):
        up, down, left, right = list(), list(), list(), list()
        if AI.map[(cell.x + 1) % self.game.mapWidth][cell.y].type:
            right = AI.map[(cell.x + 1) % self.game.mapWidth][cell.y]
        if AI.map[(cell.x - 1) % self.game.mapWidth][cell.y].type:
            left = AI.map[(cell.x - 1) % self.game.mapWidth][cell.y]
        if AI.map[cell.x][(cell.y + 1) % self.game.mapHeight].type:
            down = AI.map[cell.x][(cell.y + 1)%self.game.mapHeight]
        if AI.map[cell.x][(cell.y - 1)%self.game.mapHeight].type:
            up = AI.map[cell.x][(cell.y - 1) % self.game.mapHeight]
        return [direction for direction in [up, down, right, left] if direction != []]

    def what_resource_is_required(self):
        pass
    
    def find_direction_from_cell(self, cell):
        current_x = self.game.ant.currentX
        current_y = self.game.ant.currentY
        if cell.x == current_x - 1 and cell.y == current_y:
            return Direction.UP.value
        elif cell.x == current_x +1 and cell.y == current_y:
            return Direction.DOWN.value
        elif cell.x == current_x and cell.y == current_y - 1:
            return Direction.LEFT.value
        elif cell.x == current_x and cell.y == current_y + 1:
            return Direction.RIGHT.value
        
    def neighbour_with_cell_type(self, cell_type):
        return_list = list()
        for neighbour in self.neighbours:
            if neighbour.type == cell_type:
                return_list.append(neighbour)
        return return_list

    
    def manhattan_distance(self, source, dest):
        return abs(source.x - dest.x) + abs(source.y - dest.y)
