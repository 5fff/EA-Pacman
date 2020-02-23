from matplotlib import pyplot as plt
import re
import  argparse
import numpy as np
parser = argparse.ArgumentParser()
parser.add_argument("--file", "-f", type=str, required=False, default = "log")
argument = parser.parse_args()
log_file_name = str(argument.file)

log_list = []
file = open(str(log_file_name),"r")

EVAL = 0
AVG = 1
BEST = 2


while True:
    #find the next run block

    line = file.readline()
    if not line:
        #EOF
        print("eof")
        break
    line = re.split(' |\t|\n', line)
    if line[0] == "Run":
        run_block = []
        #start adding evals to each line
        while(True):
            line = re.split(' |\t|\n',file.readline())
            eval_line = []
            #print(line)
            if line[0] == "":
                #if it is the end of a run block, quite current loop
                break
            else:
                for i in [EVAL, AVG, BEST]:
                    eval_line.append(eval(line[i]))
            run_block.append(eval_line)
        log_list.append(run_block)

log_arr = np.array(log_list)
avg_all_runs = np.average(log_arr, axis = 0)
#print(avg_all_runs)

#Get the best fitness of each run on the last generation fot t-test
t_test_data = log_arr[:,-1,BEST]
t_test_list = list(t_test_data)
t_test_file = open("t_test_data","w")
for i in t_test_list:
    t_test_file.write(str(i)+"\n")

#EVAL, AVG, BEST
eval_axis = avg_all_runs[:,EVAL]
avg_axis = avg_all_runs[:,AVG]
best_axis = avg_all_runs[:,BEST]
plt.plot(eval_axis, avg_axis, 'g-', label = "avg_fitness")
plt.plot(eval_axis, best_axis, 'r-', label = "best_fitness")
plt.xlabel("Number of Evaluations")
plt.ylabel("Fitness Score")
plt.title("Fitness vs Number of Evaluations")
plt.legend()
plt.savefig( log_file_name +"_plot.png")
plt.show()
