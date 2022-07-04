import json
import os
import sys

file_path = os.path.dirname(__file__)
project_path = os.path.join(file_path, "../")


# GENERAL FUNCTION

def read_filejson(file_path="tmp/file.json"):
    try:
        path = os.path.join(project_path, file_path)

        with open(path, "r") as f:
            data = json.load(f)
        
        return data
    except:
        sys.exit("Error: Cannot find %s" %file_path)


def write_obj_to_filejson(file_path="tmp/file.json", obj={}):
    path = os.path.join(project_path, file_path)

    # initialize file if it's not already
    with open(path, "a"):
        pass
    
    if (obj == {}):
        while True:
            ans = input("Write empty obj to %s? (y/n) " %file_path)
            if (ans == "y"): break
            elif (ans == "n"): sys.exit("Canceled")

    with open(path, "w") as f:
        json.dump(obj, f, indent=4)


# similar with write_obj_to_filejson, but only for clear file purpose
def clear_filejson(path):
    with open(path, "w") as f:
        json.dump({}, f, indent=4)
        pass


# format json file: {"key1":value1, "key2":value2}
def write_keyvalue(file_path="tmp/file.json", key="keyname", value=None):
    path = os.path.join(project_path, file_path)
    with open(path, "r+") as f:
        data = json.load(f)

        if key in data.keys():
            data[key] = value
        else:
            sys.exit("Error: There is no key named \"%s\"" %key)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


# (END) GENERAL FUNCTION


# SPECIFIC FUNCTION

# (END) SPECIFIC FUNCTION


if __name__ == "__main__":
    # define certain obj for formatting
    variation_rc_obj = \
    {
        "Rohm CpF": {
            "r": None,
            "c": None,
            "z_ref": None,
            "z_eks": None,
            "z_err": None,
            "phase_ref": None,
            "phase_eks": None,
        }
    }

    overview_obj = \
    {
        "folder_path": [None],
        "variation": [None],
        "num_variation": None,
        "num_iteration": None
    }

    # initialization json files
    write_obj_to_filejson(file_path="tmp/variation_rc.json", obj=variation_rc_obj)
    write_obj_to_filejson(file_path="tmp/overview.json", obj=overview_obj)

    print("Run json_function.py ... Done")