from Model import *
import random
import json
from typing import *


class AI:
    def __init__(self):
        # Current Game State
        self.game: Game = None
        
        # Answer
        self.message: str = None
        self.direction: int = None
        self.value: int = None
        self.map = list()
        self.neighbours: list = list()
        self.type: str = ""
        self.init = True
        self.state = "explore"

    """
    Return a tuple with this form:
        (message: str, message_value: int, message_dirction: int)
    check example
    """
    
# java -jar server-v1.2.8.jar --run-manually

    def turn(self) -> (str, int, int):
        # initial the map
        if self.init:
            # print (self.game.baseX, self.game.baseY)
            self.map: list = [[0 for _ in range(self.game.mapHeight)] for _ in range(self.game.mapWidth)]
            self.init = False
        # update all neghbours
        self.update_neighbour()
        # update the map (that is not very correct just a view)
        self.update_map()
        # print ("4 neighbours:", self.adjacent_neighbour_finder_map(self.game.ant.getNeightbourCell(0,0)))
        if self.game.antType == 1:
            self.worker()

        elif self.game.antType == 0:
            self.soldier()
        # self.message = ""
        # self.value = random.randint(1, 10)
        # self.direction = random.choice(list(Direction)).value
        # self.direction = Direction.UP.value
        return self.message, self.value, self.direction

    def update_neighbour(self):
        self.neighbours = []
        for i in range(-1*self.game.viewDistance,self.game.viewDistance + 1):
            for j in range(-1*self.game.viewDistance, self.game.viewDistance + 1):
                if abs(i) + abs(j) <= self.game.viewDistance:
                    neighbour = self.game.ant.getNeightbourCell(i, j)
                    self.neighbours.append(neighbour)
                    neighbour.type
                    # self.neighbours.append({
                    #     'x': neighbour.x,
                    #     'y': neighbour.y,
                    #     'type': neighbour.type,
                    #     'rtype': neighbour.resource_type,
                    #     'rvalue': neighbour.resource_value,
                    #     'element': neighbour.ants
                    #     })

    def update_map(self):
        for neighbour in self.neighbours:
            self.map[neighbour.x][neighbour.y] = neighbour

    
    def worker(self):
        print("kargar")
        there_is_nothinge_around = True
        base_neighbour = self.neighbour_with_cell_type(CellType.BASE.value)
        # print(base_neighbour)
        if base_neighbour != []:
            # print ('base_x:{base_neghbour[0]['x']}'
            if base_neighbour[0].x != self.game.baseX and base_neighbour[0].y != self.game.baseY:
                self.message = f'I see the base at({base_neighbour[0].x},{base_neighbour[0].y})'
                print (self.message)
            # can see the base you have to report it with high priority ask for attack
        empty_neighbours = self.neighbour_with_cell_type(CellType.EMPTY.value)
        # print (empty_neighbours)
        if empty_neighbours != []: 
            required_resource = self.what_resource_is_required()
            for neighbour in empty_neighbours:
                if neighbour.resource_type == 0:
                    self.message = f'Bread({neighbour.resource_value}) at ({neighbour.x},{neighbour.y})'
                elif neighbour.resource_type == 1:
                    self.message = f'Grass({neighbour.resource_value}) at ({neighbour.x},{neighbour.y})'  
                
                print (self.message)
            self.message = f'i see a empty resource'
        if there_is_nothinge_around:
            self.random_walk()
        self.random_walk()
    def random_walk(self):
        self.direction = random.choice(list(Direction)).value

    def soldier(self):
        print("sarbaz")

    def find_shortest_path(self, source, dest):
        queue = [[source]]
        
        visited = set()
        while len(queue) != 0:
            path = queue.pop(0)
            front = path[-1]
            if front == dest:
                return path
            elif front not in visited:
                for adjacent__neighbour in self.adjacent__neighbour_finder_map(front):
                    newPath = list(path)
                    newPath.append(adjacent__neighbour)
                    queue.append(newPath)
                visited.add(front)
            return None
        
    

    def adjacent_neighbour_finder_map(self, cell):
        up = list()
        down = list()
        left = list()
        right = list()
        if self.map[cell.x+1][cell.y].type:
            down = self.map[cell.x+1][cell.y]
        if self.map[cell.x-1][cell.y].type:
            up = self.map[cell.x-1][cell.y]
        if self.map[cell.x][cell.y+1].type:
            right = self.map[cell.x][cell.y+1]
        if self.map[cell.x][cell.y-1].type:
            left = self.map[cell.x][cell.y-1]
        return [i for i in [up, down, right, left] if i!=[]]

    def what_resource_is_required(self):
        pass

    def neighbour_with_cell_type(self, cell_type):
        return_list = []
        for neighbour in self.neighbours:
            if neighbour.type == cell_type:
                return_list.append(neighbour)
        return return_list