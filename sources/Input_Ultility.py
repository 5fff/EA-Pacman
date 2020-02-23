#this file consists of functions dealing with inputs

import sys
def get_config_dict(filename):# readin a file as dictionary and return it
    try:
        f = open(str(filename),'r')
    except:
        print("CONFIG READING ERROR: Please check the config file path!")
        sys.exit()

    data=f.read()
    f.close()
    try:
        confg_dict = eval(data)
    except:
        print("CONFIG FORMAT ERROR: please use the standard Python dictionary format!")
        print("Format Hint: True/False value shoud be True or False WITHOUT quotes")
        print("Seed setting can be either a string or \"t\" meaning to seed with system time (both with quotes)")
        sys.exit()
    return  confg_dict #this will convert data to a dictionary
