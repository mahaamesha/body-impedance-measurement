import os
import matplotlib.pyplot as plt
from pandas.plotting import table

# file_path = os.path.dirname(__file__)
# project_path = os.path.join(file_path, "../")


def save_df_as_image(df, filename="TB Impedance Phase", saved_dirname=""):
    df.index = ["  %s  " %i for i in range(len(df))] # Format date

    fig, ax = plt.subplots(figsize=(14,len(df)//2)) # set size frame
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    ax.set_frame_on(False)  # no visible frame, uncomment if size is ok

    # tabla = table(ax, df, loc="center", colWidths=[0.24]*len(df.columns))  # where df is your data frame
    tabla = table(ax, df, loc="center")  # where df is your data frame
    tabla.auto_set_font_size(True) # Activate set fontsize manually
    # tabla.set_fontsize(12) # if ++fontsize is necessary ++colWidths
    tabla.scale(1.2, 1.5) # change size table

    fig.suptitle(filename, fontsize="xx-large", weight="bold")

    # save figure
    try:    # for notebook environment
        save_path = os.path.join("../media/", saved_dirname, filename + ".jpg")
        plt.savefig(save_path)
    except: # for local python environment
        save_path = os.path.join("media/", saved_dirname, filename + ".jpg")
        plt.savefig(save_path)

    print("Saving %s.jpg ... Done" %filename)


# df: df_z_phase, df_r_c
def create_markdown_table_from_dataframe(df, filename="TB Impedance Phase", saved_dirname=""):
    # for naming purposes
    try:    # for notebook environment
        path = os.path.join("../media/", saved_dirname, filename + ".md")
        with open(path, "a"): pass
    except: # for local python environment
        path = os.path.join("media/", saved_dirname, filename + ".md")
        with open(path, "a"): pass

    with open(path, "w") as f:
        # write header
        cols = list(df.columns)
        for j in range(len(cols)):  # loop in col
            val = cols[j]
            if "\u03C6" in cols[j]:
                if "_" in cols[j]:
                    val = cols[j].replace("\u03C6", "$\phi$\\")
                else:
                    val = cols[j].replace("\u03C6", "$\phi$")
            f.write( "| " + val + "\t" )

        f.write("|\n")

        for j in range(len(cols)):
            if j == 0: f.write("| :-\t")
            else: f.write("| -:\t")
        f.write("|\n")

        # write body of tables
        for i in range(len(df)):                # loop in rows
            for j in range(len(df.columns)):    # loop in columns
                val = df.iloc[i][j]
                f.write( "| %s\t" %val )
            f.write("|\n")

        # print(df)
        # print( df.iloc[0] )
        # print( df.iloc[0][3] )
    
    print("Build table in %s.md ... Done" %filename)