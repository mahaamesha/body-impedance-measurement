import os
import shutil
import sys

from formula import *
import json_function as fjson
import processing as proc
from graph import *
from post_process import *
import internal_factor as infac


data_path = "E:/_TUGAS/_ITBOneDrive/OneDrive - Institut Teknologi Bandung/_Kuliah/_sem7/7_kerja praktek/data/data training 74hc4051"
folder_name = ["data training/"]
folder_path = folder_name.copy()

fstart = 20e3
fend = 50e3


def detect_folder_data_training(data_path):
    # scan all files
    try:
        path, dirs, files = next(os.walk(data_path))
    except:
        sys.exit("Error: Cannot find %s" %data_path)

    # add "/" in last folder_name
    folder_name = []
    for i in range(len(dirs)):
        dirs[i] = str(dirs[i] + "/")
        if "ohm" in dirs[i]:
            folder_name.append(dirs[i])
    
    return folder_name


def copy_all_files_to_data_training_folder(data_path, folder_name):
    target_path = os.path.join(data_path, "data training/")

    for dir in folder_name:
        folder_path = os.path.join(data_path, dir)
        
        # scan all csv file in Rohm/ folder
        path, dirs, files = next(os.walk(folder_path))
        
        # copy file to target_path
        # remember that files is array of string
        for file in files:
            file_path = os.path.join(path, file)

            # if file contains this string, it means the sampling process not already done
            if "Impedance" not in file:
                shutil.copy(file_path, target_path)


def preprocessing_data_training(files):
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

    # convert as float
    for i in range(len(variation_data)):
        variation_data[i] = float(variation_data[i])
    
    return variation_str, variation_data


def get_data_ref(variation_data):
    # theoritic as reference
    arr_z_ref = []
    arr_phase_ref = []
    for i in range(len(variation_data)):
        z_ref = variation_data[i]       # actually its only R, without C
        phase_ref = 0   # ideally a resistor have phase = 0

        arr_z_ref.append(z_ref)
        arr_phase_ref.append(phase_ref)

    return arr_z_ref, arr_phase_ref



def get_arr_err(arr_ref, arr_data):
    arr_err = []

    for i in range(len(arr_ref)):
        err = calculate_error(arr_ref[i], arr_data[i])
        arr_err.append(err)
    
    return arr_err


def update_training_variation_json(variation_str,
                                arr_z_ref, arr_phase_ref,
                                arr_z_mid, arr_phase_mid,
                                arr_z_avg, arr_phase_avg,
                                arr_z_err, arr_phase_err):
    # save important information to json file
    file_path="tmp/training_variation.json"
    obj = {}

    # update value of each key
    for i in range(len(variation_str)):
        obj[variation_str[i]] = {}

        obj[variation_str[i]]["z_ref"] = arr_z_ref[i]
        obj[variation_str[i]]["z_mid"] = arr_z_mid[i]
        obj[variation_str[i]]["z_avg"] = arr_z_avg[i]
        obj[variation_str[i]]["z_err"] = arr_z_err[i]
        obj[variation_str[i]]["phase_ref"] = arr_phase_ref[i]
        obj[variation_str[i]]["phase_mid"] = arr_phase_mid[i]
        obj[variation_str[i]]["phase_avg"] = arr_phase_avg[i]
        obj[variation_str[i]]["phase_err"] = arr_phase_err[i]

    # clear formatting in file json
    data = fjson.read_filejson(file_path)
    if len(data) <= 1:
        fjson.write_obj_to_filejson(file_path, obj={})

    fjson.append_obj_to_filejson(file_path, obj=obj)

    print("Writing", file_path, "... Done")


def process_analysis(folder_path_i, variation_str, dfs_list, iteration):
    saved_dirname = proc.prepare_result_folder(data_path)

    # plot & save figure
    # proc.build_graph_per_variation(variation_str, iteration, dfs_list, folder_path_i, saved_dirname, internal_flag)
    
    
    # get z_mid & phase_mid from every dataframe. data_mid is data at fmid
    # arr = [[...], [...], ...]
    arr_z_mid, arr_phase_mid, dfs_list = proc.get_data_mid(dfs_list, iteration, internal_flag)
    
    # every variation have n dataframes. n = num_of_iteration
    # build single dataframe for every variation by averaging them (from data repetisi)
    # length of df_choosen is same with num_of_variation
    df_choosen = proc.build_df_choosen(dfs_list, iteration)


    # plot & save figure
    proc.build_single_graph_from_df_choosen(df_choosen, variation_str, folder_path_i, saved_dirname, internal_flag)

    # store measurement data as reference value
    arr_z_ref, arr_phase_ref = get_data_ref(variation_data)

    # store data_avg of parameter: z, phase. Stored to variation_json
    arr_z_avg, arr_phase_avg = proc.get_z_phase_avg_from_df_choosen(df_choosen, internal_flag)

    # calculate error of z and phase
    arr_z_err = get_arr_err(arr_z_ref, arr_z_avg)
    arr_phase_err = get_arr_err(arr_phase_ref, arr_phase_avg)       # if using phase_ref = 0, its error will be INFINITY

    # update json file data
    proc.update_overview_json(folder_name, fstart, fend, files, iteration, variation_str, 
                                file_path="tmp/training_overview.json")
    update_training_variation_json(variation_str,
                                    arr_z_ref, arr_phase_ref,
                                    arr_z_mid, arr_phase_mid,
                                    arr_z_avg, arr_phase_avg,
                                    arr_z_err, arr_phase_err)

