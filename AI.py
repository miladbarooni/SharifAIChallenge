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
        self.memory: list = list()
        self.neighbours: list = list()
        self.type: str = ""

    """
    Return a tuple with this form:
        (message: str, message_value: int, message_dirction: int)
    check example
    """
    
# java -jar server-v1.2.8.jar --run-manually

    def turn(self) -> (str, int, int):
        self.update_neighbour()
        print(self.game.mapHeight)
        print(self.game.mapWidth)
        if self.game.antType == 1:
            self.worker()
        elif self.game.antType == 0:
            self.soldier()
        self.message = ""
        self.value = random.randint(1, 10)
        self.direction = random.choice(list(Direction)).value
        # self.direction = Direction.UP.value
        return self.message, self.value, self.direction

    def worker(self):
        print("kargar")
        if (self.game.ant.currentResource.type != 2):
            self.go_to_cell(self.game.baseX, self.game.baseY)
        else:
            self.direction = random.choice(list(Direction)).value   
        print("---------------------------")

    def update_neighbour(self):
        self.neighbours = list()
        for i in range(-1*self.game.viewDistance,self.game.viewDistance + 1):
            for j in range(-1*self.game.viewDistance, self.game.viewDistance + 1):
                if abs(i) + abs(j) <= self.game.viewDistance:
                    neigbour = self.game.ant.getNeightbourCell(i, j)
                    self.neighbours.append({
                        'x': neigbour.x,
                        'y': neigbour.y,
                        'type': neigbour.type,
                        'rtype': neigbour.resource_type,
                        'rvalue': neigbour.resource_value
                        })
    
    def go_to_cell(self, x, y):
    
        print(self.game.ant.currentX.)
        print(self.neighbours)

    def soldier(self):
        print("sarbaz")
        print("---------------------------")