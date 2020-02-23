import random
import sys
from copy import deepcopy
INT_MIN = - sys.maxsize
INT_MAX = sys.maxsize
#a very small value that will always be replaced

#a/b
def safe_div(a,b):
    if(b):
        return a/b
    return INT_MAX

class Controller:
    def __init__(self, game, role_type, role_id):
        self.game = game
        #it binds with a game when initialized
        self.tree_func = None
        self.f_safe_div = safe_div
        self.rand = random.uniform
        self.role_type = role_type #"Pacman"/"Ghost"
        self.role_id = role_id
    def load_tree(self, root_node):
        str_front = "def temp_func(coord):\n\treturn "
        self.func_str = root_node.execute()
        exe_str = str_front + self.func_str
        #print(exe_str)
        exec(exe_str, locals())
        self.tree_func = locals()["temp_func"]
        #print(self.tree_func)
    #the original move function is renamed as get_move
    def get_move(self, valid_moves):
        move = None
        best_val = None
        for m in valid_moves:
            tmp_val = self.tree_func(m)
            if best_val == None or tmp_val > best_val:
                best_val = tmp_val
                move = m
        return move

class Ghost_Random_Controller:
    def __init__(self, game):
        pass
    #the original move function is renamed as get_move
    def get_move(self, valid_moves):
        return random.sample(valid_moves, 1)[0]