# considering internal factor
def naming_conditioning_for_image_and_markdown(internal_flag):
    # change filename if considering internal factor
    if not(internal_flag):
        fn1 = "TB Impedance Phase"
        fn2 = "BC Error Value"
    elif internal_flag:
        fn1 = "TB Actual Impedance Phase"
        fn2 = "BC Actual Error Value"

    return fn1, fn2



if __name__ == "__main__":
    folder_data_training_name = detect_folder_data_training(data_path)
    copy_all_files_to_data_training_folder(data_path, folder_data_training_name)


    internal_flag = infac.choose_internal_flag()
    # first, build rc_internal_factor.json
    if internal_flag: infac.get_internal_factor(data_path, file_path="tmp/training_internal_factor.json")


    # start
    # replace path_value in folder_path
    i = 0
    for f in folder_path:
        folder_path[i] = os.path.join(data_path, f)
        i += 1

    # prepare tmp files
    fjson.initialize_training_tmp_files()

    # process analysis
    for idx in range(len(folder_path)):
        print("\nProcessing %s ..." %folder_name[idx])

        # preprocessing
        files, dfs, dfs_list = proc.prepare_data(folder_path[idx])
        if internal_flag:
            dfs_list = proc.create_actual_params_columns(dfs_list, file_path="tmp/training_internal_factor.json")
        variation_str, variation_data = preprocessing_data_training(files)
        saved_dirname = proc.prepare_result_folder(data_path)

        iteration = len(dfs_list) // len(variation_data)

        # main processing
        process_analysis(folder_path[idx], variation_data, dfs_list, iteration)

    print("\nPost processing ...")

    # change filename if considering internal factor
    fn1, fn2 = naming_conditioning_for_image_and_markdown(internal_flag)

    # create dataframe from final file_variation.json
    header = ["variation", "z_ref", "z_avg", "%z", "\u03C6_ref", "\u03C6_avg", "%\u03C6"]
    data_key = ["variation", "z_ref", "z_avg", "z_err", "phase_ref", "phase_avg", "phase_err"]
    df_z_phase = proc.build_df_from_file_json(header, data_key, file_path="tmp/training_variation.json")
    # save as image
    # save_df_as_image(df_z_phase, filename=fn1, saved_dirname=saved_dirname)
    # tabulate dataframe in markdown file
    create_markdown_table_from_dataframe(df_z_phase, filename=fn1, saved_dirname=saved_dirname)

    
    graph_relation_Zerr_and_R(df_z_phase, saved_dirname,
                                x_data="z_avg", y_data="%z",
                                x_label="Measured Impedance (Ohm)", y_label="Impedance Error (%)",
                                suptitle_prefix="Zerr vs Zavg")
    graph_relation_Zerr_and_R(df_z_phase, saved_dirname,
                                x_data="z_avg", y_data="z_ref",
                                x_label="Measured Impedance (Ohm)", y_label="Impedance Reference (Ohm)",
                                suptitle_prefix="Zactual vs Zref")
    
    fjson.clear_filejson(path="tmp/training_model.json")
    model_obj = build_graph_and_model(df_z_phase, saved_dirname, degree_arr=[3, 5, 7],
                                    x_data="z_avg", y_data="%z",
                                    x_label="Measured Impedance (Ohm)", y_label="Impedance Error (%)",
                                    suptitle_prefix="MODEL ERR")
    model_obj = build_graph_and_model(df_z_phase, saved_dirname, degree_arr=[1],
                                    x_data="z_avg", y_data="z_ref",
                                    x_label="Measured Impedance (Ohm)", y_label="Impedance Reference (Ohm)",
                                    suptitle_prefix="MODEL Z")
    
    