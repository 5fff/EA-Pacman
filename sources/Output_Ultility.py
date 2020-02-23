def plot_best_run(best_run_scores,config_dict):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plot_file_name = config_dict["plot_file_name"]
    x = best_run_scores[0]
    y = best_run_scores[1]
    plt.clf()
    plt.plot(x, y, 'r-', label = "pacman_score")
    plt.xlabel("Evaluations")
    plt.ylabel("highest_pacman_score")
    plt.title(" Best pacman score vs Evaluations with random controllers")
    plt.legend()
    plt.savefig( plot_file_name)

# def write_log(game, nick_name):
#     replay_name = "replay_"+str(nick_name)
#     func_file_name = "func_"+str(nick_name)
#
#     replay_file = open(config_dict["log_file_name"],"w")
#
#     log_file.write("Use the setting in the following lines to re-create this experiment\n\n")
#     log_file.write(str(config_dict) + "\n\n")
#     log_file.write("Result Log\n")
#     for run_number, run in enumerate(all_runs_scores):
#         log_file.write("\nRun "+str(run_number)+"\n")
#         for i in range(len(run[0])):
#             #run[0][i] is the eval number  run[1][i] is the score
#             log_file.write(str(run[0][i])+"\t"+str(run[1][i])+"\n")
#     log_file.close()
