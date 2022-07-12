import os
import pandas as pd

from formula import *
import json_function as fjson


data_path = "E:/_TUGAS/_ITBOneDrive/OneDrive - Institut Teknologi Bandung/_Kuliah/_sem7/7_kerja praktek/data/hand to hand"
folder_name = ["data variasi grip/"]
folder_path = folder_name.copy()

fstart = 20e3
fend = 50e3


def find_fmid_from_data_retrieval(dfs_list):
    df_sample = dfs_list[0]
    nrows = len(df_sample)

    fmid = df_sample["Frequency"][nrows//2]

    return fmid


def get_data_mid(dfs_list, iteration):
    # get z_mid & phase_mid from every dataframe. data_mid is data at fmid
    # arr = [[...], [...], ...]
    arr_z_mid = []
    arr_phase_mid = []

    nrows = len(dfs_list[0])
    count = 0       # counting how many variation
    for df in dfs_list:
        idx = count // iteration
        
        # append new [] if need larger index
        if len(arr_z_mid)-1 != idx:
            arr_z_mid.append([])
            arr_phase_mid.append([])
        
        arr_z_mid[idx].append( df["Impedance"][nrows//2] )
        arr_phase_mid[idx].append( df["Phase"][nrows//2] )

        count += 1

    return arr_z_mid, arr_phase_mid, dfs_list


def prepare_result_folder(data_path):
    # prepare folder to save the figure
    saved_dirname = ""
    for i in range(len(data_path)-1, 0, -1):
        if data_path[i] == "/":
            saved_dirname = data_path[i+1:len(data_path)] + "/"
            break

    # create directory
    path_option = [
        os.path.join("../media/", saved_dirname),
        os.path.join("media/", saved_dirname)
        ]
    
    if not( os.path.isdir(path_option[0]) ):    # for notebook environment
        try: os.mkdir(path_option[0])
        except: pass
    if not( os.path.isdir(path_option[1]) ):  # for local python environment
        try: os.mkdir(path_option[1])
        except: pass

    return saved_dirname


def build_df_choosen(dfs_list, iteration):
    # build new dataframe
    # array of averaged dataframe from every iteration
    df_choosen = []

    for i in range(len(dfs_list) // iteration):     # iterate per num_of_variation
        df_temp = dfs_list[0].copy(deep=True)
        df_temp[:] = 0
        
        for j in range(iteration*i, iteration*(i+1)):
            # print(i, j)
            df_temp += dfs_list[j]

        df_temp[:] /= iteration
        df_choosen.append(df_temp)
    
    return df_choosen


def get_z_phase_avg_from_df_choosen(df_choosen):
    # save mid value from averaged_dataframe
    # array to store mid value of z from every averaged_dataframe
    arr_z_avg = []
    arr_phase_avg = []

    nrows = len(df_choosen[0])
    for df in df_choosen:
        arr_z_avg.append( df["Impedance"][nrows//2] )
        arr_phase_avg.append( df["Phase"][nrows//2] )
    
    return arr_z_avg, arr_phase_avg


def get_rc_value(arr_z, arr_phase, fmid):
    arr_r = []
    arr_c = []

    for i in range(len(arr_z)):
        r = calculate_r(arr_z[i], arr_phase[i])
        c = calculate_c(arr_z[i], arr_phase[i], fmid)

        arr_r.append(r)
        arr_c.append(c)

    return arr_r, arr_c


def update_retrieval_overview_json(files, iteration, variation_str):
    # save important information to json file
    file_path = "tmp/retrieval_overview.json"

    fjson.write_keyvalue(file_path, "folder_path", folder_name)
    fjson.write_keyvalue(file_path, "sweep_frequency", [fstart, fend])
    fjson.write_keyvalue(file_path, "variation_str", variation_str)
    fjson.write_keyvalue(file_path, "num_variation", len(files)//iteration)
    fjson.write_keyvalue(file_path, "num_iteration", iteration)
    
    print("Writing", file_path, "... Done")


def update_retrieval_variation_json(variation_str,
                            arr_z_mid, arr_phase_mid,
                            arr_z_avg, arr_phase_avg,
                            arr_r, arr_c):
    # save important information to json file
    file_path="tmp/retrieval_variation.json"
    obj = {}

    # update value of each key
    for i in range(len(variation_str)):
        obj[variation_str[i]] = {}

        obj[variation_str[i]]["z_mid"] = arr_z_mid[i]
        obj[variation_str[i]]["z_avg"] = arr_z_avg[i]
        obj[variation_str[i]]["phase_mid"] = arr_phase_mid[i]
        obj[variation_str[i]]["phase_avg"] = arr_phase_avg[i]
        
        obj[variation_str[i]]["r_avg"] = arr_r[i]
        obj[variation_str[i]]["c_avg"] = arr_c[i]

    # clear formatting in file json
    data = fjson.read_filejson(file_path)
    if len(data) <= 1:
        fjson.write_obj_to_filejson(file_path, obj={})

    fjson.append_obj_to_filejson(file_path, obj=obj)

    print("Writing", file_path, "... Done")


def build_df_from_rc_variation_json(header, data_key):
    data = fjson.read_filejson(file_path="tmp/retrieval_variation.json")

    keys = list( data.keys() )
    values = list( data.values() )

    df = pd.DataFrame(columns=header)

    for i in range(len(data)):      # loop as many as num_of_total_variations
        obj_row = {}    # append this as new row
        for j in range(len(header)):     # loop as many as num_of_columns
            if len(obj_row) == 0:
                obj_row[header[j]] = keys[i]        # for column: "variation"
            else:
                num = values[i][data_key[j]]
                if abs(num) == 0: num = 0
                elif float(num).is_integer(): num = int(num)
                elif abs(num) >= 1e-3: num = "{:.3f}".format(num)
                elif abs(num) < 1e-3: num = "{:.2e}".format(num)
                obj_row[header[j]] = num

        # add new row to dataframe
        df.loc[len(df)] = list( obj_row.values() )
        # print(obj_row, end="\n\n")
        # print(list(obj_row.keys()), end="\n\n")
    
    return df
