#!/usr/bin/env python

import csv
import os
import re
import sys
import platform
import datetime
from collections import OrderedDict

PRG = "TODOs"

__author__ = "Max Sbabo, GIT: sbaby171"

def main(param_dict, debug = False):
    func = "main"

    cwd = os.getcwd()
    todo_list = cwd + "/todo_list"
    done_list = cwd + "/done/done_list"

    cats = {}
    todos = {}
    lastcode = "0x0" # Hexadecimal string
    
    # Read in current categories file: 
    cats = read_categories(path=cwd + "/categories",debug=debug)
    # TODO: Make this category readin optional. The category description file is not needed.

    # Read in the current todos list: 
    todos, lastcode = read_todos_list(path=todo_list, read=param_dict["-read"],cat=param_dict["-cat"],debug=debug)

    # Add new object to todo-list
    write_todo_item(path=todo_list,cat=param_dict["-cat"],todo=param_dict["-todo"],code=next_code(lastcode),debug=debug)

    # Remove item it presented
    remove_todo_item(todo_list=todo_list,done_list=done_list,todos=todos,code=param_dict["-rm"],debug=debug)

    # Put last code in read
    

def remove_todo_item(todo_list, done_list, todos, code, debug=False):
    """ 
    Remove todo item and write it to the done_list. 

    Parameters: 
    -----------
      todo_list : Path to todo-list
      done_list : Path to done-list
      todos : Dictionary holding all open todo items. 
      code : Code to be removed

    """
    func = "remove_todo_item"
 
    if not code:
        return 

    if not os.path.isfile(todo_list):
        raise RuntimeError("(%s): File does not exist.\n  - Checked file = %s"%(func, todo_list)) 

    if not os.path.isfile(done_list):
        raise RuntimeError("(%s): File does not exist.\n  - Checked file = %s"%(func, done_list)) 

    if code not in todos:
        raise RuntimeError("(%s): Code (%s) was not found in todos list."%(func, code))


    tmp = []
    with open(todo_list, "r") as todoList:
        tdl = todoList.readlines()
        for lnum, line in enumerate(tdl, start=1):
            if lnum == 1: 
                tmp.append(line.strip())
                continue 
            _code=line.split(":")[1].strip("() ")
            if _code == code: 
                write_done_item(path=done_list,item=line.strip(),debug=debug)
            else: 
                tmp.append(line.strip())

    with open(todo_list+".new", "w") as newfile:
        for item in tmp:    
            newfile.write(item+"\n")
  
    os.popen("cp %s %s"%(todo_list, todo_list+".bak"))
    os.popen("mv %s %s"%(todo_list+".new", todo_list))


           



def write_done_item(path, item, debug=False):
    func = "write_done_item"
    
    if not os.path.isfile(path):
        raise RuntimeError("(%s): File does not exist.\n  - Checked file = %s"%(func, path)) 

    ctd  = datetime.datetime.now()
    ctds = "%s/%s/%s"%(ctd.month,ctd.day,ctd.year) 
    with open(path, "a+") as donelist: 
        front = item.split(":")[:2]
        date  = item.split(":")[2].strip("() ")
        back  = item.split(":")[3:]

        date = ": (Start=%s - Finished=%s)"%(date,ctds)
        x = "".join(front) + date + ":".join(back)
        x = x.strip("TODO: ")

        donelist.write("DONE: %s\n"%x)

   
    
def read_todos_list(path, read, cat, debug=False): 
    """ 
    Read the todos-list and store contents within a dictionary.

    Parameters: 
    -----------
      path : Path to the todos-list
      read : Boolean whether to print contents to system console. 
      cat : Category of the todo item. 
      
    Return: 
    -------
      todos : Dictionary holding the contents of the todos-list.
              Data-Structure: 
                  |
                 key(str()): pair(str()) 
      lastcode : the last todo code 
    """
    func = "read_todos_list"
    RE_TODO_ITEM = re.compile("^TODO:\s+\((?P<code>[\w]+)\):\s+\((?P<date>[\/\d]+)\):\s+\((?P<category>[\w\.]+)\):\s+(?P<desc>.*)")

    todos    =  {}   # Return todos dictionary
    lastcode =  "0x0"   # Return last todo code (hexadecimal string)

    if not os.path.isfile(path):
        raise RuntimeError("(%s): File does not exist.\n  - Checked file = %s"%(func, path))    

    with open(path,"r") as infile_data:
        ifd=infile_data.readlines()
        for lnum, line in enumerate(ifd, start=1):
            line = line.strip()
 
            if lnum == 1:
                lastcode = line.split("Latest-Code = ")[-1]

            todofound = RE_TODO_ITEM.search(line)
            if todofound:
                code = todofound.group("code")
                #lastcode = compare_codes(code, lastcode, debug=debug)
                date = todofound.group("date")
                category = todofound.group("category")
                desc = todofound.group("desc")
                todos[code] = {}
                todos[code]["category"] = category
                todos[code]["date"] = date
                todos[code]["description"] = desc
                continue;
    
    if len(todos) == 0 and read:
        print("%s: No todos found within the todos-list"%(PRG)) 

    if len(todos) != 0 and lastcode == "0x0":
        raise RuntimeError("(%s): Mismatch with latest-code (%s). Please check."%(func, lastcode))


    # todoslist done reading
    if read:
        for code in todos: 
            print("%s: (%s): Code = %s"%(PRG, func, code))
            print("%s: (%s):   Category...... =  %s"%(PRG, func, todos[code]["category"]))
            print("%s: (%s):   Date.......... =  %s"%(PRG, func, todos[code]["date"]))
            print("%s: (%s):   Description... =  %s"%(PRG, func, todos[code]["description"]))
            
    return todos, lastcode
            
