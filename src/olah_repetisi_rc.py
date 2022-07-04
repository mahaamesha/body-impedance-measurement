import os
import pandas as pd


data_path = "E:/_TUGAS/_ITBOneDrive/OneDrive - Institut Teknologi Bandung/_Kuliah/_sem7/7_kerja praktek/data/repetisi RC"
folder_path = ["465ohm variasi C/", "1003ohm variasi C/", "1468ohm variasi C/"]

i = 0
for f in folder_path:
    folder_path[i] = os.path.join(data_path, f)
    print(folder_path[i])
    i += 1


# scan all files
path, dirs, files = next(os.walk(folder_path[1]))
# create empty list
df_list = []

for file in files:
    print(file)


# append datasets to the list
for i in range(len(files)):
    temp_df = pd.read_csv(folder_path[1]+files[i])
    df_list.append(temp_df)

    print(df_list[i].head())


# CLEANING NaN
for df in df_list:
    # get the column list
    for col in df.columns:
        print(col)