from copy import deepcopy
from copy import copy
import math
import random
from PacmanNode import *
from GhostNode import *
import sys
def generate_offspring(parent_tree_list_in, n_offspring):
    #debug
    if len(parent_tree_list_in) == 0:
        print("Error: empty parent_tree_list_in")
        sys.exit()
    #print("stuck here  8")
    #this will use mutate or crossover to generate offspring
    #in case of parents don't have the same number of children
    #the higher fitness parents will have at most 1 more offspring
    offspring_counter = n_offspring
    #print("stuck here  13")
    parent_tree_list = sorted(parent_tree_list_in, reverse = True, key = lambda x: x.fitness)
    #print("stuck here  15")
    offspring_tree_list = []
    #higer fitness in the front
    #print("stuck here  18")
    ctr = 0

    while True:
        #print("stuck here  20")
        #print(ctr)
        #ctr +=1
        #if ctr >= 10: break
        #print("parent_tree_list size", len(parent_tree_list))
        for i in parent_tree_list:
            #print("loop", i)
            #choose either mutate or crossover
            if random.choice([True,False]):
                #True then do mutation
                tmp = i.mutate()
                offspring_tree_list.append(tmp)
            else:
                #False then do crossover with a random tree, it can be itself(slight chance)
                tmp = i.crossover(random.choice(parent_tree_list))
                offspring_tree_list.append(tmp)
            #print(tmp.height)
            offspring_counter -= 1
            if offspring_counter == 0:
                #print("Generated", len(offspring_tree_list), "offsprings")
                return offspring_tree_list

def initialize_population(config_dict):
    n_pacman_trees = config_dict["pacman_stable_population"]
    pacman_trees = []
    for i in range(n_pacman_trees):

        tmp_tree = PacmanNode()
        #randomly run between grow and fill (ramped half and half)
        random.choice([tmp_tree.grow,tmp_tree.fill])()
        pacman_trees.append(tmp_tree)

    n_ghost_trees = config_dict["ghost_stable_population"]
    ghost_trees = []
    for i in range(n_ghost_trees):
        tmp_tree = GhostNode()
        #randomly run between grow and fill (ramped half and half)
        random.choice([tmp_tree.grow,tmp_tree.fill])()
        ghost_trees.append(tmp_tree)
    return pacman_trees, ghost_trees

def parsimony_coef(tree_size, max_tree_size, p):
    if(tree_size > max_tree_size):
        print("tree_size > max_tree_size", tree_size, max_tree_size)
        return 0
    return ((max_tree_size - tree_size)/max_tree_size)**p

def evaluate(config_dict, game, pacman_tree_list_in, ghost_tree_list_in):
    #parsimony_pressure need to be float larger than 1 to have a punishing effect
    #returns how may evalation completed in this function call
    #pacman_fitness_watch_value: if a game instance yeilds higher pacman
    #fitness that this, then save a copy of the whole game
    saved_game = None
    pacman_parsimony_pressure = config_dict["pacman_parsimony_pressure"]
    ghost_parsimony_pressure = config_dict["ghost_parsimony_pressure"]
    #n_pacman is number of pacman in a game, same for the ghost
    n_pacman = config_dict["n_pacman"]
    n_ghost = config_dict["n_ghost"]
    #make a shallow copy of the list, just the reference is needed
    pacman_tree_list = copy(pacman_tree_list_in)
    n_pacman_tree = len(pacman_tree_list)

    ghost_tree_list = copy(ghost_tree_list_in)
    n_ghost_tree = len(ghost_tree_list)

    pacman_share_controller = bool(config_dict["pacman_share_controller"])
    ghost_share_controller = bool(config_dict["ghost_share_controller"])
    pacman_max_tree_height = config_dict["pacman_max_tree_height"]
    ghost_max_tree_height = config_dict["ghost_max_tree_height"]

    max_pacman_tree_size = 2**(pacman_max_tree_height+1)-1
    max_ghost_tree_size = 2**(ghost_max_tree_height+1)-1

    pacman_entry_counter = 0
    sum_pacman_fitnes = 0
    generation_best_pacman_score = -1

    n_p_tree_pergame = 1 if pacman_share_controller else n_pacman
    n_g_tree_pergame = 1 if ghost_share_controller else n_ghost

    #calculate number of games need to be played to evaluate all the trees
    n_games = max(math.ceil(n_pacman_tree/n_p_tree_pergame), math.ceil(n_ghost_tree/n_g_tree_pergame))

    pacman_ptr = 0
    ghost_ptr = 0
    for i in range(n_games):
        #get pacman participant
        pacman_participant = []
        for j in range(n_p_tree_pergame):
            pacman_participant.append(pacman_tree_list[pacman_ptr])
            pacman_ptr = (pacman_ptr + 1)%n_pacman_tree
        #get ghost participant
        ghost_participant = []
        for j in range(n_g_tree_pergame):
            ghost_participant.append(ghost_tree_list[ghost_ptr])
            ghost_ptr = (ghost_ptr + 1)%n_ghost_tree

        #load pacman partiipant trees into controllers
        for j in range(n_pacman):
            #the mod operation makes it compatible for both shared and individual controllers
            game.pacman_controller_list[j].load_tree(pacman_participant[j%n_p_tree_pergame])
        #load ghost partiipant trees into controllers
        for j in range(n_ghost):
            #the mod operation makes it compatible for both shared and individual controllers
            #print("j=",j,"n_g_tree_pergame",n_g_tree_pergame,"j%n_g_tree_pergame", j%n_g_tree_pergame)
            #print(game.ghost_controller_list[j])
            #print(ghost_participant[j%n_g_tree_pergame])
            game.ghost_controller_list[j].load_tree(ghost_participant[j%n_g_tree_pergame])

        #start the game
        game.game_play()
        #after the game, assign the score
        #assign pacman score
        for j in range(n_p_tree_pergame):
            #this function is conpatible with both shared and individual controller
            #when controller is shared, n_p_tree_pergame = 1, loop will run only once
            #and assign the score the the first pacman(which is a shallow copy,
            #thus the score attribute of the origonal tree is assigned)
            pacman_participant[j].fitness = game.pacman_score * parsimony_coef(pacman_participant[j].get_size(), max_pacman_tree_size, pacman_parsimony_pressure)
            # print("pacman_score=", pacman_participant[j].fitness)
        #assign ghost score
        for j in range(n_g_tree_pergame):
            ghost_participant[j].fitness = game.ghost_score * parsimony_coef(ghost_participant[j].get_size(), max_ghost_tree_size, ghost_parsimony_pressure)
            # if type(ghost_participant[j].fitness) == complex:
            #     print("ERROR!!!!!!!!")
            #     print("game.ghost_score", game.ghost_score)
            #     print("ghost_score=", ghost_participant[j].fitness)
            #     print("parsimony_coef", parsimony_coef(ghost_participant[j].get_size(), max_ghost_tree_size, ghost_parsimony_pressure))
            #     print("ghost_participant[j].get_size()", ghost_participant[j].get_size())
            #     print("max_ghost_tree_size",max_ghost_tree_size,"ghost_parsimony_pressure",ghost_parsimony_pressure)
            #     print("ghost_tree_height=",ghost_participant[j].height)
            #     print("ghost_tree:", ghost_participant[j].execute())
            #     sys.exit()
        #get stats
        sum_pacman_fitnes += pacman_participant[0].fitness
        #pacmans have same fitness
        if(game.pacman_score > generation_best_pacman_score):
            generation_best_pacman_score = game.pacman_score
            saved_game = deepcopy(game)

    #after evaluation, the fitness scores are attached
    avg_pacman_fitnes = sum_pacman_fitnes/n_games

    return n_games, avg_pacman_fitnes, generation_best_pacman_score, saved_game

