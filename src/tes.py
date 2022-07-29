import os, sys
import shutil

data_path = "E:/_TUGAS/_ITBOneDrive/OneDrive - Institut Teknologi Bandung/_Kuliah/_sem7/7_kerja praktek/data/data training 74hc4051"
folder_name = ["data training/"]
folder_path = folder_name.copy()


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


folder_name = detect_folder_data_training(data_path)
copy_all_files_to_data_training_folder(data_path, folder_name)