def compare_codes(a, b, debug=False):
    """ 
    This function returns the highest of the two hexadecimal strings
    
    Parameters: 
    -----------
      a : Hexadecimal string
      b : Hexadecimal string

    Returns: 
    --------
      c : The greater of the two input strings.
    """
    func = "compare_codes"
    ai = int(a, 16)
    bi = int(b, 16)
    
    if ai > bi:
        c = a
    else: 
        c = b
    return c

def next_code(a):
    """ 
    This function takes in a hexadecimal string and increments it by one, and returns it back as a hex-string.

    Parameters: 
    -----------
      a : hexadecimal string
     
    Returns: 
      b : 'a' + 1 as a hex-string 
    """
    func ="next_code"
    ai = int(a, 16)
    ai+=1
    b = hex(ai)
    return b 

    

def write_todo_item(path, cat, todo, code, debug=False):
    """ 
    Append todo item to the todo-list. 
    
    Parameters: 
    -----------
      path : Path to the todos-list
      cat : Category of todo item. 
      todo : Description of todo item. 
      code : Hex-string for the todo entry

    Return: 
    """
    func = "write_todo_item"
 
    if not todo:
        if debug: print("DEBUG: (%s): Warning, No '-todo' was provided. Skipping function."%(func))
        return 

    if todo and not cat: 
        raise RuntimeError("(%s): Must provide a category for the todo item."%(func))

    if not os.path.isfile(path):
        raise RuntimeError("(%s): File does not exist.\n  - Checked file = %s"%(func, path))
    
    ctd  = datetime.datetime.now()
    ctds = "%s/%s/%s"%(ctd.month,ctd.day,ctd.year) 
    
    with open(path,"a+") as todolist:
        todolist.write("TODO: (%s): (%s): (%s): %s\n"%(code,ctds,cat,todo))

    # rewrite first line to update latest-code
    with open(path,"r") as todolist: 
        tdl = todolist.readlines()
    tdl[0] = "Latest-Code = %s\n"%(code)
    with open(path, "w") as _file: 
        _file.writelines(tdl) 
   
    return  


# NOTE: It is the job of the caller to provide path
def read_categories(path, debug=False):
    """ 
    Read in the category description file and provide a dictionary representation of it. 

    Parameters: 
    -----------
      path : Path to category description file.
    
    Return: 
    -------
      cat : Dictionary representation of category description file.
            Data-Structue: 
                |
               key(str(category)): Pair(str(description))
    """
    func = "read_categories"

    cats = {}

    if not os.path.isfile(path):
        raise RuntimeError("(%s): File does not exist.\n  - Checked file = %s"%(func, path))

    with open(path,"r") as infile_data:
        ifd=infile_data.readlines()
        for lnum, line in enumerate(ifd):
            line=line.strip()
            if lnum == 0: # if first line, check the header 
                sline = line.split(",")
                if sline[0] != "category" or sline[1] != "description": # Check the syntax
                    raise RuntimeError("(%s): File header is incorrect. Exiting"%(func)) 
            else: 
                sline = line.split(",", 1) # Split string at the first comma 
                cats[sline[0]] = sline[1]  
    if debug: 
        for cat in cats: 
            print("DEBUG: (%s): Category = %s, Description = %s"%(func, cat, cats[cat]))

    return cats
            
     
  
 
