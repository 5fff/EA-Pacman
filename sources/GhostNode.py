from GPNode import *

def t_g_1():
    return "self.game.t_md_near_p(coord)"

def t_g_2():
    return "self.game.t_md_other_g(coord, self.role_id)"

# def t_g_3():
#     return "(-1)"
class GhostNode(GPNode):
    terminal_list = [t_g_1, t_g_2]

GhostNode.node_type = GhostNode
