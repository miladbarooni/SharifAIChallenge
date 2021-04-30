import math
from Model import *
import random


class AI:
    map: list = list()
    init: bool = True
    state: str = ''
    enemy_base: Cell = None
    resource_shortest_path: list = list()
    previous_move: Direction = None
    agent_history: set =  set()
    past_messages: list = list()
    played_turns: int = 0
    generated_scorpion: int = 0
    attacking_scorpion: int = 0
    is_attacking: bool = False
    purpose_cell: Cell = None
    explored_path: list = list()
    candidate_cell: set = set()
    time_spend_to_find = 0
    plan_path = list()
    another_plan_path = list()
    seen_candidate_cell = list()
    health : int 

    def __init__(self):
        self.game: Game = None
        self.message: str = ''
        self.direction: int = 0
        self.value: int = 0
        self.neighbours: list = list()
        self.type: str = ''
        self.chat_box: list = list()
        self.appended_state = ''
        self.ants = []

    def turn(self) -> (str, int, int):
        if AI.init:
            AI.map = [[0 for _ in range(self.game.mapHeight)] for _ in range(self.game.mapWidth)]
            AI.our_base = self.current_position()
            AI.init = False
            AI.enemy_base=None 
            if self.game.antType == 0:
                AI.state = 'defence'
                AI.health = self.game.healthSarbaaz
            if self.game.antType == 1:
                AI.health = self.game.healthKargar
        AI.explored_path.append((self.current_position().x, self.current_position().y))
        self.check_health()
        self.update_neighbour()
        self.check_for_enemy_base()
        self.read_chat_box()
        self.generate_messages_of_one_agent()
        self.update_map()
        if self.game.antType == 1:
            self.worker()
        elif self.game.antType == 0:
            self.soldier()
        self.message = self.generate_single_message()
        AI.played_turns += 1
        return self.message, self.value, self.direction
    def check_health(self):
        pass
        # if self.game.ant.health < AI.health:
        #     print ("i'm under Attack")
        #     self.agent_history.add((f'U{chr(self.current_position().x)}chr({self.current_position().y)}', 4))
    def check_for_enemy_base(self): 
        
        for neighbour in self.neighbours:
            # print (neighbour.type)
            if neighbour.type == 0 and (neighbour.x != self.game.baseX or neighbour.y != self.game.baseY):
                AI.agent_history.add((f'T{chr(neighbour.x)}{chr(neighbour.y)}', 5))
                AI.enemy_base = neighbour

    def update_neighbour(self):
        self.neighbours = list()
        for row_counter in range(-1 * self.game.viewDistance, self.game.viewDistance + 1):
            bound = self.game.viewDistance - abs(row_counter)
            for column_counter in range(-1 * bound, bound + 1):
                self.neighbours.append(self.game.ant.getNeightbourCell(row_counter, column_counter))
                self.ants.append(self.game.ant.getNeightbourCell(row_counter, column_counter).ants)

    def previous_turn(self):
        chats = self.game.chatBox.allChats
        if chats:
            previous_turn = chats[len(chats) - 1].turn
            return previous_turn
        return 0

    def update_map(self):
        type_dict = {'E': 1,'S': 4, 'T': 3 ,'W': 2, 'R': 1, 'G': 1, 'B': 0}
        resource_type_dict = {'R': 0, 'G': 1, 'W': 2, 'B': 2, 'S': 2, 'T':2, 'E':2}
        chat_box_list = list(self.chat_box)
        chat_box_list.sort(key=lambda x:x[1])
        # print (chat_box_list)
        for chat in chat_box_list:
            # if chat[0] == 'E':
            #     # print ("empty")
            #     print (x, y)
            # if chat[0] == 'W':
            #     print ("wall")
            x = ord(chat[0][1])
            y = ord(chat[0][2])
            # print (chat[0],x, y)
            cell_type = type_dict[chat[0][0]]
            resource_type = resource_type_dict[chat[0][0]]
            cell = Cell(x, y, cell_type, resource_type, 1)
            AI.map[x][y] = cell
            if cell.type == 0 and cell.x != self.game.baseX and cell.y != self.game.baseY:
                AI.enemy_base = cell
        for neighbour in self.neighbours:
            AI.map[neighbour.x][neighbour.y] = neighbour
        for chat in chat_box_list:
            if chat[0][0] == 'E':
                AI.map[ord(chat[0][1])][ord(chat[0][2])].resource_type = 2
            if chat[0][0] == 'B':
                AI.map[ord(chat[0][1])][ord(chat[0][2])].resource_type = 0
                AI.enemy_base = AI.map[ord(chat[0][1])][ord(chat[0][2])]

    def read_chat_box(self):
        self.chat_box = set()
        chats = self.game.chatBox.allChats
        for chat in chats:
            decode_until = len(chat.text)
            split_message = [chat.text[index:index + 3] for index in range(0, decode_until, 3)]
            for cell in split_message:
                self.chat_box.add((cell,chat.turn))

    def current_position(self):
        return self.game.ant.getNeightbourCell(0, 0)

    def worker(self):
        if len(AI.plan_path) >= 1:
            self.direction = self.find_direction_from_cell(AI.plan_path[0])
            AI.plan_path.pop(0)
            return
        if self.previous_turn() >= 100:
            shortest_path = self.find_shortest_path(self.current_position(), AI.map[self.game.baseX][self.game.baseY])
            self.direction = self.find_direction_from_cell (shortest_path[1])
            AI.plan_path = shortest_path[2:]
            if self.current_position().x == self.game.baseX and self.current_position().y == self.game.baseY:
                for neighbour in self.neighbours:
                    if neighbour.type == 1 and neighbour.resource_type != 2:
                        directions = self.find_shortest_path(self.current_position(), neighbour)
                        self.direction = self.find_direction_from_cell(directions[1]) 
                        AI.plan_path = directions[2:]
            return 
        
        if self.game.ant.currentResource.value != 0:
            AI.state = "carrying"
            shortest_path = self.find_shortest_path(self.current_position(),
                                                    AI.map[self.game.baseX][self.game.baseY])
            if shortest_path is None:
                AI.state = "not_carrying"
                shortest_path = self.find_shortest_path(self.current_position(), AI.map[self.game.baseX][self.game.baseY])
            self.direction = self.find_direction_from_cell(shortest_path[1])
            return
        AI.state = "not_carrying"
        all_resources_available = list()
        for row in AI.map:
            for cell in row:
                if cell != 0 and cell.type == 1 and cell.resource_type != 2:
                    this_path = self.find_shortest_path(self.current_position(), cell)
                    if this_path is not None:
                        all_resources_available.append(this_path)
        # print (len(all_resources_available))
        if len(all_resources_available) > 0:
            shortest_path = all_resources_available[0]
            for path in all_resources_available:
                if len(path) < len(shortest_path):
                    shortest_path = path
            self.direction = self.find_direction_from_cell(shortest_path[1])
            if len(shortest_path) > 2:
                AI.plan_path = shortest_path[2:]
            return
        else:
            AI.state = "not_carrying"
            if len(AI.another_plan_path) >=1 :
                self.direction = self.find_direction_from_cell(AI.another_plan_path[0])
                AI.another_plan_path.pop(0)
                return
            self.worker_explorer()

    def worker_explorer(self):
        self.find_candidate_cells()
        candidate_cell_list = list(AI.candidate_cell)
        candidate_cell_list.sort(key=lambda x: x[1])
        candidate_cell_list.reverse()
        cell = candidate_cell_list[0]
        shortest_path = self.find_shortest_path(self.current_position(), cell[0])
        if (len (shortest_path) != 1):
            self.direction = self.find_direction_from_cell(shortest_path[1])
            AI.another_plan_path = shortest_path[2:]
            return 
        else:
            self.random_walk()
    def find_candidate_cells(self):
        all_resources_available = list()
        for row in AI.map:
            for cell in row:
                if cell != 0 and cell.type == 1 and cell.resource_type != 2:
                    this_path = self.find_shortest_path(self.current_position(), cell)
                    if this_path is None:
                        all_resources_available.append(cell)
        for resource in all_resources_available:
            for row in AI.map:
                for cell in row:
                    if cell != 0 :
                        if (cell.type == 1 or cell.type==2) and self.manhattan_distance(cell, resource) <= 3:
                            if (cell.x, cell.y) not in AI.explored_path:
                            
                                # if cell not in [i[0] for i in AI.candidate_cell] and (
                                if self.find_shortest_path(self.current_position(), cell) is not None and (cell.x, cell.y) not in AI.seen_candidate_cell:
                                    AI.seen_candidate_cell.append((cell.x, cell.y))
                                    count_distance = self.manhattan_distance(resource, cell)
                                    AI.candidate_cell.add((cell, count_distance))
                            # else:
                            #     copy = set (AI.candidate_cell)
                            #     print (copy)
                            #     if (cell.x, cell.y) in AI.seen_candidate_cell:
                            #         for item in AI.candidate_cell:
                            #             if item[0].x == cell.x and item[0].y == cell.y:
                            #                 copy.remove(item)
                            #                 copy.add((item, item[1]-10))
                            #     AI.candidate_cell = set(copy)
                            #     print (copy)

                                
        for row in AI.map:
            for cell in row:
                if cell != 0:
                    if (cell.x, cell.y) not in AI.explored_path:
                        # if ((cell.x, cell.y) not in [(i[0].x, i[0].y) for i in AI.candidate_cell]) and (
                        #         cell.x, cell.y) not in AI.seen_candidate_cell:
                        if cell.type == 1:
                            if self.find_shortest_path(self.current_position(), cell) is not None and (cell.x, cell.y) not in AI.seen_candidate_cell:
                                count_distance = self.manhattan_distance(AI.map[self.game.baseX][self.game.baseY], cell)
                                count_distance2 = self.manhattan_distance(self.current_position(), cell) 
                                AI.candidate_cell.add((cell, count_distance+count_distance2+self.previous_turn()))
                                AI.seen_candidate_cell.append((cell.x, cell.y))
                    # else:
                        
                    #     copy = set (AI.candidate_cell)
                    #     if (cell.x, cell.y) in AI.seen_candidate_cell:
                    #         for item in AI.candidate_cell:
                    #             if item[0].x == cell.x and item[0].y == cell.y:
                    #                 copy.remove(item)
                    #                 copy.add((cell, item[1]-10))
                    #     AI.candidate_cell = set(copy)
                        # flag = False
                        # delete_cell = tuple()
                        # new_cell = tuple()
                        # for seen_cell in AI.candidate_cell:
                        #     if (seen_cell[0].x, seen_cell[0].y) == (cell.x, cell.y):
                        #         # can change it
                        #         delete_cell = seen_cell
                        #         new_cell = (seen_cell[0], seen_cell[1]-10)
                        #         flag = True
                        #         break
                        # if (flag):
                        #     AI.candidate_cell.remove(delete_cell)
                        #     AI.candidate_cell.add(new_cell)
        for candidate in AI.candidate_cell:
            for explored in AI.explored_path:
                if candidate[0].x == explored[0] and candidate[0].y == explored[1]:
                    candidate = (candidate[0], candidate[1] - 5)
            

    @staticmethod
    def reverse_direction(direction):
        direction = (direction + 2) % 4
        return direction if direction != 0 else 2

    def set_move_so_that_not_previous(self, directions):
        if len(directions) >= 2 and AI.previous_move == self.reverse_direction(directions[0]):
            if len(directions) != 1:
                AI.previous_move = self.direction = directions[1]
            else:
                AI.previous_move = self.direction = directions[0]

        elif len(directions) != 0:
            AI.previous_move = self.direction = directions[0]
        else:
            self.random_walk()

    def find_overall_direction_from_cell(self, cell):
        if abs(cell.x - self.current_position().x) >= self.game.mapWidth // 2:
            if cell.x < self.current_position().x:
                cell.x += self.game.mapWidth
            else:
                cell.x -= self.game.mapWidth
        if abs(cell.y - self.current_position().y) >= self.game.mapHeight // 2:
            if cell.y < self.current_position().y:
                cell.y += self.game.mapHeight
            else:
                cell.y -= self.game.mapHeight
        if cell.x > self.current_position().x and cell.y == self.current_position().y:
            return Direction.RIGHT.value, Direction.RIGHT.value
        if cell.x < self.current_position().x and cell.y == self.current_position().y:
            return Direction.LEFT.value, Direction.LEFT.value
        if cell.x == self.current_position().x and cell.y < self.current_position().y:
            return Direction.UP.value, Direction.UP.value
        if cell.x == self.current_position().x and cell.y > self.current_position().y:
            return Direction.DOWN.value, Direction.DOWN.value
        if cell.x > self.current_position().x and cell.y > self.current_position().y:
            return Direction.RIGHT.value, Direction.DOWN.value
        if cell.x > self.current_position().x and cell.y < self.current_position().y:
            return Direction.RIGHT.value, Direction.UP.value
        if cell.x < self.current_position().x and cell.y > self.current_position().y:
            return Direction.LEFT.value, Direction.DOWN.value
        if cell.x < self.current_position().x and cell.y < self.current_position().y:
            return Direction.LEFT.value, Direction.UP.value

    @staticmethod
    def remove_tuple_from_list(this_tuple, this_list, count):
        for item in this_tuple:
            for _ in range(count):
                if item in this_list:
                    this_list.remove(item)
        return this_list

    def you_are_going_crazy(self):
        if AI.explored_path[-1] == AI.explored_path[-3] and AI.explored_path[-2] == AI.explored_path[-4]:
            return True
        return False

    def explorer(self):
        probabilities = [counter for counter in range(1, 5) for _ in range(60)]
        adjacent_neighbours = self.find_neighbours(self.current_position())
        valid_neighbours = list(adjacent_neighbours)
        for neighbour in adjacent_neighbours:
            for coordinate in AI.explored_path:
                if coordinate[0] == neighbour.x and coordinate[1] == neighbour.y:
                    if neighbour in valid_neighbours:
                        valid_neighbours.remove(neighbour)
        if len(valid_neighbours) == 0:
            adjacent_neighbours = self.find_neighbours(self.current_position())
            valid_neighbours = list(adjacent_neighbours)
            if len(adjacent_neighbours) >= 2:
                for neighbour in adjacent_neighbours:
                    if len(AI.explored_path) >= 2 and neighbour.x == AI.explored_path[-2][0] and neighbour.y == \
                            AI.explored_path[-2][1]:
                        valid_neighbours.remove(neighbour)
        adjacent_neighbours_directions = [self.find_direction_from_cell(neighbour) for neighbour in valid_neighbours]
        probabilities = [probability for probability in probabilities if probability in adjacent_neighbours_directions]
        all_neighbours = [neighbour for neighbour in self.neighbours if
                          neighbour.x != self.current_position().x and neighbour.y != self.current_position().y]
        for neighbour in all_neighbours:
            if self.find_shortest_path(self.current_position(), neighbour) is None or neighbour.type == 2:
                count = self.manhattan_distance(self.current_position(), neighbour)
                probabilities = self.remove_tuple_from_list(self.find_overall_direction_from_cell(neighbour),
                                                            probabilities, count)
            for coordinate in AI.explored_path:
                if coordinate[0] == neighbour.x and coordinate[1] == neighbour.y:
                    count = self.manhattan_distance(self.current_position(), neighbour)
                    probabilities = self.remove_tuple_from_list(self.find_overall_direction_from_cell(neighbour),
                                                                probabilities, count)
        random.shuffle(probabilities)
        count = list()
        for i in range(1, 5):
            count.append(probabilities.count(i))
        if probabilities:
            for i in range(0, 4):
                if count[i] == max(count):
                    self.direction = i
        else:
            all_acceptable_cells = list()
            for row in AI.map:
                for cell in row:
                    if cell != 0 and cell.type != 2:
                        all_acceptable_cells.append(cell)
            valid_acceptable_cells = list(all_acceptable_cells)
            for cell in all_acceptable_cells:
                for coordinate in AI.explored_path:
                    if coordinate[0] == cell.x and coordinate[1] == cell.y:
                        if cell in valid_acceptable_cells:
                            valid_acceptable_cells.remove(cell)
            all_paths = list()
            for cell in valid_acceptable_cells:
                shortest_path = self.find_shortest_path(self.current_position(), cell)
                if shortest_path is not None:
                    all_paths.append(shortest_path)
            if all_paths:
                shortest_path = all_paths[0]
                for path in all_paths:
                    if len(shortest_path) > len(path):
                        shortest_path = path
                self.direction = self.find_direction_from_cell(shortest_path[1])
            else:
                adjacent_neighbours = self.find_neighbours(self.current_position())
                random.shuffle(adjacent_neighbours)
                self.direction = self.find_direction_from_cell(adjacent_neighbours[0])

    def soldier(self):
        for row in AI.map:
            for cell in row:
                if cell != 0 and cell.type == 0 and (cell.x != self.game.baseX or cell.y != self.game.baseY):
                    AI.enemy_base = cell
        if len(AI.another_plan_path) >=1 :
                self.direction = self.find_direction_from_cell(AI.another_plan_path[0])
                AI.another_plan_path.pop(0)
                return
        if self.previous_turn() <= 150:
            self.defence()
        else:
            
            if AI.enemy_base is None:
                self.soldier_explorer()
                
            else:
                self.attack()
    def soldier_explorer(self):
        self.find_candidate_cells_soldier()
        candidate_cell_list = list(AI.candidate_cell)
        candidate_cell_list.sort(key=lambda x: x[1])
        candidate_cell_list.reverse()
        cell = candidate_cell_list[0]
        shortest_path = self.find_shortest_path(self.current_position(), cell[0])
        if (len (shortest_path) != 1):
            self.direction = self.find_direction_from_cell(shortest_path[1])
            AI.another_plan_path = shortest_path[2:]
            return 
        else:
            self.random_walk()
    def find_candidate_cells_soldier(self):
        for row in AI.map:
            for cell in row:
                if cell != 0:
                    if (cell.x, cell.y) not in AI.explored_path:
                        # if ((cell.x, cell.y) not in [(i[0].x, i[0].y) for i in AI.candidate_cell]) and (
                        #         cell.x, cell.y) not in AI.seen_candidate_cell:
                        if cell.type == 1:
                            if self.find_shortest_path(self.current_position(), cell) is not None and (cell.x, cell.y) not in AI.seen_candidate_cell:
                                count_distance = self.manhattan_distance(AI.map[self.game.baseX][self.game.baseY], cell)
                                count_distance2 = self.manhattan_distance(self.current_position(), cell) 
                                AI.candidate_cell.add((cell, count_distance+count_distance2+(2 * self.previous_turn())))
                                AI.seen_candidate_cell.append((cell.x, cell.y))
        for candidate in AI.candidate_cell:
            for explored in AI.explored_path:
                if candidate[0].x == explored[0] and candidate[0].y == explored[1]:
                    candidate = (candidate[0], candidate[1] - 5) 
    
    def calculate_enemy_base(self, cell):
        basex = self.game.baseX
        basey = self.game.baseY
        # if basey < self.game.
    
    def defence(self):
        AI.state = 'defence'
        if self.previous_turn() is None:
            turn = 0 
        else:
            turn = (self.previous_turn() // 50 ) * 2
        if AI.plan_path:
            self.direction = self.find_direction_from_cell(AI.plan_path.pop(0))
            return
        all_accessible_cells = list()
        for row in AI.map:
            for cell in row:
                if cell != 0 and cell.type == 1 \
                        and self.manhattan_distance(cell, AI.map[self.game.baseX][self.game.baseY]) <= 4 + turn \
                        and self.manhattan_distance(self.current_position(), cell) >= 2 + turn \
                        and self.find_shortest_path(cell, self.current_position()) is not None:
                    all_accessible_cells.append(cell)
        random.shuffle(all_accessible_cells)
        path = self.find_shortest_path(self.current_position(), all_accessible_cells[0])
        while path is None or len(path) <= 1:
            random.shuffle(all_accessible_cells)
            path = self.find_shortest_path(self.current_position(), all_accessible_cells[0])
        self.direction = self.find_direction_from_cell(path[1])
        AI.plan_path = path[2:]
        return

    def attack(self):

        shortest_path = self.find_shortest_path(self.current_position(), AI.enemy_base)
        if shortest_path is None:
            best = math.inf
            best_cell = ''
            for row in AI.map:
                for cell in row:
                    if cell.type == 1 and self.manhattan_distance(cell, AI.enemy_base) < best \
                        and self.find_shortest_path(cell, self.current_position()) is not None:
                        best = self.manhattan_distance(cell, AI.enemy_base)
                        best_cell = cell
            shortest_path = self.find_shortest_path(self.current_position(), best_cell)
            self.direction = shortest_path[1]
            AI.plan_path = shortest_path[2:]
        else:
            self.direction = shortest_path[1]
            AI.plan_path = shortest_path[2:]


        self.direction = self.find_direction_from_cell(shortest_path[1])

    def find_best_neighbour(self, cell):
        distance, destination = math.inf, None
        for neighbour in self.neighbours:
            if self.manhattan_distance(cell, neighbour) < distance:
                if self.find_shortest_path(self.current_position(), neighbour) is not None:
                    distance, destination = self.manhattan_distance(cell, neighbour), neighbour
        return destination

    def find_shortest_path(self, source, dest):
        queue = [[source]]
        visited = set()
        counter = 0
        while len(queue) != 0:
            path = queue.pop(0)
            front = path[-1]
            if front.x == dest.x and front.y == dest.y:
                return path
            elif front not in visited:
                for adjacent_neighbour in self.find_neighbours(front):
                    new_path = list(path)
                    if adjacent_neighbour.type == 4:
                        if counter == 3:
                            counter = 0
                            new_path.append(adjacent_neighbour)
                            continue
                        else:
                            counter += 1
                    else:
                        new_path.append(adjacent_neighbour)
                    queue.append(new_path)
                visited.add(front)

    def find_neighbours(self, cell):
        if AI.state == "carrying":
            up, down, left, right = list(), list(), list(), list()
            if AI.map[(cell.x + 1) % self.game.mapWidth][cell.y] != 0 \
                    and AI.map[(cell.x + 1) % self.game.mapWidth][cell.y].type != 2 \
                    and AI.map[(cell.x + 1) % self.game.mapWidth][cell.y].type != 3:
                right = AI.map[(cell.x + 1) % self.game.mapWidth][cell.y]
            if AI.map[(cell.x - 1) % self.game.mapWidth][cell.y] != 0 \
                    and AI.map[(cell.x - 1) % self.game.mapWidth][cell.y].type != 2 \
                    and AI.map[(cell.x - 1) % self.game.mapWidth][cell.y].type != 3:
                left = AI.map[(cell.x - 1) % self.game.mapWidth][cell.y]
            if AI.map[cell.x][(cell.y + 1) % self.game.mapHeight] != 0 \
                    and AI.map[cell.x][(cell.y + 1) % self.game.mapHeight].type != 2 \
                    and AI.map[cell.x][(cell.y + 1) % self.game.mapHeight].type != 3:
                down = AI.map[cell.x][(cell.y + 1) % self.game.mapHeight]
            if AI.map[cell.x][(cell.y - 1) % self.game.mapHeight] != 0 \
                    and AI.map[cell.x][(cell.y - 1) % self.game.mapHeight].type != 2 \
                    and AI.map[cell.x][(cell.y - 1) % self.game.mapHeight].type != 3:
                up = AI.map[cell.x][(cell.y - 1) % self.game.mapHeight]
            return [direction for direction in [up, down, right, left] if direction != []]
        else:
            up, down, left, right = list(), list(), list(), list()
            if AI.map[(cell.x + 1) % self.game.mapWidth][cell.y] != 0 \
                    and AI.map[(cell.x + 1) % self.game.mapWidth][cell.y].type != 2:                right = AI.map[(cell.x + 1) % self.game.mapWidth][cell.y]
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

    def generate_single_message(self):
        return_message = ''
        list_message_history = list(AI.agent_history)
        list_message_history.sort(key=lambda item: item[1])
        list_message_history.reverse()
        value = 0
        for message in list_message_history:
            if len(return_message) == 30:
                break
            if message not in AI.past_messages and message not in self.chat_box:
                return_message += message[0]
                if message[1] >= value:
                    value = message[1]
                AI.past_messages.append(message)
        self.value = value
        # print (return_message)
        return return_message

    def generate_messages_of_one_agent(self):

        
        for neighbour in self.neighbours:
            if neighbour.type == 1 and (neighbour.resource_type == 0 or neighbour.resource_type == 1):
                if neighbour.resource_type == 0:
                    AI.agent_history.add(
                        (f'R{chr(neighbour.x)}{chr(neighbour.y)}', 4))
                elif neighbour.resource_type == 1:
                    AI.agent_history.add(
                        (f'G{chr(neighbour.x)}{chr(neighbour.y)}', 4))
            elif neighbour.type == 1 and neighbour.resource_type == 2:
                if AI.map[neighbour.x][neighbour.y] != 0:
                    if AI.map[neighbour.x][neighbour.y].resource_type != 2 and AI.map[neighbour.x][neighbour.y].type == 1:
                        AI.agent_history.add((f'E{chr(neighbour.x)}{chr(neighbour.y)}', 5))
            elif neighbour.type == 2:
                AI.agent_history.add(
                    (f'W{chr(neighbour.x)}{chr(neighbour.y)}', 2))
            elif neighbour.type == 3:
                AI.agent_history.add(
                    (f'T{chr(neighbour.x)}{chr(neighbour.y)}', 2))
            elif neighbour.type == 4:
                AI.agent_history.add(
                    (f'S{chr(neighbour.x)}{chr(neighbour.y)}', 2))
    def random_walk(self):
        neighbours = self.find_neighbours(self.current_position())
        random.shuffle(neighbours)
        directions = list()
        for neighbour in neighbours:
            directions.append(self.find_direction_from_cell(neighbour))
        self.set_move_so_that_not_previous(directions)
