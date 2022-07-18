import matplotlib.pyplot as plt
import os
import pandas as pd
from json_function import read_filejson
from olah_repetisi_rc import get_arr_rc_str


def graph_per_variation(variation_str, iteration, dfs_list, folder_path_i, saved_dirname="",
                        x_data="Frequency", y_data="Impedance",
                        x_label="Frequency (Hz)", y_label="Impedance (Ohm)",
                        suptitle_prefix="Impedance"):

    # figure and axs
    fig, axs = plt.subplots(ncols=1, nrows=len(variation_str), figsize=(10,4*len(variation_str)), constrained_layout=True)

    count = 1   # to multiply the second loop (iteration)
    for ax in axs:
        for i in range(iteration*(count-1), iteration*count):
            # print(i//iteration, arr_title[i//iteration])
            label_idx = (i+1) - iteration*(count-1)
            dfs_list[i].plot(x=x_data, y=y_data, label="iteration (%s)" %label_idx, ax=ax)

            if i == iteration*count - 1:
                ax.set_title(variation_str[i//iteration], weight="bold")
        # print()
        count += 1

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(True)

    # add figure title
    length = len( folder_path_i )-1
    suptitle_sufix = ""
    for i in range( length, 0, -1):
        if folder_path_i[i] == "\\":
            suptitle_sufix = folder_path_i[i+1:length]
            break

    suptitle_text = suptitle_prefix + " - " + suptitle_sufix

    fig.suptitle(suptitle_text, fontsize="xx-large", weight="bold")


    # save figure
    try:    # for notebook environment
        save_path = os.path.join("../media/", saved_dirname, suptitle_text + ".jpg")
        fig.savefig(save_path)
        plt.show()
    except: # for local python environment
        save_path = os.path.join("media/", saved_dirname, suptitle_text + ".jpg")
        fig.savefig(save_path)

    print("Saving %s ... Done" %suptitle_text)



# create single graph use dataframes in df_choosen
# df_choosen is array to store averaged dataframe from every variation
# df_choosen normalize all dataframe from all iteration in one variation
def single_graph_from_df_choosen(df_choosen, variation_str, folder_path_i, saved_dirname="",
                                x_data="Frequency", y_data="Impedance",
                                x_label="Frequency (Hz)", y_label="Impedance (Ohm)",
                                suptitle_prefix="SG"):

    # figure and axs
    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10,4), constrained_layout=True)

    idx = 0
    for df in df_choosen:
        df.plot(x=x_data, y=y_data, label=variation_str[idx], ax=ax)

        idx += 1
    
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(True)

    
    # add figure title
    length = len( folder_path_i )-1
    count = 0
    slash_position = []     # store position of "\\"
    suptitle_sufix = ""
    for i in range( length, 0, -1):
        if (folder_path_i[i] == "\\" or folder_path_i[i] == "/") and count < 2:
            slash_position.append(i)
            count += 1
            if count == 2:
                suptitle_sufix = folder_path_i[slash_position[1]+1:slash_position[0]]

    suptitle_text = suptitle_prefix + " - " + suptitle_sufix

    fig.suptitle(suptitle_text, fontsize="xx-large", weight="bold")


    # save figure
    try:    # for notebook environment
        save_path = os.path.join("../media/", saved_dirname, suptitle_text + ".jpg")
        fig.savefig(save_path)
        plt.show()
    except: # for local python environment
        save_path = os.path.join("media/", saved_dirname, suptitle_text + ".jpg")
        fig.savefig(save_path)

    print("Saving %s ... Done" %suptitle_text)


