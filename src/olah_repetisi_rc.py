import os
import shutil
import pandas as pd

from formula import *
import json_function as fjson
from graph import *


data_path = "E:/_TUGAS/_ITBOneDrive/OneDrive - Institut Teknologi Bandung/_Kuliah/_sem7/7_kerja praktek/data/repetisi RC"
folder_name = ["465ohm variasi C/", "1003ohm variasi C/", "1468ohm variasi C/"]
folder_path = folder_name.copy()

fstart = 20e3
fend = 50e3


def process_analysis(folder_path_i, fstart=20e3, fend=50e3):
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

    # extract the RC variation
    variation_str = []
    for f in files:
        if f[:-8] not in variation_str:
            variation_str.append( f[:-8] )

    variation_data = variation_str.copy()

    # remove units
    for i in range(len(variation_data)):
        want_to_replaced = ["ohm", "F"]
        for str in want_to_replaced:
            if str in variation_data[i]:
                variation_data[i] = variation_data[i].replace(str, "")

    # convert "p" and "n" into 1e(-N)
    convert_unit = [["k", "e3"], ["u", "e-6"], ["n", "e-9"], ["p", "e-12"]]
    for i in range(len(variation_data)):
        for unit_str, unit_val in convert_unit:
            if unit_str in variation_data[i]:
                mystr = variation_data[i]
                variation_data[i] = mystr.replace(unit_str, unit_val)

    # split into [[R1, C1], [R2, C2], ...]
    for i in range(len(variation_data)):
        mystr = variation_data[i]
        arr_split = mystr.split(" ")
        variation_data[i] = arr_split

    # convert as float
    for i in range(len(variation_data)):
        if len(variation_data[i]) != 2:     # only R
            variation_data[i].append(0)     # add value of C = 0
        for j in range(len(variation_data[i])):
            variation_data[i][j] = float(variation_data[i][j])

    # theoritic
    fmid = calculate_fmid(fstart, fend)
    arr_z = []
    arr_phase = []
    for i in range(len(variation_data)):
        r = variation_data[i][0]
        c = variation_data[i][1]
        xc = calculate_xc(fmid, c)
        z = calculate_z(r, xc)
        phase = calculate_phase(fmid, r, c)

        arr_z.append(z)
        arr_phase.append(phase)

    # calculate error Z
    iteration = len(dfs) // len(variation_data)

    i = 0
    for df in dfs_list:
        df["%Z"] = calculate_error(arr_z[i//iteration], df["Impedance"])
        i += 1


    # prepare folder to save the figure
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
    
    # plot
    graph_per_variation(variation_str, iteration, dfs_list, folder_path_i, saved_dirname,
                    x_data="Frequency", y_data="%Z",
                    x_label="Frequency (Hz)", y_label="Impedance Error (%)",
                    suptitle_prefix="%Z vs f")
    graph_per_variation(variation_str, iteration, dfs_list, folder_path_i, saved_dirname,
                    x_data="Frequency", y_data="Impedance",
                    x_label="Frequency (Hz)", y_label="Impedance (Ohm)",
                    suptitle_prefix="Impedance")
    graph_per_variation(variation_str, iteration, dfs_list, folder_path_i, saved_dirname,
                    x_data="Frequency", y_data="Phase",
                    x_label="Frequency (Hz)", y_label="Phase (°)",
                    suptitle_prefix="Phase")

    # save important information to json file

    file_path="tmp/variation_rc.json"
    variation_rc_obj = {}
    for i in range(len(variation_data)):
        variation_rc_obj[variation_str[i]] = {}
        
        variation_rc_obj[variation_str[i]]["r"] = variation_data[i][0]
        variation_rc_obj[variation_str[i]]["c"] = variation_data[i][1]
        variation_rc_obj[variation_str[i]]["z_ref"] = arr_z[i]
        variation_rc_obj[variation_str[i]]["phase_ref"] = arr_phase[i]

    fjson.write_obj_to_filejson(file_path, obj=variation_rc_obj)

    print("Writing", file_path, "... Done")


    # save important information to json file
    file_path = "tmp/overview.json"
    overview_obj = fjson.read_filejson(file_path)

    fjson.write_keyvalue(file_path, "num_variation", len(files)//iteration)
    fjson.write_keyvalue(file_path, "num_iteration", iteration)
    fjson.write_keyvalue(file_path, "folder_path", folder_name)

    # extract variation r and c
    arr_r_str = []
    for i in range(len(folder_name)):
        count_space = 0
        for j in range(len(folder_name[i])):
            if folder_name[i][j] == " " and count_space == 0:
                arr_r_str.append( folder_name[i][:j] )
                count_space += 1

    arr_c_str = []
    for i in range(len(variation_str)):
        for j in range(len(variation_str[i])):
            if variation_str[i][j] == " ":
                arr_c_str.append( variation_str[i][j+1:] )

    fjson.write_keyvalue(file_path, "r_variation", arr_r_str)
    fjson.write_keyvalue(file_path, "c_variation", arr_c_str)

    print("Writing", file_path, "... Done")


if __name__ == "__main__":
    i = 0
    for f in folder_path:
        folder_path[i] = os.path.join(data_path, f)
        i += 1

    for idx in range(len(folder_path)):
        print("Processing %s ..." %folder_name[idx])
        process_analysis(folder_path[idx], fstart=fstart, fend=fend)
        print()