def k_tour(tree_list_in, n_select, k, rp):
    #tree_list, select n candidates, k size tournament, rp(replacement)= True/False
    if n_select > len(tree_list_in):
        print("ERROR: n_select is bigger than given group!")
    tree_set = set(tree_list_in)
    selected = []
    for i in range(n_select):
        #compatibility feature, if remaining population is less than k, then reduce the k
        if len(tree_set) < k:
            k = len(tree_set)
        tournament = random.sample(tree_set,k)
        winner = max(tournament, key = lambda x: x.fitness)
        if not rp:
            #if without replacement, then remove the winner from the big group
            tree_set.remove(winner)
        selected.append(winner)
    return selected


def fps(tree_list_in, n_select):
    if len(tree_list_in) == 0:
        print("Error: fps got empty list")
        sys.exit()
    selected = []
    #first fint the cumsum
    sum = 0
    list_in_size = len(tree_list_in)
    cumsum_list = []
    for i in tree_list_in:
        sum += i.fitness
        cumsum_list.append(sum)
    #cumsum_list is the big wheel
    for i in range(n_select):
        wheel_arm = random.uniform(0,sum)
        for j in range(list_in_size):
            if wheel_arm <= cumsum_list[j]:
                selected.append(tree_list_in[j])
                break
    #done
    if len(selected) == 0:
        print("Error: fps returning empty")
        sys.exit()
    return selected

def over_selection(tree_list_in, n_select, x):
    #x is the top x in percent, x is a float between 0 and 1
    #this algorithm will try* to get %80 of the selecting from the top x percent
    #meaning, if the n_given * x is smaller than n_select * 0.8, then all of the
    #top x percent will be selected once, the rest will all come from the rest 1-x percent
    if n_select > len(tree_list_in):
        print("ERROR: n_select is bigger than given group!")
    tree_list = copy(tree_list_in)
    #defaut sort is increasing order
    tree_list.sort(key = lambda x: x.fitness)
    tree_list_size = len(tree_list)
    #top x percent has the following number of elements
    n_top = int(tree_list_size * x)
    #the number in the rest of the group has this many
    n_bottom = tree_list_size - n_top

    n_select_from_top = min(n_select, n_top)
    #can't select more than it has
    n_select_from_bottom = n_select - n_select_from_top
    bottom_list = tree_list[:n_bottom]#increasing order
    top_list = tree_list[n_bottom:]
    selected = random.sample(top_list, n_select_from_top) + random.sample(bottom_list, n_select_from_bottom)
    return selected

def trunc(tree_list_in, n_select):
    # print("TRUNC ###########################")

    # for i in tree_list_in:
    #     print(i.fitness, end =" ")
    # print("#################################")
    if n_select > len(tree_list_in):
        print("ERROR: n_select is bigger than given group!")
    return sorted(tree_list_in, key = lambda x: x.fitness)[:n_select]
