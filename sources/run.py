from Game_Ultility import *
from GPNode import *
from EA_Ultility import *
from Controller import *
from Output_Ultility import *
from Input_Ultility import *
import  argparse
from datetime import datetime
import sys
import os
#read config file name
parser = argparse.ArgumentParser()
parser.add_argument("--file", "-f", type=str, required=False, default = "default.cfg")
argument = parser.parse_args()
config_file_name = str(argument.file)

#read config dictionary
config_dict = get_config_dict(config_file_name)

result_folder_name = config_dict["result_folder_name"]
os.mkdir(result_folder_name)

#seeding
if("convergence_n_eval" in config_dict):
    convergence_n_eval = config_dict["convergence_n_eval"]
    no_change_counter = 0
    last_best_fitness = 0
else:
    convergence_n_eval = None


if("seed" in config_dict) and (config_dict["seed"] != "t"):
    seed = str(config_dict["seed"])
else: #if seed is not specified
    #if seed with time
    seed = str(datetime.now())
    config_dict["seed"] = seed #change config_dict for log keeping
print("Seeding with", seed)
random.seed(seed)

GPNode.grow_terminal_prob = config_dict["grow_terminal_prob"]
PacmanNode.max_tree_height = config_dict["pacman_max_tree_height"]
GhostNode.max_tree_height = config_dict["ghost_max_tree_height"]

play_station = Maze(config_dict)


all_runs_scores = []
best_run_scores = None #[[eval#, eval#, ...],[score 0, score 1...]]
global_best_play_instance = None

#write log header and config
log_file = open(result_folder_name+"/"+config_dict["log_file_name"],"w")
log_file.write("Use the setting in the following lines to re-create this experiment\n\n")
log_file.write(str(config_dict) + "\n\n")
log_file.write("Result Log\n")

game_score_watch_value = 0
best_saved_game = None
for i in range(config_dict["n_run"]):#each run
    print("Run", i, "################")
    log_file.write("\nRun "+str(i)+"\n")
    play_station = Maze(config_dict)
    eval_counter = 0

    ###########initialize population and evaluate##########
    pacman_population, ghost_population = initialize_population(config_dict)
    n_eval, avg_pacman_fitnes, best_pacman_fitness, saved_game = evaluate(config_dict, play_station, pacman_population, ghost_population)

    ####logging log <- eval avg best
    if saved_game:
        if(best_saved_game == None or saved_game.pacman_score > best_saved_game.pacman_score):
            best_saved_game = saved_game
            game_score_watch_value = best_saved_game.pacman_score
    eval_counter += n_eval
    log_file.write(str(eval_counter)+"\t"+str(avg_pacman_fitnes)+"\t"+str(best_pacman_fitness) + "\n")
    print("Eval", eval_counter)
    ############begin the evolution cycles####################
    while(True):
        ########Pacman Parent Selection##################
        if config_dict["pacman_parent_selection"] == "fps":
            pacman_parent = fps(pacman_population, config_dict["n_pacman_parent"])
        elif config_dict["pacman_parent_selection"] == "os":
            pacman_parent = over_selection(pacman_population, config_dict["n_pacman_parent"], config_dict["over_selection_x"])
        ########Ghost Parent Selection###################
        if config_dict["ghost_parent_selection"] == "fps":
            ghost_parent = fps(ghost_population, config_dict["n_ghost_parent"])
        elif config_dict["ghost_parent_selection"] == "os":
            ghost_parent = over_selection(ghost_population, config_dict["n_ghost_parent"], config_dict["over_selection_x"])

        if (len(pacman_parent) != config_dict["n_pacman_parent"]):
            print("Pacman_parent population =", len(pacman_parent))
            sys.exit()
        ########offspring generation##############
        pacman_offspring = generate_offspring(pacman_parent, config_dict["pacman_offspring_population"])
        ghost_offspring = generate_offspring(ghost_parent, config_dict["ghost_offspring_population"])
        ########evaluate offspring################
        n_eval, avg_pacman_fitnes, best_pacman_fitness, saved_game = evaluate(config_dict, play_station, pacman_offspring, ghost_offspring)
        ####logging log <- eval avg best
        if saved_game:
            if(best_saved_game == None or saved_game.pacman_score > best_saved_game.pacman_score):
                best_saved_game = saved_game
                game_score_watch_value = best_saved_game.pacman_score
        eval_counter += n_eval
        log_file.write(str(eval_counter)+"\t"+str(avg_pacman_fitnes)+"\t"+str(best_pacman_fitness) + "\n")
        print("Eval", eval_counter)
        ########## merge offspring into current population##########
        pacman_population = pacman_population + pacman_offspring
        ghost_population = ghost_population + ghost_offspring
        ########## Pacman survival selection ################
        if config_dict["pacman_survival_selection"] == "trunc":
            pacman_population = trunc(pacman_population, config_dict["pacman_stable_population"])
        elif config_dict["pacman_survival_selection"] == "k_tour_no_rp":
            #k tournament without replacement
            pacman_population = k_tour(pacman_population, config_dict["pacman_stable_population"], config_dict["pacman_survival_k"], False)
        else:
            print("ERROR: Wrong Pacman Selection Method!")
            sys.exit()
        ########## ghost survival selection ################
        if config_dict["ghost_survival_selection"] == "trunc":
            ghost_population = trunc(ghost_population, config_dict["ghost_stable_population"])
        elif config_dict["ghost_survival_selection"] == "k_tour_no_rp":
            #k tournament without replacement
            ghost_population = k_tour(ghost_population, config_dict["ghost_stable_population"], config_dict["ghost_survival_k"], False)
        else:
            print("ERROR: Wrong ghost Selection Method!")
            sys.exit()
        ########termination check#################
        if(eval_counter >= config_dict["n_eval"]):
            break
        ########## No Change Termination(optional) ###########################
        if convergence_n_eval:
            if best_pacman_fitness > last_best_fitness:
                last_best_fitness = best_pacman_fitness
                no_change_counter = 0
            else:
                no_change_counter += n_eval
                if(no_change_counter >= convergence_n_eval):
                    print("NO CHANGE IN FITNESS, TERMINATING!")
                    break
    #at the end of each run, print the replay log
    saved_game.print_replay_log(result_folder_name+"/run_"+str(i)+"_replay")
    pacman_func_src = saved_game.pacman_controller_list[0].func_str
    ghost_func_src = saved_game.ghost_controller_list[0].func_str
    func_file = open(result_folder_name+"/run_"+str(i)+"_func",'w')
    func_file.write("\nBest Pacman Function in last generation:\n" + str(pacman_func_src))
    func_file.write("\n\nCorresponding Ghost Function in last generation::\n" + str(ghost_func_src))


#plot_best_run(best_run_scores,config_dict)
#write_log(all_runs_scores, config_dict)

#best_saved_game.print_replay_log()
