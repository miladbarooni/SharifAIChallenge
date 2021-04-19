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

    def turn(self) -> (str, int, int):
        # initial the map
        if AI.init:
            AI.map = [[0 for _ in range(self.game.mapHeight)] for _ in range(self.game.mapWidth)]
            AI.our_base = self.current_position()
            AI.init = False
        # update all neighbours
        self.update_neighbour()
        self.read_chat_box()
        self.check_for_enemy_base()
        self.generate_messages_of_one_agent()
        self.message = self.generate_single_message()
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
                    AI.agent_history.add((f'B{"{0:0=2d}".format(neighbour.x)}{"{0:0=2d}".format(neighbour.y)}', 3))
                    AI.enemy_base = neighbour

    def update_neighbour(self):
        self.neighbours = list()
        for row_counter in range(-1 * self.game.viewDistance, self.game.viewDistance + 1):
            bound = self.game.viewDistance - abs(row_counter)
            for column_counter in range(-1 * bound, bound + 1):
                self.neighbours.append(self.game.ant.getNeightbourCell(row_counter, column_counter))

    def update_map(self):
        type_dict = {'W': 2, 'R': 1, 'G': 1, 'B': 0}
        resource_type_dict = {'R': 0, 'G': 1, 'W': 2, 'B': 2}
        for chat in self.chat_box:
            x = int(chat[1:3])
            y = int(chat[3:])
            cell_type = type_dict[chat[0]]
            resource_type = resource_type_dict[chat[0]]
            cell = Cell(x, y, cell_type, resource_type, 1)
            AI.map[x][y] = cell
        for neighbour in self.neighbours:
            AI.map[neighbour.x][neighbour.y] = neighbour

    def read_chat_box(self):
        self.chat_box = list()
        chats = self.game.chatBox.allChats
        for chat in chats:
            split_message = [chat.text[index:index + 5] for index in range(0, 30, 5)]
            split_message = [message for message in split_message if message != '']
            for cell in split_message:
                self.chat_box.append(cell)

    def current_position(self):
        return self.game.ant.getNeightbourCell(0, 0)

    def worker(self):
        there_is_nothing_around = False
        if self.game.ant.currentResource.value != 0:
            shortest_path = self.find_shortest_path(self.current_position(),
                                                    AI.map[self.game.baseX][self.game.baseY])
            if shortest_path:
                self.direction = self.find_direction_from_cell(shortest_path[1])
                there_is_nothing_around = False
            else:
                there_is_nothing_around = True
        if self.game.ant.currentResource.value == 0 and AI.resource_shortest_path == []:
            resource_cells = self.find_all_resources_with_distance()
            if resource_cells:
                resource_cell = self.choose_best_resource(resource_cells)
                shortest_path = self.find_shortest_path(self.current_position(), resource_cell)
                if shortest_path is None:
                    best_resource = self.find_best_neighbour(resource_cell)
                    shortest_path = self.find_shortest_path(self.current_position(), best_resource)
                AI.resource_shortest_path = shortest_path[1:]
            else:
                shortest_path = None
                all_resources_in_agent_map = []
                for row in AI.map:
                    for cell in row:
                        if cell != 0 and cell.resource_type != 2:
                            all_resources_in_agent_map.append(
                                (cell, self.manhattan_distance(self.current_position(), cell)))
                if all_resources_in_agent_map:
                    best_resource = self.choose_best_resource(all_resources_in_agent_map)
                    shortest_path = self.find_shortest_path(self.current_position(), best_resource)
                    if shortest_path is None:
                        best_resource = self.find_best_neighbour(best_resource)
                        shortest_path = self.find_shortest_path(self.current_position(), best_resource)
                    self.direction = self.find_direction_from_cell(shortest_path[1])
            if shortest_path:
                self.direction = self.find_direction_from_cell(shortest_path[1])
                there_is_nothing_around = False
            else:
                there_is_nothing_around = True
        elif self.game.ant.currentResource.value == 0 and AI.resource_shortest_path != []:
            self.direction = self.find_direction_from_cell(AI.resource_shortest_path[0])
            AI.resource_shortest_path.pop(0)
            there_is_nothing_around = False
        if there_is_nothing_around:
            self.random_walk()

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
        if len(directions) and AI.previous_move == directions[0]:
            if len(directions) != 1:
                AI.previous_move = self.direction = directions[1]
            else:
                AI.previous_move = self.direction = directions[0]
        else:
            AI.previous_move = self.direction = directions[0]

    def explorer(self):
        x, y = self.game.baseX, self.game.baseY
        directions = list()
        allowed_directions = list()
        neighbours = self.find_neighbours(self.current_position())
        for neighbour in neighbours:
            allowed_directions.append(self.find_direction_from_cell(neighbour))
        if x > self.game.mapWidth / 2:
            directions += self.make_direction(allowed_directions, Direction.LEFT.value, 1, 5)
        else:
            directions += self.make_direction(allowed_directions, Direction.RIGHT.value, 1, 5)
        if y > self.game.mapHeight / 2:
            directions += self.make_direction(allowed_directions, Direction.UP.value, 1, 5)
        else:
            directions += self.make_direction(allowed_directions, Direction.DOWN.value, 1, 5)
        random.shuffle(directions)
        self.set_move_so_that_not_previous(directions)

    @staticmethod
    def choose_best_resource(cells):
        resource_cell = cells[0]
        for cell in cells:
            if cell[0].resource_type == 1 and resource_cell[0].resource_type == 0:
                resource_cell = cell
            elif cell[0].resource_type == 1 and resource_cell[0].resource_type == 1 and cell[1] < resource_cell[1]:
                resource_cell = cell
            elif cell[0].resource_type == 0 and resource_cell[0].resource_type == 0 and cell[1] < resource_cell[1]:
                resource_cell = cell
        return resource_cell[0]

    def random_walk(self):
        neighbours = self.find_neighbours(self.current_position())
        random.shuffle(neighbours)
        directions = []
        for neighbour in neighbours:
            directions.append(self.find_direction_from_cell(neighbour))
        self.set_move_so_that_not_previous(directions)

    def soldier(self):
        # if AI.enemy_base is None:
        #     all_chats = self.game.chatBox.allChats
        #     for chat in all_chats:
        #         enemy_base_coordinate = chat.text
        #         if enemy_base_coordinate != '':
        #             enemy_base_coordinate = enemy_base_coordinate.split()
        #             x, y = self.current_position().x, self.current_position().y
        #             relative_x = x - int(enemy_base_coordinate[0]) % self.game.mapWidth
        #             relative_y = y - int(enemy_base_coordinate[1]) % self.game.mapHeight
        #             AI.enemy_base = self.game.ant.getMapRelativeCell(-1 * relative_x, -1 * relative_y)
        #             print(f'{AI.enemy_base.x}, {AI.enemy_base.y}')
        if AI.enemy_base is None:
            self.explorer()
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
        return_message = str()
        wall_message = list()
        resource_message = list()
        for message in AI.agent_history:
            if message not in AI.past_messages:
                if message[1] == 3:
                    self.value = 3
                    return_message += message[0]
                    AI.past_messages.append(message)
                elif message[1] == 2:
                    if self.value != 3:
                        self.value = 2
                    wall_message.append(message)
                elif message[1] == 1:
                    if self.value != 2 and self.value != 3:
                        self.value = 1
                    resource_message.append(message)
        while len(return_message) <= 30:
            if len(wall_message) == 0 and len(resource_message) == 0:
                break
            if len(wall_message) > 0:
                random.shuffle(wall_message)
                return_message += wall_message[0][0]
                AI.past_messages.append(wall_message[0])
                wall_message = wall_message[1:]
            if len(resource_message) > 0 and len(wall_message) == 0:
                random.shuffle(resource_message)
                return_message += resource_message[0][0]
                AI.past_messages.append(resource_message[0])
                resource_message = resource_message[1:]
        return return_message

    def generate_messages_of_one_agent(self):
        for neighbour in self.neighbours:
            if neighbour.type == 2:
                AI.agent_history.add((f'W{"{0:0=2d}".format(neighbour.x)}{"{0:0=2d}".format(neighbour.y)}', 2))
            elif neighbour.type == 1 and neighbour.resource_type != 2:
                if neighbour.resource_type == 0:
                    AI.agent_history.add((f'R{"{0:0=2d}".format(neighbour.x)}{"{0:0=2d}".format(neighbour.y)}', 1))
                elif neighbour.resource_type == 1:
                    AI.agent_history.add((f'G{"{0:0=2d}".format(neighbour.x)}{"{0:0=2d}".format(neighbour.y)}', 1))
