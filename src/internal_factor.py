import os
import pandas as pd

import json_function as fjson
import processing as proc


# change this as needed
# as default value, for testing in this file only.
# in another file, I parse arguments
data_path = "E:/_TUGAS/_ITBOneDrive/OneDrive - Institut Teknologi Bandung/_Kuliah/_sem7/7_kerja praktek/data/repetisi RC"


def define_data_path(data_path):
    # dont change this below
    folder_name = "calibration/"
    folder_path = os.path.join(data_path, folder_name)

    return folder_path


def init_internal_factor_json():
    print("Initialize JSON file of internal factor ...")
    print("1. rc_internal_factor.json")
    print("2. retrieval_internal_factor.json")
    key = int( input("Choose filename: ") )
    if key == 1:
        file_path = "tmp/rc_internal_factor.json"
    elif key == 2:
        file_path = "tmp/retrieval_internal_factor.json"

    fjson.initialize_internal_factor(file_path)

    return file_path


# input Rcal and Phase for calibration
def build_df_internal_factor(dfs_list):
    # ask input for actual value from measurement
    print()
    r_cal = float( input("Input Actual Rcal (Ohm): ") )
    phase_cal = float( input("Input Actual Phase (°): ") )
    print()

    # calculate delta for z and phase
    # calculate the actual result: actual_result = (value_from_measurement - delta_params)
    df_internal_factor_list = []     # store calibration dataframes
    for i in range(len(dfs_list)):     # scan all dataframe
        z = dfs_list[i].loc[:, "Impedance"]
        phase = dfs_list[i].loc[:, "Phase"]

        dfs_list[i]["ΔZ"] = z - r_cal
        dfs_list[i]["Δφ"] = phase - phase_cal

        # append df[i] to df_temporary
        df_internal_factor_list.append(dfs_list[i])

        # print(files[i])
        # print(dfs_list[i].head())

    # create df to store result of averaging all dataframes
    df_internal_factor = pd.DataFrame()     # empty
    df_internal_factor = 0      # make all elements value to zero
    # sum every dataframe
    for df in df_internal_factor_list:
        df_internal_factor += df
    # average it in last iteration
    df_internal_factor /= len(df_internal_factor_list)
    
    # print(df_internal_factor)
    return df_internal_factor


# store delta_z and delta_phase to json file
def store_internal_factor_to_json(df_internal_factor, file_path="tmp/rc_internal_factor.json"):
    data = fjson.read_filejson(file_path)

    arr_delta_z = list( df_internal_factor["ΔZ"] )
    arr_delta_phase = list( df_internal_factor["Δφ"] )

    for i in range(len(arr_delta_z)):
        data["delta_z"].append( arr_delta_z[i] )
        data["delta_phase"].append( arr_delta_phase[i] )

    fjson.write_obj_to_filejson(file_path, obj=data)

    print("Writing %s ... Done" %file_path)


def get_internal_factor(data_path):
    folder_path = define_data_path(data_path)
    file_path = init_internal_factor_json()

    files, dfs, dfs_list = proc.prepare_data(folder_path)
    
    df_internal_factor = build_df_internal_factor(dfs_list)

    store_internal_factor_to_json(df_internal_factor, file_path)


if __name__ == "__main__":
    get_internal_factor(data_path)
    
    print("Run internal_factor.py ... Done")