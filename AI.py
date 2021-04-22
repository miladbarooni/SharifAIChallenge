import math

from Model import *
import random


class AI:
    map: list = list()
    init: bool = True
    state: str = ""
    enemy_base: Cell = None
    resource_shortest_path: list = list()
    previous_move: Direction = None
    agent_history: set = set()
    past_messages: list = list()
    played_turns: int = 0
    generated_scorpion: int = 0
    attacking_scorpion: int = 0
    is_attacking: bool = False
    purpose_cell: Cell = None
    explored_path: list = list()

    def __init__(self):
        # Current Game State
        self.game: Game = None
        # Answer
        self.message: str = ''
        self.direction: int = 0
        self.value: int = 0
        self.neighbours: list = list()
        self.type: str = ""
        self.chat_box: list = list()
        self.appended_state = ''

    def turn(self) -> (str, int, int):
        # initial the map
        if AI.init:
            AI.map = [[0 for _ in range(self.game.mapHeight)] for _ in range(self.game.mapWidth)]
            AI.our_base = self.current_position()
            AI.init = False
        # update all neighbours
        AI.explored_path.append((self.current_position().x, self.current_position().y))
        self.update_neighbour()
        self.read_chat_box()
        self.check_for_enemy_base()
        self.generate_messages_of_one_agent()
        self.update_map()
        if self.game.antType == 1:
            self.worker()
        elif self.game.antType == 0:
            self.soldier()
        self.message = self.generate_single_message()
        AI.played_turns += 1
        return self.message, self.value, self.direction

    def check_for_enemy_base(self):
        if AI.enemy_base is None:
            for neighbour in self.neighbours:
                if neighbour.x != self.game.baseX and neighbour.y != self.game.baseY and neighbour.type == 0:
                    AI.agent_history.add((f'B{"{0:0=2d}".format(neighbour.x)}{"{0:0=2d}".format(neighbour.y)}', 3))
                    AI.enemy_base = neighbour

    def update_neighbour(self):
        self.neighbours = list()
        for row_counter in range(-1 * self.game.viewDistance, self.game.viewDistance + 1):
            bound = self.game.viewDistance - abs(row_counter)
            for column_counter in range(-1 * bound, bound + 1):
                self.neighbours.append(self.game.ant.getNeightbourCell(row_counter, column_counter))

    def previous_turn(self):
        chats = self.game.chatBox.allChats
        if chats:
            previous_turn = chats[len(chats) - 1].turn
            return previous_turn
        return 0

    def update_map(self):
        type_dict = {'W': 2, 'R': 1, 'G': 1, 'B': 0}
        resource_type_dict = {'R': 0, 'G': 1, 'W': 2, 'B': 2}
        AI.scorpion_count = 0
        for chat in self.chat_box:
            if len(chat) == 1:
                continue
            x = int(chat[1:3])
            y = int(chat[3:])
            cell_type = type_dict[chat[0]]
            resource_type = resource_type_dict[chat[0]]
            cell = Cell(x, y, cell_type, resource_type, 1)
            AI.map[x][y] = cell
            if cell.type == 0 and cell.x != self.game.baseX and cell.y != self.game.baseY:
                AI.enemy_base = cell
        for neighbour in self.neighbours:
            AI.map[neighbour.x][neighbour.y] = neighbour

    def read_chat_box(self):
        AI.generated_scorpion = 0
        self.chat_box = list()
        chats = self.game.chatBox.allChats
        for chat in chats:
            decode_until = len(chat.text)
            if decode_until % 5 != 0:
                appended_state = chat.text[-1]
                chat.text = chat.text[0:-1]
                if appended_state == 'G':
                    AI.generated_scorpion += 1
                self.chat_box.append(appended_state)
            split_message = [chat.text[index:index + 5] for index in range(0, decode_until - 1, 5)]
            split_message = [message for message in split_message if message != '']
            split_message = split_message[:len(split_message) - 1]
            for cell in split_message:
                self.chat_box.append(cell)

    def current_position(self):
        return self.game.ant.getNeightbourCell(0, 0)

    def path_to_best_resource_cell(self, resource_cells):
        resource_cell = self.choose_best_resource(resource_cells)
        AI.purpose_cell = resource_cell
        shortest_path = self.find_shortest_path(self.current_position(), resource_cell)
        if shortest_path is None:
            best_resource = self.find_best_neighbour(resource_cell)
            shortest_path = self.find_shortest_path(self.current_position(), best_resource)
        if shortest_path is None:
            best_resource = self.find_best_neighbour_greedy(resource_cell)
            shortest_path = self.find_shortest_path(self.current_position(), best_resource)
        if len(shortest_path) > 2:
            AI.resource_shortest_path = shortest_path[2:]
        else:
            AI.resource_shortest_path = []
        return shortest_path

    def find_best_neighbour_greedy(self, resource_cell):
        neighbours = self.find_neighbours(self.current_position())
        distance = self.manhattan_distance(self.current_position(), resource_cell)
        result_cell = resource_cell
        for neighbour in neighbours:
            if self.manhattan_distance(self.current_position(), neighbour) < distance:
                result_cell = neighbour
                distance = self.manhattan_distance(self.current_position(), neighbour)
        return result_cell

    def worker(self):
        shortest_path = None
        if self.game.ant.currentResource.value != 0:
            shortest_path = self.find_shortest_path(self.current_position(),
                                                    AI.map[self.game.baseX][self.game.baseY])
            self.direction = self.find_direction_from_cell(shortest_path[1])
            return
        if self.game.ant.currentResource.value == 0 and AI.resource_shortest_path != []:
            self.direction = self.find_direction_from_cell(AI.resource_shortest_path[0])
            AI.resource_shortest_path.pop(0)
            return
        if self.game.ant.currentResource.value == 0 and AI.resource_shortest_path == []:
            resource_cells = self.find_all_resources_with_distance()
            if resource_cells:
                shortest_path = self.path_to_best_resource_cell(resource_cells)
            if shortest_path is None:
                all_resources_in_agent_map = []
                for row in AI.map:
                    for cell in row:
                        if cell != 0 and cell.type == 1 and cell.resource_type != 2:
                            all_resources_in_agent_map.append(
                                (cell, self.manhattan_distance(self.current_position(), cell)))
                if all_resources_in_agent_map:
                    shortest_path = self.path_to_best_resource_cell(all_resources_in_agent_map)
            if shortest_path:
                self.direction = self.find_direction_from_cell(shortest_path[1])
                return
        self.explorer()

    @staticmethod
    def reverse_direction(direction):
        direction = (direction + 2) % 4
        return direction if direction != 0 else 2

    def make_direction(self, allowed_directions, current_direction, less, more):
        result = list()
        if current_direction in allowed_directions:
            for _ in range(more):
                result.append(current_direction)
        if current_direction in allowed_directions:
            for _ in range(less):
                result.append(self.reverse_direction(current_direction))
        return result

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

    def remove_tuple_from_list(self, this_tuple, this_list):
        for item in this_tuple:
            if item in this_list:
                this_list.remove(item)
        return this_list

    def explorer(self):
        probabilities = [counter for counter in range(1, 5) for _ in range(20)]
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
            if len(adjacent_neighbours) == 2:
                for neighbour in adjacent_neighbours:
                    if len(AI.explored_path) >= 2 and neighbour.x == AI.explored_path[-2][0] and neighbour.y == AI.explored_path[-2][1]:
                        valid_neighbours.remove(neighbour)
        adjacent_neighbours_directions = [self.find_direction_from_cell(neighbour) for neighbour in valid_neighbours]
        probabilities = [probability for probability in probabilities if probability in adjacent_neighbours_directions]
        all_neighbours = [neighbour for neighbour in self.neighbours if
                          neighbour.x != self.current_position().x and neighbour.y != self.current_position().y]
        for neighbour in all_neighbours:
            if (neighbour.x, neighbour.y) in AI.explored_path or neighbour.type == 2 or self.find_shortest_path(
                    self.current_position(), neighbour) is None:
                probabilities = self.remove_tuple_from_list(self.find_overall_direction_from_cell(neighbour),
                                                            probabilities)
        random.shuffle(probabilities)
        self.direction = probabilities[0]

    def choose_best_resource(self, cells):
        resource_cell = cells[0]
        if self.previous_turn() <= 10:
            for cell in cells:
                if cell[0].resource_type == 0 and resource_cell[0].resource_type == 1:
                    resource_cell = cell
                elif cell[0].resource_type == 0 and resource_cell[0].resource_type == 0 and cell[1] < resource_cell[1]:
                    resource_cell = cell
                elif cell[0].resource_type == 1 and resource_cell[0].resource_type == 1 and cell[1] < resource_cell[1]:
                    resource_cell = cell
        else:
            for cell in cells:
                if cell[0].resource_type == 1 and resource_cell[0].resource_type == 0:
                    resource_cell = cell
                elif cell[0].resource_type == 1 and resource_cell[0].resource_type == 1 and cell[1] < resource_cell[1]:
                    resource_cell = cell
                elif cell[0].resource_type == 0 and resource_cell[0].resource_type == 0 and cell[1] < resource_cell[1]:
                    resource_cell = cell
        return resource_cell[0]

    def soldier(self):
        if AI.state == "Attack" and AI.enemy_base is None:
            self.explorer()
            self.appended_state = 'A'
            return
        if AI.state == "Attack":
            self.attack()
            self.appended_state = 'A'
            return
        if AI.generated_scorpion - AI.attacking_scorpion < 4:
            self.direction = Direction.CENTER.value
        elif AI.generated_scorpion - AI.attacking_scorpion >= 4 and AI.enemy_base is not None:
            self.appended_state = 'A'
            AI.state = "Attack"
            AI.attacking_scorpion += 1
            self.attack()
        elif AI.generated_scorpion - AI.attacking_scorpion >= 4 and AI.enemy_base is None:
            self.appended_state = 'A'
            AI.state = "Attack"
            AI.attacking_scorpion += 1
            self.explorer()

    def attack(self):
        shortest_path = self.find_shortest_path(self.current_position(), AI.enemy_base)
        if shortest_path is None:
            best_neighbour = self.find_best_neighbour(AI.enemy_base)
            shortest_path = self.find_shortest_path(self.current_position(), best_neighbour)
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
        while len(queue) != 0:
            path = queue.pop(0)
            front = path[-1]
            if front.x == dest.x and front.y == dest.y:
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

    def generate_single_message(self):
        if AI.played_turns == 0 and self.game.antType == 0:
            AI.generated_scorpion += 1
            self.value = 4
            self.appended_state = 'G'
        return_message = str()
        wall_message = list()
        resource_message = list()
        for message in AI.agent_history:
            if message not in AI.past_messages and message not in self.chat_box:
                if message[1] == 3:
                    if self.value != 4:
                        self.value = 3
                    return_message += message[0]
                    AI.past_messages.append(message)
                elif message[1] == 2:
                    if self.value != 3 and self.value != 4:
                        self.value = 2
                    wall_message.append(message)
                elif message[1] == 1:
                    if self.value != 2 and self.value != 3 and self.value != 4:
                        self.value = 1
                    resource_message.append(message)
        while len(return_message) <= 25:
            if len(wall_message) == 0 and len(resource_message) == 0:
                break
            if len(resource_message) > 0:
                random.shuffle(resource_message)
                return_message += resource_message[0][0]
                AI.past_messages.append(resource_message[0])
                resource_message = resource_message[1:]
            if len(wall_message) > 0 and len(resource_message) == 0:
                random.shuffle(wall_message)
                return_message += wall_message[0][0]
                AI.past_messages.append(wall_message[0])
                wall_message = wall_message[1:]

        return_message += self.appended_state
        return return_message

    def generate_messages_of_one_agent(self):
        for neighbour in self.neighbours:
            if neighbour.type == 1 and neighbour.resource_type != 2:
                if neighbour.resource_type == 0:
                    AI.agent_history.add(
                        (f'R{"{0:0=2d}".format(neighbour.x)}{"{0:0=2d}".format(neighbour.y)}', 2))
                elif neighbour.resource_type == 1:
                    AI.agent_history.add(
                        (f'G{"{0:0=2d}".format(neighbour.x)}{"{0:0=2d}".format(neighbour.y)}', 2))
            elif neighbour.type == 2:
                AI.agent_history.add(
                    (f'W{"{0:0=2d}".format(neighbour.x)}{"{0:0=2d}".format(neighbour.y)}', 1))

    def random_walk(self):
        neighbours = self.find_neighbours(self.current_position())
        random.shuffle(neighbours)
        directions = []
        for neighbour in neighbours:
            directions.append(self.find_direction_from_cell(neighbour))
        self.set_move_so_that_not_previous(directions)

    # def agent_count(self):
    #     chats = self.game.chatBox.allChats
    #     self.previous_ant_count = 0
    #     self.previous_scorpion_count = 0
    #     last_turn = self.previous_turn()
    #     for chat in chats:
    #         if chat.turn == last_turn:
    #             split_message = [chat.text[index:index + 5] for index in range(0, 30, 5)]
    #             split_message = [message for message in split_message if message != '']
    #             agent_type = split_message[len(split_message) - 1]
    #             if agent_type == '1':
    #                 self.previous_ant_count += 1
    #             else:
    #                 self.previous_scorpion_count += 1
    #     if self.game.antType == 0:
    #         if AI.played_turns == 0 or last_turn == 0:
    #             return self.previous_scorpion_count + 1, self.previous_ant_count
    #     else:
    #         if AI.played_turns == 0 or last_turn == 0:
    #             return self.previous_scorpion_count, self.previous_ant_count + 1
    #     return self.previous_scorpion_count, self.previous_ant_count
