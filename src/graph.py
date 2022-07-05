import matplotlib.pyplot as plt
import os

def graph_per_variation(variation_str, iteration, dfs_list, folder_path_i, 
                        x_data="Frequency", y_data="Impedance",
                        x_label="Frequency (Hz)", y_label="Impedance (Ohm)",
                        suptitle_prefix="Impedance"):
    # plot impedance

    # compare data for each itearation
    fig, axs = plt.subplots(nrows=len(variation_str), figsize=(10,4*len(variation_str)), constrained_layout=True)

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
        save_path = os.path.join("../media/", suptitle_text + ".jpg")
        fig.savefig(save_path)
        plt.show()
    except: # for local python environment
        save_path = os.path.join("media/", suptitle_text + ".jpg")
        fig.savefig(save_path)

    print("Saving %s ... Done" %save_path)