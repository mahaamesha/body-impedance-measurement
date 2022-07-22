# run this program before/after retrieving data for a sample
# this will store data for every sample, which is used in body-composition (BC) calculation

import json_function as fjson


# ask input
def input_user():
    print()
    id = str( input("Input id (idxxx name)\t: ") )
    w = int( input("Input weight (kg)\t: ") )
    h = int( input("Input height (cm)\t: ") )
    y = int( input("Input age    (yo)\t: ") )
    s = int( input("Input gender (1/0)\t: ") )
    print()

    return id, w, h, y, s


# I will run this program in while loop, so this will wait for next sample data
def store_sample_data(file_path):
    # load retrieval_sample_data.json
    data = fjson.read_filejson(file_path)
    
    # ask input
    id, w, h, y, s = input_user()

    obj = {}        # create empty obj
    obj[id] = {}    # create new key
    obj[id]["weight"] = w   # assign data
    obj[id]["height"] = h
    obj[id]["age"] = y
    obj[id]["gender"] = s

    # write obj to json file
    if "sample id" in data.keys():
        fjson.write_obj_to_filejson(file_path, obj)
    else:
        fjson.append_obj_to_filejson(file_path, obj)

    print("Succesfully store sample data: %s" %id)


def print_choice():
    print("\nKey option:")
    print("a : Append new sample data")
    print("c : Clear json file")
    print("q : Quit program ")



if __name__ == "__main__":
    file_path = "tmp/retrieval_sample_data.json"
    fjson.initialize_retrieval_sample_data_files(file_path)

    key = ord("0")
    while key != ord("q"):
        print_choice()      # a/c/q
        key = ord( input("Input key (a/c/q): ") )
        
        if key == ord("a"):
            store_sample_data(file_path)
        elif key == ord("c"):
            fjson.clear_filejson(file_path)
        elif key == ord("q"):
            pass        # this will quit the while loop
