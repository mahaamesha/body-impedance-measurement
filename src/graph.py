import matplotlib.pyplot as plt
import os
import pandas as pd
from json_function import append_obj_to_filejson, clear_filejson, read_filejson, write_obj_to_filejson
from olah_repetisi_rc import get_arr_rc_str
import numpy as np
from sklearn.metrics import r2_score


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
    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10,4), constrained_layout=False)

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


def graph_overview_body_composition(saved_dirname, suptitle_text="BC Body Composition"):
    file_path = "tmp/retrieval_body_composition.json"
    data = read_filejson(file_path)

    obj_plot = {}
    # obj_plot = {
    #     "g1": ["ffm", "fm", "tbw"],
    #     "g2": ["ffm", "fm", "tbw"]
    # }

    # body composition labels
    bc_labels = ["ffm_percentage", "fm_percentage", "tbw_percentage"]
    labels = ["FFM", "FM", "TBW"]

    for key in data.keys():
        # create new key: "g1", "g2", ...
        obj_plot[key] = []

        # append body_composition_data to arr: ffm, fm, tbw
        for label in bc_labels:
            obj_plot[key].append( data[key][label] )

    # print(obj_plot)


    # figure and axs
    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(12,8), sharex=True)
    fig.suptitle(suptitle_text, fontsize="xx-large", weight="bold")

    # create dataframe
    df_plot = pd.DataFrame(obj_plot, index=labels)
    # print(df_plot)

    # create bar chart
    df_plot.plot(kind="bar", ax=ax)
    ax.set_ylabel("Percentage (%)")
    ax.grid(True)
    
    # save figure
    try:    # for notebook environment
        save_path = os.path.join("../media/", saved_dirname, suptitle_text + ".jpg")
        fig.savefig(save_path)
        plt.show()
    except: # for local python environment
        save_path = os.path.join("media/", saved_dirname, suptitle_text + ".jpg")
        fig.savefig(save_path)

    print("Saving %s ... Done" %(suptitle_text + ".jpg"))


# i use this in training_data.py
# i have variation of R, %Z
# i want to plot %Z vs R
def graph_relation_Z(df, saved_dirname,
                                x_data="z_ref", y_data="%z",
                                x_label="Impedance Reference (Ohm)", y_label="Impedance Error (%)",
                                suptitle_prefix="ZR"):

    # convert column in dataframe from string/object to float
    df[x_data] = pd.to_numeric(df[x_data], downcast="float")
    df[y_data] = pd.to_numeric(df[y_data], downcast="float")

    # sort by x_data column
    df = df.sort_values(by=[x_data], ascending=True)
    # print(df)

    # plot data
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10,4), constrained_layout=False)
    
    df.plot(x=x_data, y=y_data, ax=ax)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(True)


    suptitle_text = suptitle_prefix + " - " + saved_dirname[:-1]
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


# i use this in training_data.py
def build_graph_and_model(df, saved_dirname, degree_arr=[3, 5, 7],
                x_data="z_avg", y_data="%z",
                x_label="Impedance Reference (Ohm)", y_label="Impedance Error (%)",
                suptitle_prefix="MODEL"):

    # figure and axis
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10,4), constrained_layout=False)

    model_obj = {}
    idx = 0

    x = df[x_data]
    y = df[y_data]
    ax.scatter(x, y, color="gray")

    model_obj = {}

    for degree in degree_arr:
        # build model
        mymodel = np.poly1d(np.polyfit(x, y, degree))
        mymodel_coef = list( np.polyfit(x, y, degree) )     # if ax^2 + bx^1 + cx^0 --> arr = [a, b, c]
        # r-square value
        r2_score_value = r2_score(y, mymodel(x))
        # store model to obj
        tmp_model_obj = {"%s_%s" %((suptitle_prefix.lower()).replace(" ", "_"), idx+1): {"degree": degree, "model_coef": mymodel_coef, "r_square": r2_score_value}}
        append_obj_to_filejson(file_path="tmp/training_model.json", obj=tmp_model_obj)
        model_obj.update(tmp_model_obj)
        
        myline = np.linspace(min(x), max(x), len(x)*100)

        # plot data
        r2_score_value = "{:.2f}".format(r2_score_value)
        ax.plot(myline, mymodel(myline), label="degree %s, R²=%s" %(degree, r2_score_value))

        idx += 1
    
    # store model to JSON file
    # print(model_obj)
    # append_obj_to_filejson(file_path="tmp/training_model.json", obj=model_obj)
    
    # set properties
    ax.legend()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(True)

    suptitle_text = suptitle_prefix + " - " + saved_dirname[:-1]
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
    
    return model_obj


def barchart_compare(df, saved_dirname,
                    x_data="variation", y_data=["%z", "%z_model"],
                    x_label="Variation", y_label="Impedance Error (%)",
                    suptitle_prefix="COMPARE ERR"):
    index_arr = list( df[x_data] )

    # i need to build obj for barchart data
    # {"key1": [], "key2": [], ...}
    plot_obj = {}
    for var in y_data:
        arr = []
        for n in list(df[var]):
            arr.append(n)
                
        # update to obj
        plot_obj.update( {var: arr} )

    # build bar chart
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10,5), constrained_layout=True)
    
    df_plot = pd.DataFrame(plot_obj, index=index_arr)
    df_plot.plot(kind="bar", ax=ax)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(True)

    suptitle_text = suptitle_prefix + " - " + saved_dirname[:-1]
    fig.suptitle(suptitle_text, fontsize="xx-large", weight="bold")

    # add text
    str_text = ""
    idx = 0
    pading = (plt.axis()[3] - plt.axis()[2]) / 10
    for var in y_data:
        min_val = "{:.2f}".format( min( list(df[var]) ) )
        max_val = "{:.2f}".format( max( list(df[var]) ) )
        str_text = "%s: (%s - %s)" %(var, min_val, max_val) + "%"
        ax.text(x=int(plt.axis()[1]*2/3), y=int(plt.axis()[3]*1/2 - pading*idx), s=str_text, fontsize="x-large")
        idx += 1

    # save figure
    try:    # for notebook environment
        save_path = os.path.join("../media/", saved_dirname, suptitle_text + ".jpg")
        fig.savefig(save_path)
        plt.show()
    except: # for local python environment
        save_path = os.path.join("media/", saved_dirname, suptitle_text + ".jpg")
        fig.savefig(save_path)

    print("Saving %s ... Done" %suptitle_text)