import itertools
import queue
import random
from copy import deepcopy
import sys
from Controller import *

DEAD_PACMAN_COORD = (-5,-5)
INT_MAX = sys.maxsize

def vec_add(a,b): #tuple element wise add
    return tuple(sum(x) for x in zip(a,b))

def vec_dist(a,b): #tuple distance, return one value
    return sum(abs(x[0]-x[1]) for x in zip(a,b))

def vec_subtract(a,b): #a-b
    return tuple((x[0]-x[1]) for x in zip(a,b))

def vec_bounded(a,b): # return True/False if vector a is bounded by (0,0) and b
    for x in zip(a,b):
        if(not(x[0] >= 0 and x[0]<= x[1])): return False
    return True

class Maze:
    def __init__(self, config_dict):
        self.config = deepcopy(config_dict)
        self.size_tuple = config_dict["size_tuple"]
        self.bound_tuple = vec_add(self.size_tuple ,(-1,-1)) #size is the furthest coordinate from orgin, offset by 1
        self.pacman_start_point = (0,self.bound_tuple[1])
        self.ghost_start_point = (self.bound_tuple[0],0)
        self.n_pacman = self.config["n_pacman"]
        self.n_ghost = self.config["n_ghost"]
        self.pill_value = self.config["pill_value"]
        #get controller for both pacman and the ghosts
        self.pacman_controller_list = [Controller(self, "Pacman", i) for i in range(config_dict["n_pacman"])]
        self.ghost_controller_list = [Controller(self, "Ghost", i) for i in range(config_dict["n_ghost"])]
    def clear_t_cache(self):
        #clear all the terminal cache
        self.t_cache_dict = {
        self.t_mdpg: dict(),
        self.t_mdpp: dict(),
        self.t_nwp: dict(),
        self.t_mdpf: dict(),
        self.t_md_other_p: dict(),
        self.t_md_near_p: dict(),
        self.t_md_other_g: dict()
        }

    def t_md_near_p(self, ghost_coordinate):
        #this is used by ghost to find the manhattan distance to nearest pacman
        if ghost_coordinate in self.t_cache_dict[self.t_md_near_p]:
            return self.t_cache_dict[self.t_md_near_p][ghost_coordinate]
        else:
            #first make a index set of alive pacmans' coordinate
            dist = INT_MAX
            for i in range(self.n_pacman):
                if self.pacman_alive[i]:
                    dist = min(dist, vec_dist(ghost_coordinate,self.pacman[i]))
            #update cache
            self.t_cache_dict[self.t_md_near_p][ghost_coordinate] = dist
            if(dist == INT_MAX):
                print("Error in t_md_near_p, probaby called this function when no pacman alive")
                sys.exit()
            return dist

    def t_md_other_g(self, ghost_coordinate, ghost_id):
        #this is used by a ghost to find the manhattan distance to the nearest other ghost
        if (ghost_coordinate, ghost_id) in self.t_cache_dict[self.t_md_other_g]:
            return self.t_cache_dict[self.t_md_other_g][(ghost_coordinate, ghost_id)]
        else:
            #first make a set of other ghosts' coordinate
            other_ghost_set = set(range(self.n_ghost)) - {ghost_id}
            dist = INT_MAX
            for i in other_ghost_set:
                dist = min(dist, vec_dist(ghost_coordinate,self.ghost[i]))
            #update cache
            self.t_cache_dict[self.t_md_other_g][(ghost_coordinate, ghost_id)] = dist
            return dist

    def t_md_other_p(self, pacman_coordinate, pacman_id):
        #this is used by a pacman to find the manhattan distance to the nearest other pacman
        if (pacman_coordinate, pacman_id) in self.t_cache_dict[self.t_md_other_p]:
            return self.t_cache_dict[self.t_md_other_p][(pacman_coordinate, pacman_id)]
        else:
            #first make a set of other alive pacman's coordinate
            other_pacman_set = set(range(self.n_pacman)) - {pacman_id}
            other_alive_pacman = set()
            for i in other_pacman_set:
                if self.pacman_alive[i]:
                    other_alive_pacman.add(i)
            #if no other pacman alive, then return a very big number (distance to heaven)
            dist = INT_MAX
            for i in other_alive_pacman:
                dist = min(dist, vec_dist(pacman_coordinate,self.pacman[i]))
            #update cache
            self.t_cache_dict[self.t_md_other_p][(pacman_coordinate, pacman_id)] = dist
            return dist
    def t_mdpg(self, pacman_coordinate):
        #Manhattan distance between Pac-Man and the nearest Ghost
        #pacman_coordinate is the whatif coordinate for a pacman
        #check if cache exist
        if pacman_coordinate in self.t_cache_dict[self.t_mdpg]:
            return self.t_cache_dict[self.t_mdpg][pacman_coordinate]
        else:
            dist = INT_MAX
            for g in self.ghost:
                dist = min(dist, vec_dist(pacman_coordinate,g))
            #store cache
            self.t_cache_dict[self.t_mdpg][pacman_coordinate] = dist
            return dist

    def t_mdpp(self, pacman_coordinate):
        #Manhattan distance between Pac-Man and the nearest pill
        if pacman_coordinate in self.t_cache_dict[self.t_mdpp]:
            return self.t_cache_dict[self.t_mdpp][pacman_coordinate]
        else:
            dist = INT_MAX
            for p in self.pills:
                dist = min(dist, vec_dist(pacman_coordinate,p))
            #store cache
            self.t_cache_dict[self.t_mdpp][pacman_coordinate] = dist
            return dist

    def t_nwp(self, pacman_coordinate):
        #the number of walls immediately adjacent to Pac-Man, used by pacman only
        if pacman_coordinate in self.t_cache_dict[self.t_nwp]:
            return self.t_cache_dict[self.t_nwp][pacman_coordinate]
        else:
            n = 0
            for direction in [(1,0),(0,-1),(-1,0),(0,1)]:
                if (vec_add(pacman_coordinate, direction) in self.walls):
                    n += 1
            self.t_cache_dict[self.t_nwp][pacman_coordinate] = n
            return n

    def t_mdpf(self, pacman_coordinate):
        #the Manhattan distance between Pac-Man and the fruit
        if pacman_coordinate in self.t_cache_dict[self.t_mdpf]:
            return self.t_cache_dict[self.t_mdpf][pacman_coordinate]
        else:
            if self.fruit:
                dist = vec_dist(pacman_coordinate,self.fruit)
            else:
                #if fruit doesn't exist, then give it a huge value to make it "hopeless" lol
                dist = INT_MAX
            self.t_cache_dict[self.t_mdpf][pacman_coordinate] = dist
        return dist



    def spawn_fruit(self): #it will only spawn fruit if theres no fruit on board
        if (not self.fruit) and random.random() <= self.config["fruit_spawn_probability"]:
            self.fruit = random.sample(self.empty_cells - set(self.pacman) - self.pills, 1)[0]

    def update_valid_moves(self):#generates available moves for both pacman and ghost(two 2d lists)
        direction_list = [(1,0),(0,-1),(-1,0),(0,1)]
        #pacmans
        #self.all_pacman_valid_moves = set() # all available moves for all ghpsts an pacmans, this is for generating sensor feed
        self.pacman_valid_moves=[]
        for i in self.pacman:
            moves = []
            for direction in direction_list:
                try_cell = vec_add(i, direction)
                if try_cell in self.empty_cells:
                    moves.append(try_cell)
                    #self.all_pacman_valid_moves.add(try_cell)
            moves.append(i)#add its current location in valid moves(hold position)
            #self.all_pacman_valid_moves.add(i)
            self.pacman_valid_moves.append(moves)
        #self.all_ghost_valid_moves = set()
        self.ghost_valid_moves=[]
        for i in self.ghost:
            moves = []
            for direction in direction_list:
                try_cell = vec_add(i, direction)
                if try_cell in self.empty_cells:
                    moves.append(try_cell)
                    #self.all_ghost_valid_moves.add(try_cell)
            self.ghost_valid_moves.append(moves)
    def print_replay_log(self, f_name = None): #print log to file
        if f_name:
            time_step_log_file = open(f_name, "w")
        else:
            time_step_log_file = open(self.config["replay_file_name"], "w")
        time_step_log_file.write(str(self.size_tuple[0]) + "\n" + str(self.size_tuple[1]) + "\n")
        #print walls

        for j in self.walls:
            time_step_log_file.write("w " + str(j[0]) + " " + str(j[1]) + "\n")
        for j in self.replay_log["pills"]:
            time_step_log_file.write("p " + str(j[0]) + " " + str(j[1]) + "\n")
        prev_fruit = None
        n_turns = len(self.replay_log["pacman"])
        for i in range(0, n_turns):
            for j, p in enumerate(self.replay_log["pacman"][i]): #!!!!!!!!!!!!!! only use one symbol for all pacmen
                time_step_log_file.write("m" + str(j) + " " + str(p[0]) + " " + str(p[1]) + "\n")
            for j, g in enumerate(self.replay_log["ghost"][i]):
                time_step_log_file.write(str(j+1) + " " + str(g[0]) + " " + str(g[1]) + "\n")#!!!!ghost number start with 1
            tmp_fruit = self.replay_log["fruit"][i]
            if tmp_fruit and tmp_fruit != prev_fruit: #if fruit exist
                prev_fruit = tmp_fruit
                time_step_log_file.write("f " + str(tmp_fruit[0]) + " " + str(tmp_fruit[1]) + "\n")
            tmp_time = self.replay_log["time_left"][i]
            tmp_score = self.replay_log["pacman_score"][i]
            time_step_log_file.write("t " + str(tmp_time) + " " + str(tmp_score) + "\n")
    #initialize also regenerate a new board
    def game_initialize(self): #keep the maze and reset the game
        self.fast_generate_board()
        self.clear_t_cache()
        self.pills = set() #pills are recorded in a set
        self.pacman = [self.pacman_start_point for x in range(self.n_pacman)] #pacman starting coordinate
        #print(self.pacman)
        self.ghost = [self.ghost_start_point for x in range(self.n_ghost)] #ghost starting coordinate
        self.n_pills = int(self.config["pills_density"] * (len(self.empty_cells)-1))
        self.pills = set(random.sample(self.empty_cells - {self.pacman_start_point}, self.n_pills))
        self.time_limit = self.size_tuple[0]*self.size_tuple[1]*self.config["time_multiplier"]
        self.countdown_timer = self.time_limit
        self.fruit = None
        self.pacman_score = 0
        self.pacman_alive = [True for _ in range(self.n_pacman)]

    def log_current_turn(self):
        self.replay_log["pacman"].append(deepcopy(self.pacman))
        self.replay_log["ghost"].append(deepcopy(self.ghost))
        self.replay_log["time_left"].append(self.countdown_timer)
        self.replay_log["pacman_score"].append(self.pacman_score)
        self.replay_log["fruit"].append(self.fruit)

    def game_over(self):
        #this function also update the alive status of pacmans
        #detect if game over
        g_set = set(self.ghost)

        any_pacman_alive = False
        for i in range(self.n_pacman):
            if self.pacman[i] in g_set:
                self.pacman_alive[i] = False
                self.pacman[i] = DEAD_PACMAN_COORD
            if self.pacman_alive[i] == True:
                any_pacman_alive = True
        if not any_pacman_alive:
            return True
        if(self.countdown_timer <= 0):
            return True
        if not self.pills:
            return True
        return False

    def game_play(self): #start the evaluation/gameplay
        self.game_initialize()
        self.replay_log = {"pacman":[], "ghost":[], "time_left":[], "pacman_score":[], "fruit":[]}
        self.replay_log["pills"] = deepcopy(self.pills)
        game_over_flag = False

        while(not game_over_flag):
            self.log_current_turn()
            self.countdown_timer -= 1
            self.spawn_fruit()
            #update pacman
            self.update_valid_moves()
            for i in range(self.n_pacman):
                #only update if the pacman is alive
                if self.pacman_alive[i]:
                    self.pacman[i] = self.pacman_controller_list[i].get_move(self.pacman_valid_moves[i])#update pacmans' locations, it can detect swap
                    if self.pacman[i] == None:
                        print("controller gives None")
            #update score
            tmp_pacman_set = set(self.pacman)
            self.pacman_score += len(tmp_pacman_set.intersection(self.pills))*self.pill_value
            self.pills = self.pills.difference(tmp_pacman_set) #remaining pills
            if self.fruit in tmp_pacman_set:
                self.pacman_score += self.config["fruit_score"]
                self.fruit = None
            #detect game_over
            if self.game_over():
                break
                #game_over_flag = True
            #update ghost
            for i in range(self.n_ghost):
                self.ghost[i] = self.ghost_controller_list[i].get_move(self.ghost_valid_moves[i])#update ghosts' locations
            if self.game_over():
                break
                #game_over_flag = True
            self.clear_t_cache()
            #record log
        #after the game ends, if all pills are eaten then add time bonus
        if(not self.pills):
            self.pacman_score += int(self.countdown_timer/self.time_limit*100)
        self.ghost_score = max(0, self.pill_value * self.n_pills - self.pacman_score)
        self.log_current_turn() #log the state when the game ends

    def fast_generate_board(self): #it also resets the game
        #empty cells means non-wall cells, or the cells that can be walked on
        self.walls = set() #walls are recorded in a set
        self.empty_cells = set(itertools.product(range(self.size_tuple[0]),range(self.size_tuple[1])))#every open coordinates on board
        self.wall_density = self.config["wall_density"] #wall density has to be between 0 and (total_cell - width - y)/(total_cell - 2)
        self.exp_n_wall = int(self.wall_density*(self.size_tuple[0]*self.size_tuple[1]-2))
        iter_list = random.sample(self.empty_cells- {self.pacman_start_point, self.ghost_start_point}, len(self.empty_cells)-2)
        #iter_list = deepcopy(self.empty_cells)
        self.wall_counter = 0
        for i in iter_list:
             #remove it and see if it works
            #if(self.local_connected(i) ):#if it works, then add it to wall set
            #if(self.greedy_connected(i)):
            if(self.quick_frag_check(i)):
                self.empty_cells.remove(i)
                self.walls.add(i)
                self.wall_counter += 1 #increment the counter
            if self.wall_counter == self.exp_n_wall: break #quota met

    def generate_board(self): #it also resets the game
        #empty cells means non-wall cells, or the cells that can be walked on
        self.walls = set() #walls are recorded in a set
        self.empty_cells = set(itertools.product(range(self.size_tuple[0]),range(self.size_tuple[1])))#every open coordinates on board
        self.wall_density = self.config["wall_density"] #wall density has to be between 0 and (total_cell - width - y)/(total_cell - 2)
        self.exp_n_wall = int(self.wall_density*(self.size_tuple[0]*self.size_tuple[1]-2))
        self.random_list = random.sample(self.empty_cells- {self.pacman_start_point, self.ghost_start_point}, len(self.empty_cells)-2)
        self.wall_counter = 0
        for i in self.random_list:
            self.empty_cells.remove(i) #remove it and see if it works
            #if(self.local_connected(i) ):#if it works, then add it to wall set
            #if(self.greedy_connected(i)):
            #if(self.local_connected(i)):
            #if(self.local_connected(i) or self.greedy_connected(i)):
            if(self.local_connected(i) or self.cells_connected(self.empty_cells)):#if it works, then add it to wall set
                self.walls.add(i)
                self.wall_counter += 1 #increment the counter
            else:
                self.empty_cells.add(i) #if it doesn't work, add it back
            if self.wall_counter == self.exp_n_wall: break #quota met
        # the function will at most run n-2 times
    def quick_frag_check(self, center):
        #returns True if it is NOT fragmented, False if fragmented
        #A super fast way to check if the surrounding 8 cells are fragmented if a wall is placed in the center
        #Methedology
        #a wall or a non-existant cell(outside the board) is defined as False state
        #an empty cell is defined as a True state
        #a fragmentation exists if go around the circle and the state toggles more than twice
        n_toggle = 0
        #get the initlal state
        prev_state = vec_add(center, (-1, -1)) in self.empty_cells
        search_direction = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
        for direction in search_direction:
            current_state = vec_add(center, direction) in self.empty_cells
            n_toggle += prev_state ^ current_state
            prev_state = current_state
            #this is XOR, it can be used to detect difference
            if n_toggle > 2:
                return False
        return True
    def local_connected(self, center):
        search_direction = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        local_cells = set()
        for direction in search_direction:
            try_cell = vec_add(center, direction)
            if try_cell in self.empty_cells:
                local_cells.add(try_cell)
        return self.cells_connected(local_cells)

    def greedy_connected(self, center):
        search_direction = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)] #surrounding 9 direction
        visit_queue = queue.Queue()
        local_set = set()
        for direction in search_direction:
            try_cell = vec_add(center, direction)
            if try_cell in self.empty_cells:
                local_set.add(try_cell)
        visit_queue.put(next(iter(local_set)))
        greedy_direction = [(0,1),(1,0),(0,-1),(-1,0)] # up right down left
        remaining_cells = deepcopy(self.empty_cells)
        while(not visit_queue.empty()):
            visiting = visit_queue.get()
            offset_vector = vec_subtract(visiting, center) #distance vector, used to tell direction
            greedy_direction_start = int(True)<<1 + int(True) #turn true/fase into binary, use this value to determine the starting direction
            for i in range(greedy_direction_start, greedy_direction_start + 4): #explor 4 directions
                direction = greedy_direction[i%4] #circular list
                try_visit = vec_add(visiting, direction)
                if(try_visit in remaining_cells):
                    remaining_cells.remove(try_visit)
                    visit_queue.put(try_visit)
            if(not local_set.intersection(remaining_cells)): return True
        if(remaining_cells): return False #if there remains cells unvisited, then it is not connected
        else: return True

    def cells_connected(self, cells):
        remaining_cells = deepcopy(cells)
        visit_queue = queue.Queue()
        visit_queue.put(remaining_cells.pop())
        while(not visit_queue.empty()):
            visiting = visit_queue.get()
            for direction in [(1,0),(0,-1),(-1,0),(0,1)]:#right,down,left,up
                try_visit = vec_add(visiting, direction)
                if(try_visit in remaining_cells):
                    remaining_cells.remove(try_visit)
                    visit_queue.put(try_visit)
        if(remaining_cells): return False #if there remains cells unvisited, then it is not connected
        else: return True

    def display(self):
        disp_dict = {"wall":"\x1b[0;33;44m  \x1b[0m", "empty": "  "}
        visual_grid = [["empty" for i in range(self.size_tuple[0])] for j in range(self.size_tuple[1])]
        for i in self.walls:
            visual_grid[i[1]][i[0]] = "wall"
        for row in visual_grid[::-1]:
            for cell in row:
                print(disp_dict[cell],end = "")
            print()
