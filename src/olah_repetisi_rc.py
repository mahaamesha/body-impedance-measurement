import os
import pandas as pd

from formula import *
import json_function as fjson
from graph import *
from post_process import *
from internal_factor import get_internal_factor


data_path = "E:/_TUGAS/_ITBOneDrive/OneDrive - Institut Teknologi Bandung/_Kuliah/_sem7/7_kerja praktek/data/repetisi RC"
folder_name = ["465ohm variasi C/", "1003ohm variasi C/", "1468ohm variasi C/"]
folder_path = folder_name.copy()

fstart = 20e3
fend = 50e3

internal_flag = False


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


# revise z and phase value by internal factor
def create_actual_params_columns(dfs_list):
    # load data internal factor
    file_path="tmp/rc_internal_factor.json"
    data = fjson.read_filejson(file_path)

    for df in dfs_list:         # loop in each dataframe
        # create new column
        df["Actual Z"] = 0
        df["Actual Phase"] = 0

        for row in range(len(df)):      # loop in each row
            # assign actual value
            df.loc[row, "Actual Z"] = df.loc[row, "Impedance"] - data["delta_z"][row]
            df.loc[row, "Actual Phase"] = df.loc[row, "Phase"] - data["delta_phase"][row]
            # print( df.loc[row, "Impedance"], data["delta_z"][row] )

        # print(df)
    return dfs_list


def preprocessing_rc_data(files):
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
    
    return variation_str, variation_data


def get_data_ref(variation_data):
    # theoritic as reference
    fmid = calculate_fmid(fstart, fend)
    arr_z_ref = []
    arr_phase_ref = []
    for i in range(len(variation_data)):
        r = variation_data[i][0]
        c = variation_data[i][1]
        xc = calculate_xc(fmid, c)
        z = calculate_z(r, xc)
        phase = calculate_phase(fmid, r, c)

        arr_z_ref.append(z)
        arr_phase_ref.append(phase)

    return arr_z_ref, arr_phase_ref