def graph_to_overview_error_value(variation_str, saved_dirname, y_data="z_err", title="Impedance Error"):
    data = read_filejson(file_path="tmp/rc_variation.json")
    vals = list(data.values())

    # for index in bar chart
    arr_r_str, arr_c_str = get_arr_rc_str(variation_str)
    arr_c_str.insert(0, "without C")
    # print(arr_r_str)
    # print(arr_c_str)

    # build data for plot bar chart
    # num_of_variation_c bar per index x
    # if num_of_variation_c = 7 and num_of_variaton_r = 3
    # obj_plot = {
    #     "c1": ["r1", "r2", "r3"],
    #     "c2": ["r1", "r2", "r3"]
    # }

    # prepare error data as arrays
    # arr_err = [i for i in range(len(data))]       # only for checking
    arr_err = []
    for val in vals:
        # check data_key in val. val is object that store all parameters
        for data_key in val.keys():
            # check if data_key contain "err". i want to get error value only
            # because err value from data_theoryref is almost 0, i only concern in data_theoryavg
            if ("err" in data_key) and ("ref" not in data_key):
                # because data_theoryavg is long enough, check wheter y_data in data_key
                if y_data in data_key:
                    arr_err.append( val[data_key] )


    # build obj_plot. it used in dataframe. graph require dataframe
    obj_plot = {}
    for c in range(len(arr_c_str)):
        key = arr_c_str[c]
        obj_plot[key] = []
        for r in range(len(arr_r_str)):
            idx = r * len(arr_c_str) + c
            err_value = arr_err[idx]
            obj_plot[key].append( err_value )

        # print(obj_plot)
            

    # plot obj_plot to bar chart
    df_plot = pd.DataFrame(obj_plot, index=arr_r_str)

    df_plot.plot(kind="bar")
    plt.title("BC %s" %title)
    plt.ylabel(title + " (%)")
    plt.grid(True)
    plt.tight_layout()
    
    # save figure
    try:    # for notebook environment
        save_path = os.path.join("../media/", saved_dirname, "BC %s.jpg" %title)
        plt.savefig(save_path)
        plt.show()
    except: # for local python environment
        save_path = os.path.join("media/", saved_dirname, "BC %s.jpg" %title)
        plt.savefig(save_path)

    print("Saving %s ... Done" %("BC %s.jpg" %title))


def graph_to_overview_error_value_batch(variation_str, saved_dirname, 
                                        y_data=["z_err", "phase_err", "r_err", "c_err"], 
                                        title=["Impedance Error", "Phase Error", "R Value Error", "C Value Error"],
                                        filename="BC Error Value"):
    data = read_filejson(file_path="tmp/rc_variation.json")
    vals = list(data.values())

    # for index in bar chart
    arr_r_str, arr_c_str = get_arr_rc_str(variation_str)
    arr_c_str.insert(0, "without C")
    # print(arr_r_str)
    # print(arr_c_str)

    # build data for plot bar chart
    # num_of_variation_c bar per index x
    # if num_of_variation_c = 7 and num_of_variaton_r = 3
    # obj_plot = {
    #     "c1": ["r1", "r2", "r3"],
    #     "c2": ["r1", "r2", "r3"]
    # }

    # prepare error data as arrays
    # arr_err = [i for i in range(len(data))]       # only for checking
    arr_err = [ [] for i in range(len(y_data)) ]
    # print(arr_err)
    

    for val in vals:
        # check data_key in val. val is object that store all parameters
        for data_key in val.keys():
            # check if data_key contain "err". i want to get error value only
            # because err value from data_theoryref is almost 0, i only concern in data_theoryavg
            if ("err" in data_key) and ("ref" not in data_key):
                # because data_theoryavg is long enough, check wheter y_data in data_key
                for i in range(len(y_data)):
                    if y_data[i] in data_key:
                        arr_err[i].append( val[data_key] )
                    # print(arr_err)
    # print(len(arr_err))


    # figure and axs
    fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(14,5*2), sharex=True)

    # build obj_plot. it used in dataframe. graph require dataframe
    for param in range(len(arr_err)):       # if I loop it by param, I will have obj_plot for every param in y_data
        obj_plot = {}
        for c in range(len(arr_c_str)):
            key = arr_c_str[c]
            obj_plot[key] = []
            for r in range(len(arr_r_str)):
                idx = r * len(arr_c_str) + c
                err_value = arr_err[param][idx]
                obj_plot[key].append( err_value )

            # print(obj_plot)
        # print( len(obj_plot) )

        
        # after I store df of each param in obj_plot, I need directly plot it before next iteration
        # plot obj_plot to bar chart
        df_plot = pd.DataFrame(obj_plot, index=arr_r_str)

        # convert 0 = 00   1 = 01   2 = 10  3 = 11
        def convert_to_bin(param):
            bin = (0,0)     #(i,j) --> (i*2, j*1) = i*2 + j
            for i in range(2):
                for j in range(2):
                    sum = i*2 + j
                    if sum == param:
                        bin = (i,j)
                        return bin
        bin = convert_to_bin(param)
        df_plot.plot(kind="bar", ax=axs[bin[0]][bin[1]])
        axs[bin[0]][bin[1]].set_title("BC %s" %title[param])
        axs[bin[0]][bin[1]].set_ylabel(title[param] + " (%)")
        axs[bin[0]][bin[1]].grid(True)
        
    

    # save figure
    try:    # for notebook environment
        save_path = os.path.join("../media/", saved_dirname, filename + ".jpg")
        fig.savefig(save_path)
        plt.show()
    except: # for local python environment
        save_path = os.path.join("media/", saved_dirname, filename + ".jpg")
        fig.savefig(save_path)

    print("Saving %s ... Done" %(filename + ".jpg"))