def handle_cmd_args(args = None, debug = False):
    def print_help_menu():
        for opt in lookup_desc:
            print("  <%s>:\n         %s"%(opt, lookup_desc[opt]))
    
    func = "handle_cmd_args"
    if (debug): print("DEBUG: (func%s): <--> Function invoked."%(func))

    lookup_dict = {"-debug" : False, "-help": False,"-h":False,  
                   "-todo": "", 
                   "-cat" : "",
                   "-read": False,
                   "-rm" : "",
                  } 
    lookup_desc = {"-debug" : "(optiona;): (Default=False): Debug flag. If true, state details of program will be provided to console.",
                   "-help"  : "(optional): Display help menu.",
                   "-cat"   : "(optional): Category",
                   "-rm"    : "(optional): Remove todo item by code",
                   "-read"  : "(optional): Print todos list. Can be used with '-cat' to print todos only related to given category.",
                   "-todo"  : "(optional):String decription of execution. String must be enclosed by quotations.\n" + 
"         Ex)  -todo \"Call your mother.\""
                  }
    if ("-help" in args) or ("-h" in args): 
        print_help_menu(); sys.exit(1)
    
    i = 0 
    stop = len(args)
    while i < stop:
        arg = args[i]
        if (debug): print("DEBUG: (func%s): Command-line arguement = %s, index value = %d"%(func, arg, i))
        if arg in lookup_dict:
            if type(lookup_dict[arg]) is list:  # MSN: List should not iterate the index 'i' because the end key is an arg "-<arg>", that still needs to be processed.
                if (debug): print("DEBUG: (func%s): Cmd-arg (%s) lookup-type is (%s = %s)"%(func, arg, type(arg), list))
                tmpList = []
                for ii in range(i+1,stop,1):
                    listItem = args[ii]
                    if (debug): print("DEBUG: (%s): ii = %d, value = %s, value-type: %s."%(func, ii, str(listItem), str(type(listItem))))
                    if (debug): print("DEBUG: (%s): Processing for type-list: cmd-arg = %s"%(func, str(listItem)))

                    if listItem.startswith("-"):
                        if (debug): ("DEBUG: (%s): Found a new cmd-arg. List is complete. Setting list to look up."%(func))
                        lookup_dict[arg] = tmpList
                        i = ii;
                        break
                    if listItem == args[-1]:
                        tmpList.append(listItem) # MSN: Store the list-item.
                        lookup_dict[arg] = tmpList
                        i = ii + 1 
                        break
                    if not listItem.startswith("-"):
                        if (debug): ("DEBUG: (%s): Found list item: %s"%(func,listItem)) 
                        tmpList.append(listItem) # MSN: Store the list-item.


            if type(lookup_dict[arg]) is (type(str())):
                if (debug): print("DEBUG: (func%s): Cmd-arg (%s) lookup-type is (%s = %s)"%(func, arg, type(arg), type(str())))
                lookup_dict[arg] = str(args[args.index(arg)+1])
                i += 2; continue;
            if type(lookup_dict[arg]) is (type(bool())):
                if (debug): print("DEBUG: (func%s): Cmd-arg (%s) lookup-type is (%s = %s)"%(func, arg, type(arg), type(bool())))
                lookup_dict[arg] = not lookup_dict[arg] # invert the opposite.
                i += 1; continue;
            if type(lookup_dict[arg]) is (type(int())):
                if (debug): print("DEBUG: (func%s): Cmd-arg (%s) lookup-type is (%s = %s)"%(func, arg, type(arg), type(int())))
                lookup_dict[arg] = str(args[args.index(arg)+1])
                i += 2; continue;
            # Add other type checks here, if needed...
        else: 
            print("ERROR: (func%s): Unsupported command line = %s. Exiting."%(func, arg)) 
            print_help_menu(); sys.exit(1)

    ## Check mandatory options:
    ##   Example: Uncommment if needed
    ##   -----------------------------
    #if not lookup_dict["-cat"]:
    #    print("ERROR: (func%s): Command line option (%s) is mandatory! Exiting!"%(func, "-cat"))
    #    print_help_menu(); sys.exit(1)
    #if not lookup_dict["-todo"]:
    #    print("ERROR: (func%s): Command line option (%s) is mandatory! Exiting!"%(func, "-note"))
    #    print_help_menu(); sys.exit(1)
    #if lookup_dict["-rm"]:
    #    lookup_dict["-rm"]= hex(lookup_dict["-rm"]) 

    if (debug):  
        for key in lookup_dict:
            print("DEBUG: (func%s): 'lookup_dict' final status: key = (%s), pair = (%s), pair-type = (%s)" %(func, key, lookup_dict[key], type(lookup_dict[key])))

    return lookup_dict




def _exit_(msg = "", errcode = 1, debug = False):
    func = "_exit_"
    global ERROR, DEBUG

    # MSN: ERROR = 1; It is the standard-default error code.(Can configure at TOF) 
    if (errcode == ERROR):
        sys.stderr.write("ERROR: (%s): %s.\n"%(func,msg))
        sys.exit(ERROR)
    # MSN: DEBUG = -1; It is the standard-default debug code. (can configure at TOF)
    if (errcode == DEBUG): 
        sys.stderr.write("DEBUG: (%s): %s.\n"%(func,msg))
        sys.exit(DEBUG)
   
    # Un-accounted for errcode
    sys.stderr.write("EXIT: (%s): Exitting (%s) with error-code = %d\n"%(func,PROG, errcode))
    sys.exit(errcode)
    

if __name__ == "__main__":
    func = __name__

    debug = True if ("-debug" in sys.argv) else False
    if debug: print("DEBUG: (func%s): Python Version: %s"%(func, str(platform.python_version())))

    # Parse command-line and call main
    arg_lookup = handle_cmd_args(args = sys.argv[1:], debug = debug)
    # Call main to being processing 
    main(param_dict = arg_lookup, debug = debug)
