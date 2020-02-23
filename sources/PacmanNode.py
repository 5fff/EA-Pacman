from GPNode import *

def t_p_1():
    return "self.game.t_mdpg(coord)"

def t_p_2():
    return "self.game.t_mdpp(coord)"

def t_p_3():
    return "self.game.t_nwp(coord)"

def t_p_4():
    return "self.game.t_mdpf(coord)"

#Manhattan distance to closest other pacman
def t_p_5():
    return "self.game.t_md_other_p(coord, self.role_id)"


class PacmanNode(GPNode):
    terminal_list = [t_p_1,t_p_2,t_p_3,t_p_4,t_p_5]

PacmanNode.node_type = PacmanNode
