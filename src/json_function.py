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
    
    with open(path, "w") as f:
        json.dump(obj, f, indent=4)


# appending obj={} to dictionary that already exist
def append_obj_to_filejson(file_path="tmp/file.json", obj={}):
    path = os.path.join(project_path, file_path)

    data = read_filejson(path)
    data.update(obj)
    
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


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
def initialize_tmp_files():
    # define obj for formatting purposes
    variation_rc_obj = \
    {
        "Rohm CpF": {
            "r": None,  # from measurement
            "c": None,  # from measurement

            "z_ref": None,  # from calculate_z(r, xc) using r,c measurement
            "z_mid": [],    # from data retrieval. for every iteration
            "z_avg": None,  # from data retrieval
            "z_err": None,  # reference: "z_ref", data: "z_avg"

            "phase_ref": None,
            "phase_mid": [],
            "phase_avg": None,
            "phase_err": None,
            
            "r_ref": None,                          # from "z_ref" and "phase_ref"
            "r_avg": None,                          # from "z_avg" and "phase_avg"
            "r_err_theoryref_measurement": None,    # reference: "r", data: "r_ref"
            "r_err_theoryavg_measurement": None,    # reference: "r", data: "r_avg"

            "c_ref": None,
            "c_avg": None,
            "c_err_theoryref_measurement": None,
            "c_err_theoryavg_measurement": None
        }
    }

    overview_obj = \
    {
        "folder_path": [None],
        "sweep_frequency": [None],
        "r_variation": [None],
        "c_variation": [None],
        "num_variation": None,
        "num_iteration": None
    }

    # initialization json files
    write_obj_to_filejson(file_path="tmp/variation_rc.json", obj=variation_rc_obj)
    write_obj_to_filejson(file_path="tmp/overview.json", obj=overview_obj)

    print("Initialize tmp files ... Done")

# (END) SPECIFIC FUNCTION


if __name__ == "__main__":
    initialize_tmp_files()

    print("Run json_function.py ... Done")