import matplotlib.pyplot as plt
import os

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