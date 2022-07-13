import os
import pandas as pd

from formula import *
import json_function as fjson
from graph import *
from post_process import *


data_path = "E:/_TUGAS/_ITBOneDrive/OneDrive - Institut Teknologi Bandung/_Kuliah/_sem7/7_kerja praktek/data/hand to hand"
folder_name = ["data variasi grip/"]
folder_path = folder_name.copy()

fstart = 20e3
fend = 50e3


def prepare_data(folder_path_i):
    # scan all files
    path, dirs, files = next(os.walk(folder_path_i))

    # append datasets to the list
    dfs = {}
    for fn in files:
        path = folder_path_i + fn
        temp_df = pd.read_csv(path)
        dfs[fn[:-4]] = temp_df

    dfs_list = list(dfs.values())

    # delete column contains NaN
    for df in dfs_list:
        # get column name
        column_list = []
        for col in df.columns:
            column_list.append(col)
        
        # delete column after "Magnitude"
        # "Magnitude" in index 5
        for i in range(len(column_list)):
            if i > 5: del df[column_list[i]]
    
    return files, dfs, dfs_list


def preprocessing_data_retrieval(files):
    # extract the every variation
    variation_str = []
    for f in files:
        if f[:-8] not in variation_str:
            variation_str.append( f[:-8] )

    return variation_str


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


def process_analysis(folder_path_i, variation_str, dfs_list, iteration):
    saved_dirname = prepare_result_folder(data_path)
    
    # plot & save figure
    graph_per_variation(variation_str, iteration, dfs_list, folder_path_i, saved_dirname,
                    x_data="Frequency", y_data="Impedance",
                    x_label="Frequency (Hz)", y_label="Impedance (Ohm)",
                    suptitle_prefix="Impedance")
    graph_per_variation(variation_str, iteration, dfs_list, folder_path_i, saved_dirname,
                    x_data="Frequency", y_data="Phase",
                    x_label="Frequency (Hz)", y_label="Phase (°)",
                    suptitle_prefix="Phase")
    
    # get z_mid & phase_mid from every dataframe. data_mid is data at fmid
    # arr = [[...], [...], ...]
    arr_z_mid, arr_phase_mid, dfs_list = get_data_mid(dfs_list, iteration)
    
    # every variation have n dataframes. n = num_of_iteration
    # build single dataframe for every variation by averaging them
    df_choosen = build_df_choosen(dfs_list, iteration)

    # plot & save figure
    single_graph_from_df_choosen(df_choosen, variation_str, folder_path_i, saved_dirname,
                                x_data="Frequency", y_data="Impedance",
                                x_label="Frequency (Hz)", y_label="Impedance (Ohm)",
                                suptitle_prefix="SG Impedance")

    single_graph_from_df_choosen(df_choosen, variation_str, folder_path_i, saved_dirname,
                                x_data="Frequency", y_data="Phase",
                                x_label="Frequency (Hz)", y_label="Phase (°)",
                                suptitle_prefix="SG Phase")

    # store data_avg of parameter: z, phase. Stored to variatioin_rc_json
    arr_z_avg, arr_phase_avg = get_z_phase_avg_from_df_choosen(df_choosen)

    # calculate r,c from z,phase
    fmid = find_fmid_from_data_retrieval(dfs_list)
    arr_r, arr_c = get_rc_value(arr_z_avg, arr_phase_avg, fmid)  

    # update json file data
    update_retrieval_overview_json(files, iteration, variation_str)
    update_retrieval_variation_json(variation_str,
                                    arr_z_mid, arr_phase_mid,
                                    arr_z_avg, arr_phase_avg,
                                    arr_r, arr_c)


if __name__ == "__main__":
    i = 0
    for f in folder_path:
        folder_path[i] = os.path.join(data_path, f)
        i += 1

    # prepare tmp files
    fjson.initialize_tmp_files()

    # process analysis
    for idx in range(len(folder_path)):
        print("Processing %s ..." %folder_name[idx])

        # preprocessing
        files, dfs, dfs_list = prepare_data(folder_path[idx])
        variation_str = preprocessing_data_retrieval(files)
        saved_dirname = prepare_result_folder(data_path)

        iteration = len(dfs_list) // len(variation_str)

        # main processing
        process_analysis(folder_path[idx], variation_str, dfs_list, iteration)
        # process_analysis(folder_path[idx])

        print()


    # create dataframe from final retrieval_variation.json
    header = ["Variation", "Z (Ohm)", "\u03C6 (°)", "R (Ohm)", "C (Farad)"]
    data_key = ["variation", "z_avg", "phase_avg", "r_avg", "c_avg"]
    df_params = build_df_from_rc_variation_json(header, data_key)

    # save them as image
    save_df_as_image(df_params, filename="TB Parameters", saved_dirname=saved_dirname)

    # tabulate dataframe in markdown file
    create_markdown_table_from_dataframe(df_params, filename="TB Parameters", saved_dirname=saved_dirname)