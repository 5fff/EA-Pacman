import random
from copy import deepcopy
import sys

 #addition
def f_add(a,b):
    return "(" + a + "+" + b + ")"
#subtraction
def f_sub(a,b):
    return "(" + a + "-" + b + ")"
#multiplication
def f_mul(a,b):
    return "(" + a + "*" + b + ")"
#division
def f_div(a,b):
    return "self.f_safe_div(" + a + "," + b + ")"
#random
def f_rand(a,b):
    return "self.rand(" + a + "," + b + ")"

class GPNode:
    #below is the common data shared betwn all nodes
    #terminal_list = [t_p_1,t_p_2,t_p_3,t_p_4,t_p_5]
    function_list = [f_add,f_sub,f_mul,f_div,f_rand]

    def __init__(self):
        self.height = None
        self.is_terminal = None
        self.func = None #a reference to the function
        self.left = None
        self.right = None
    def get_size(self):
        if self.is_terminal:
            return 1
        else:
            return self.left.get_size() + self.right.get_size() + 1

    def execute(self):
        if(self.is_terminal):
            return self.func()#terminal does not take input
        else:
            return self.func(self.left.execute(),self.right.execute())

    #update_height may not be useful as variatiopn operators updates the height
    def update_height(self):
        if(self.is_terminal):
            self.height = 0
            return 0
        else:
            self.height = max(self.left.update_height(), self.right.update_height()) + 1
            return self.height
    def grow(self):
        self.grow_operation(self.max_tree_height)

    def grow_operation(self, max_depth):
        #this will grow randomly and  recursively from the node it is called and will stop at the max depth
        #it will update the height as well
        #return height
        #first decide if this node becomes a terminal
        if(max_depth == 0 or random.random() <= self.grow_terminal_prob):
            #grow terminal(this node becomes the terminal)
            self.is_terminal = True
            self.height = 0
            #randomly choose a terminal function
            self.func = random.choice(self.terminal_list)
            self.left = None
            self.right = None
            return self.height
        else:
            #not terminal
            self.is_terminal = False
            self.func = random.choice(self.function_list)
            self.left = self.node_type()
            self.right = self.node_type()
            #grow the children nodes and calculate the height at the same time
            self.height = max(self.left.grow_operation(max_depth - 1), self.right.grow_operation(max_depth - 1)) + 1
            return self.height
    def fill(self):
        #this is the user facing function
        self.fill_operation(self.max_tree_height)

    def fill_operation(self, max_depth):
        #this function can be used as user facing, but it needs to manually configure depth
        #this function builds a full binary tree, so max depth equals max height
        if(max_depth == 0):
            #grow terminal(this node becomes the terminal)
            self.is_terminal = True
            self.height = 0
            #randomly choose a terminal function
            self.func = random.choice(self.terminal_list)
            self.left = None
            self.right = None
            #return self.height
        else:
            #not terminal
            self.is_terminal = False
            self.func = random.choice(self.function_list)
            self.left = self.node_type()
            self.right = self.node_type()
            self.left.fill_operation(max_depth -1)
            self.right.fill_operation(max_depth -1)
            #grow the children nodes
            #height is the max depth of the sub tree
            self.height = max_depth
    def mutate(self):
        #mutate function will return a mutated copy of the tree itself, canbe used in offspring generation
        target_depth = random.randint(0, self.height)
        mutation_depth_limit = self.max_tree_height - target_depth
        offspring = deepcopy(self)
        #if the parent has a fitness score on itself, it need to remove it from the offspring as that's not
        #the offspring's fitness score
        #try to remove the fitness score if it exists
        try:
            del offspring.fitness
        except:
            pass
        # print("mutat_operation return height=",offspring.mutate_operation(target_depth, mutation_depth_limit))

        ###Debug###
        #tmp_save = offspring.height
        offspring.update_height()
        """
        if(tmp_save != offspring.update_height()):
            print("height error in offspring mutate")
            print("offspring.height=", tmp_save, "Actual height=", offspring.update_height())
            sys.exit()
        """
        return offspring

    def mutate_operation(self, target_depth, mutation_depth_limit):
        #this is not user facing, its is an internal function
        #target_depth is at which depth the mutation will happen
        #mutation_depth_limit is the max depth the mutation will propagate counting from the target_depth
        #mutation_depth_limit need to be calculated carefully for keeping trees within height limit
        if(target_depth == 0):
            #reached the target depth
            self.grow_operation(mutation_depth_limit)
            #self.height is already updated by self.grow_operation()
            return self.height
        else:
            #not yet reached the target depth
            branch_choices = []
            if(self.left.height >= target_depth - 1):
                branch_choices.append(self.left)
            if(self.right.height >= target_depth - 1):
                branch_choices.append(self.right)
            ##debug
            if(branch_choices == []):
                print("Self.height", self.height)
                print("Self.left.height", self.left.height)
                print("Self.right.height", self.right.height)
            next_node = random.choice(branch_choices)
            self.height = next_node.mutate_operation(target_depth - 1, mutation_depth_limit) + 1
            return self.height

    def crossover_opration(self, target_depth, foreign_subtree):
        #this is not user facing, its is an internal function
        #this will be called on the undeveloped offspring root node recursively(without branching)
        if(target_depth == 0):
            #reached the target depth
            #can't directly replace it self with the root node of the foreign sub tree
            # copy all the foreign subtree rootnode's value to itself
            self.is_terminal = foreign_subtree.is_terminal
            self.height = foreign_subtree.height
            self.func = foreign_subtree.func
            self.left = foreign_subtree.left
            self.right = foreign_subtree.right
            #done copying value
            #no need to update the subtree's height, it's already updated
            return self.height

        else:
            #not yet reached the target depth
            branch_choices = []
            if(self.left.height >= target_depth - 1):
                branch_choices.append(self.left)
            if(self.right.height >= target_depth - 1):
                branch_choices.append(self.right)
            ##debug
            if(branch_choices == []):
                print("target_depth", target_depth)
                print("Self.height", self.height)
                print("Self.left.height", self.left.height)
                print("Self.right.height", self.right.height)
            next_node = random.choice(branch_choices)

            self.height = next_node.crossover_opration(target_depth - 1, foreign_subtree) + 1
            return self.height

    def crossover(self, target_tree):
        #first randomly select a subtree from the target tree
        target_depth = random.randint(0,target_tree.height)
        ref = target_tree
        while(target_depth > 0):
            target_depth -= 1
            branch_choices = []
            if(ref.left.height >= target_depth):
                branch_choices.append(ref.left)
            if(ref.right.height >= target_depth):
                branch_choices.append(ref.right)
            ref = random.choice(branch_choices)

        #now reference points at the root node of the target subtree
        foreign_subtree = deepcopy(ref)
        #try to strip the fitness value on the rootnode in case it is the original tree's rootnode with a fitness value
        try:
            del foreign_subtree.fitness
        except:
            pass
        #start with a copy of the parent itself, this is an undeveloped offspring
        offspring = deepcopy(self)
        #try to strip the fitness value, same reason as the others
        try:
            del offspring.fitness
        except:
            pass
        #then attach the subtree to applicable locations, replacing the subtree
        #at the same time
        max_crossover_depth = self.max_tree_height - foreign_subtree.height
        random_depth = random.randint(0, min(max_crossover_depth, self.height))
        ###debug
        #print("foreign_subtree.height",foreign_subtree.height)
        #print("random_depth",random_depth)
        #print("self.height",self.height)
        ###debug
        offspring.crossover_opration(random_depth, foreign_subtree)
        offspring.update_height()
        return offspring