def create_error_z_column(arr_z_ref, dfs_list, iteration):
    # calculate error Z
    i = 0
    for df in dfs_list:
        if not(internal_flag):
            df["%Z"] = calculate_error(arr_z_ref[i//iteration], df["Impedance"])
        elif internal_flag:
            df["%Zactual"] = calculate_error(arr_z_ref[i//iteration], df["Actual Z"])
        i += 1

    return dfs_list


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
        
        if not(internal_flag):
            arr_z_mid[idx].append( df["Impedance"][nrows//2] )
            arr_phase_mid[idx].append( df["Phase"][nrows//2] )
        elif internal_flag:
            arr_z_mid[idx].append( df["Actual Z"][nrows//2] )
            arr_phase_mid[idx].append( df["Actual Phase"][nrows//2] )

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


def build_graph_per_variation(variation_str, iteration, dfs_list, folder_path_i, saved_dirname):
    if not(internal_flag):
        # plot & save figure
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
    elif internal_flag:
        # plot & save figure
        graph_per_variation(variation_str, iteration, dfs_list, folder_path_i, saved_dirname,
                        x_data="Frequency", y_data="%Zactual",
                        x_label="Frequency (Hz)", y_label="Impedance Error (%)",
                        suptitle_prefix="%Zactual vs f")
        graph_per_variation(variation_str, iteration, dfs_list, folder_path_i, saved_dirname,
                        x_data="Frequency", y_data="Actual Z",
                        x_label="Frequency (Hz)", y_label="Impedance (Ohm)",
                        suptitle_prefix="Actual Impedance")
        graph_per_variation(variation_str, iteration, dfs_list, folder_path_i, saved_dirname,
                        x_data="Frequency", y_data="Actual Phase",
                        x_label="Frequency (Hz)", y_label="Phase (°)",
                        suptitle_prefix="Actual Phase")


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


def build_single_graph_from_df_choosen(df_choosen, variation_str, folder_path_i, saved_dirname):
    if not(internal_flag):
        # plot & save figure
        single_graph_from_df_choosen(df_choosen, variation_str, folder_path_i, saved_dirname,
                                    x_data="Frequency", y_data="Impedance",
                                    x_label="Frequency (Hz)", y_label="Impedance (Ohm)",
                                    suptitle_prefix="SG Impedance")

        single_graph_from_df_choosen(df_choosen, variation_str, folder_path_i, saved_dirname,
                                    x_data="Frequency", y_data="Phase",
                                    x_label="Frequency (Hz)", y_label="Phase (°)",
                                    suptitle_prefix="SG Phase")
    elif internal_flag:
        # plot & save figure
        single_graph_from_df_choosen(df_choosen, variation_str, folder_path_i, saved_dirname,
                                    x_data="Frequency", y_data="Actual Z",
                                    x_label="Frequency (Hz)", y_label="Impedance (Ohm)",
                                    suptitle_prefix="SG Actual Impedance")

        single_graph_from_df_choosen(df_choosen, variation_str, folder_path_i, saved_dirname,
                                    x_data="Frequency", y_data="Actual Phase",
                                    x_label="Frequency (Hz)", y_label="Phase (°)",
                                    suptitle_prefix="SG Actual Phase")


def get_z_phase_avg_from_df_choosen(df_choosen):
    # save mid value from averaged_dataframe
    # array to store mid value of z from every averaged_dataframe
    arr_z_avg = []
    arr_phase_avg = []

    nrows = len(df_choosen[0])
    for df in df_choosen:
        if not(internal_flag):
            arr_z_avg.append( df["Impedance"][nrows//2] )
            arr_phase_avg.append( df["Phase"][nrows//2] )
        elif internal_flag:
            arr_z_avg.append( df["Actual Z"][nrows//2] )
            arr_phase_avg.append( df["Actual Phase"][nrows//2] )
    
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


def get_arr_err(arr_ref, arr_data):
    arr_err = []

    for i in range(len(arr_ref)):
        err = calculate_error(arr_ref[i], arr_data[i])
        arr_err.append(err)
    
    return arr_err


def get_arr_rc_value(variation_data):
    arr_r_value = []
    arr_c_value = []

    # variation_data = [[R1, C1], [R2, C2], ...]
    for i in range(len(variation_data)):
        r_value = variation_data[i][0]
        c_value = variation_data[i][1]

        arr_r_value.append(r_value)
        arr_c_value.append(c_value)
    
    return arr_r_value, arr_c_value


def get_arr_rc_str(variation_str):
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

    return arr_r_str, arr_c_str


def get_rc_value_theoryavg_theoryref(arr_z_avg, arr_phase_avg, arr_z_ref, arr_phase_ref, variation_data):
    # value of r and c from measurement
    arr_r_value, arr_c_value = get_arr_rc_value(variation_data)
    # array of r theory calculated from data: z_avg, phase_avg
    arr_r_theory_avg, arr_c_theory_avg = get_rc_value(arr_z_avg, arr_phase_avg, fmid=calculate_fmid(fstart, fend))
    # array of r theory calculated from data: z_ref, phase_ref
    arr_r_theory_ref, arr_c_theory_ref = get_rc_value(arr_z_ref, arr_phase_ref, fmid=calculate_fmid(fstart, fend))

    return arr_r_value, arr_c_value,\
            arr_r_theory_avg, arr_c_theory_avg,\
            arr_r_theory_ref, arr_c_theory_ref


def get_arr_err_from_all_parameters(arr_z_ref, arr_z_avg, arr_phase_ref, arr_phase_avg, variation_data):
    # calculate error of z and phase
    arr_z_err = get_arr_err(arr_z_ref, arr_z_avg)
    arr_phase_err = get_arr_err(arr_phase_ref, arr_phase_avg)

    arr_r_value, arr_c_value,\
        arr_r_theory_avg, arr_c_theory_avg,\
        arr_r_theory_ref, arr_c_theory_ref = \
        get_rc_value_theoryavg_theoryref(arr_z_avg, arr_phase_avg, arr_z_ref, arr_phase_ref, variation_data)

    # calculate error of r and c
    arr_rtheoryref_err = get_arr_err(arr_r_value, arr_r_theory_ref)
    arr_ctheoryref_err = get_arr_err(arr_c_value, arr_c_theory_ref)
    arr_rtheoryavg_err = get_arr_err(arr_r_value, arr_r_theory_avg)
    arr_ctheoryavg_err = get_arr_err(arr_c_value, arr_c_theory_avg)

    return arr_z_err, arr_phase_err,\
            arr_rtheoryref_err, arr_ctheoryref_err,\
            arr_rtheoryavg_err, arr_ctheoryavg_err


def update_rc_variation_json(variation_str, variation_data,
                            arr_z_ref, arr_phase_ref,
                            arr_z_mid, arr_phase_mid,
                            arr_z_avg, arr_phase_avg,
                            arr_z_err, arr_phase_err,
                            arr_r_theory_ref, arr_c_theory_ref,
                            arr_r_theory_avg, arr_c_theory_avg,
                            arr_rtheoryref_err, arr_ctheoryref_err,
                            arr_rtheoryavg_err, arr_ctheoryavg_err):
    # save important information to json file
    file_path="tmp/rc_variation.json"
    obj = {}

    # update value of each key
    for i in range(len(variation_data)):
        obj[variation_str[i]] = {}
        
        obj[variation_str[i]]["r"] = variation_data[i][0]
        obj[variation_str[i]]["c"] = variation_data[i][1]
        obj[variation_str[i]]["z_ref"] = arr_z_ref[i]
        obj[variation_str[i]]["z_mid"] = arr_z_mid[i]
        obj[variation_str[i]]["z_avg"] = arr_z_avg[i]
        obj[variation_str[i]]["z_err"] = arr_z_err[i]
        obj[variation_str[i]]["phase_ref"] = arr_phase_ref[i]
        obj[variation_str[i]]["phase_mid"] = arr_phase_mid[i]
        obj[variation_str[i]]["phase_avg"] = arr_phase_avg[i]
        obj[variation_str[i]]["phase_err"] = arr_phase_err[i]

        obj[variation_str[i]]["r_ref"] = arr_r_theory_ref[i]
        obj[variation_str[i]]["r_avg"] = arr_r_theory_avg[i]
        obj[variation_str[i]]["r_err_theoryref_measurement"] = arr_rtheoryref_err[i]
        obj[variation_str[i]]["r_err_theoryavg_measurement"] = arr_rtheoryavg_err[i]
        
        obj[variation_str[i]]["c_ref"] = arr_c_theory_ref[i]
        obj[variation_str[i]]["c_avg"] = arr_c_theory_avg[i]
        obj[variation_str[i]]["c_err_theoryref_measurement"] = arr_ctheoryref_err[i]
        obj[variation_str[i]]["c_err_theoryavg_measurement"] = arr_ctheoryavg_err[i]


    # clear formatting in file json
    data = fjson.read_filejson(file_path)
    if len(data) <= 1:
        fjson.write_obj_to_filejson(file_path, obj={})

    fjson.append_obj_to_filejson(file_path, obj=obj)

    print("Writing", file_path, "... Done")


def update_rc_overview_json(files, iteration, variation_str):
    # save important information to json file
    file_path = "tmp/rc_overview.json"

    fjson.write_keyvalue(file_path, "sweep_frequency", [fstart, fend])
    fjson.write_keyvalue(file_path, "num_variation", len(files)//iteration)
    fjson.write_keyvalue(file_path, "num_iteration", iteration)
    fjson.write_keyvalue(file_path, "folder_path", folder_name)

    arr_r_str, arr_c_str = get_arr_rc_str(variation_str)
    fjson.write_keyvalue(file_path, "r_variation", arr_r_str)
    fjson.write_keyvalue(file_path, "c_variation", arr_c_str)

    print("Writing", file_path, "... Done")


def build_df_from_file_json(header, data_key, file_path="tmp/rc_variation.json"):
    data = fjson.read_filejson(file_path)

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


def process_analysis(folder_path_i, variation_data, dfs_list, iteration):
    arr_z_ref, arr_phase_ref = get_data_ref(variation_data)

    dfs_list = create_error_z_column(arr_z_ref, dfs_list, iteration)


    saved_dirname = prepare_result_folder(data_path)
    
    # plot & save figure
    build_graph_per_variation(variation_str, iteration, dfs_list, folder_path_i, saved_dirname)

    
    arr_z_mid, arr_phase_mid, dfs_list = get_data_mid(dfs_list, iteration)
    
    # every variation have n dataframes. n = num_of_iteration
    # build single dataframe for every variation by averaging them
    df_choosen = build_df_choosen(dfs_list, iteration)

    # plot & save figure
    build_single_graph_from_df_choosen(df_choosen, variation_str, folder_path_i, saved_dirname)


    # store data_avg of parameter: z, phase. Stored to variatioin_rc_json
    arr_z_avg, arr_phase_avg = get_z_phase_avg_from_df_choosen(df_choosen)

    arr_r_value, arr_c_value, \
        arr_r_theory_avg, arr_c_theory_avg, \
        arr_r_theory_ref, arr_c_theory_ref = \
        get_rc_value_theoryavg_theoryref(arr_z_avg, arr_phase_avg, arr_z_ref, arr_phase_ref, variation_data)

    arr_z_err, arr_phase_err, \
        arr_rtheoryref_err, arr_ctheoryref_err, \
        arr_rtheoryavg_err, arr_ctheoryavg_err = \
        get_arr_err_from_all_parameters(arr_z_ref, arr_z_avg, arr_phase_ref, arr_phase_avg, variation_data)

    
    update_rc_overview_json(files, iteration, variation_str)
    update_rc_variation_json(variation_str, variation_data,
                            arr_z_ref, arr_phase_ref,
                            arr_z_mid, arr_phase_mid,
                            arr_z_avg, arr_phase_avg,
                            arr_z_err, arr_phase_err,
                            arr_r_theory_ref, arr_c_theory_ref,
                            arr_r_theory_avg, arr_c_theory_avg,
                            arr_rtheoryref_err, arr_ctheoryref_err,
                            arr_rtheoryavg_err, arr_ctheoryavg_err)


def prepare_df_from_rc_variation_json():
    header = ["variation", "z_ref", "z_avg", "%z", "\u03C6_ref", "\u03C6_avg", "%\u03C6"]
    data_key = ["variation", "z_ref", "z_avg", "z_err", "phase_ref", "phase_avg", "phase_err"]
    df_z_phase = build_df_from_file_json(header, data_key, file_path="tmp/rc_variation.json")

    header = ["variation", "r_ref", "%r_ref", "r_avg", "%r_avg",
                            "c_ref", "%c_ref", "c_avg", "%c_avg"]
    data_key = ["variation", "r_ref", "r_err_theoryref_measurement", "r_avg", "r_err_theoryavg_measurement",
                            "c_ref", "c_err_theoryref_measurement", "c_avg", "c_err_theoryavg_measurement",]
    df_r_c = build_df_from_file_json(header, data_key, file_path="tmp/rc_variation.json")

    return df_z_phase, df_r_c


# considering internal factor
def naming_conditioning_for_image_and_markdown():
    # change filename if considering internal factor
    if not(internal_flag):
        fn1 = "TB Impedance Phase"
        fn2 = "TB RC Value"
        fn3 = "BC Error Value"
    elif internal_flag:
        fn1 = "TB Actual Impedance Phase"
        fn2 = "TB Actual RC Value"
        fn3 = "BC Actual Error Value"

    return fn1, fn2, fn3



if __name__ == "__main__":
    # first, build rc_internal_factor.json
    if internal_flag: get_internal_factor()

    # start
    # replace path_value in folder_path
    i = 0
    for f in folder_path:
        folder_path[i] = os.path.join(data_path, f)
        i += 1

    # prepare tmp files
    fjson.initialize_rc_tmp_files()

    # process analysis
    for idx in range(len(folder_path)):
        print("\nProcessing %s ..." %folder_name[idx])

        # preprocessing
        files, dfs, dfs_list = prepare_data(folder_path[idx])
        dfs_list = create_actual_params_columns(dfs_list)
        variation_str, variation_data = preprocessing_rc_data(files)
        saved_dirname = prepare_result_folder(data_path)

        iteration = len(dfs_list) // len(variation_data)

        # main processing
        process_analysis(folder_path[idx], variation_data, dfs_list, iteration)


    # create dataframe from final rc_variation.json
    df_z_phase, df_r_c = prepare_df_from_rc_variation_json()
    
    # save them as image and markdown file
    fn1, fn2, fn3 = naming_conditioning_for_image_and_markdown()
    
    # save them as image
    save_df_as_image(df_z_phase, filename=fn1, saved_dirname=saved_dirname)
    save_df_as_image(df_r_c, filename=fn2, saved_dirname=saved_dirname)
    # tabulate dataframe in markdown file
    create_markdown_table_from_dataframe(df_z_phase, filename=fn1, saved_dirname=saved_dirname)
    create_markdown_table_from_dataframe(df_r_c, filename=fn2, saved_dirname=saved_dirname)

    # make bar chart to compare error
    y_data = ["z_err", "phase_err", "r_err", "c_err"]
    title = ["Impedance Error", "Phase Error", "R Value Error", "C Value Error"]
    graph_to_overview_error_value_batch(variation_str, saved_dirname, y_data, title, filename=fn3)