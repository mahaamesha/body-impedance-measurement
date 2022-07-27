import os
import pandas as pd
from math import atan, pi


data_path = "E:/_TUGAS/_ITBOneDrive/OneDrive - Institut Teknologi Bandung/_Kuliah/_sem7/7_kerja praktek/data/pengukuran tangan modul"
folder_name = ["calibration/", "id001 dwi/", "id002 angga/", "id003 avima/", "id004 aldian/"]
folder_path = folder_name.copy()


# this works if
# initial   : Frequency, Real, Imaginer, Impedance
# i want    : Frequency,Real,Imaginer,Impedance
def conditioning_header(file_path, file):
# read data and change the header
    with open(file_path, "r") as f:
        data = f.read()
        
        # detect header of each csv file
        idx = 0
        while not(data[idx].isnumeric()):
            idx += 1
            
            if data[idx].isnumeric():
                str_head = data[:idx-1]
                # print(str_head)

                # delete space in header
                # initial   : Frequency, Real, Imaginer, Impedance
                # i want    : Frequency,Real,Imaginer,Impedance
                for c in str_head:
                    if c == " ":
                        str_head = str_head.replace(" ", "")
                str_data = str_head + "\n" + data[idx:]
    
    # write file
    with open(file_path, "w") as f:
        f.write(str_data)

    # notification
    # print("Conditioning header: %s ... Done" %file)


def move_column_position(file_path, column, index):
    with open(file_path, "r") as f:
        df = pd.read_csv(f)

        if df.columns[index] != column:
            col_data = df.pop( str(column) )

            df.insert(loc=index, column=column, value=col_data)

            # write it to csv file
            df.to_csv(file_path, index=False)

        # print(df)


# i need this because, in first raw data, 
# i only have FREQ, REAL, IMAG, IMPEDANCE
# so i need to calculate PHASE from REAL & IMAG
def conditioning_phase(file_path, file):
    with open(file_path, "r") as f:
        df = pd.read_csv(f)

        # add phase column
        try:
            df.insert(loc=2, column="Phase", value=0)
        except:
            # print("Column \"Phase\" already exist.")
            pass
        
        # access every REAL & IMAG value, then calculate PHASE
        for row in range(len(df)):
            real = df["Real"][row]
            imag = df["Imaginer"][row]

            # check quadrant to calculate phase
            if real > 0 and imag > 0:   # quadrant 1
                phase = atan(imag/real) * 180 / pi
            elif real < 0 and imag > 0: # quadrant 2
                phase = atan(imag/real) * 180 / pi + 180
            elif real < 0 and imag < 0: # quadrant 3
                phase = atan(imag/real) * 180 / pi + 180
            elif real > 0 and imag < 0: # quadrant 4
                phase = atan(imag/real) * 180 / pi + 360

            # assign value of phase
            phase = "{:.2f}".format(phase)
            df.loc[row, "Phase"] = float(phase)

        # write to csv file
        df.to_csv(file_path, index=False)

        # print(df)
    
    # notification
    # print("Add phase column: %s ... Done" %file)


def process_csv_conditioning(data_path, folder_path):
    print("Running %s ..." %("csv_conditioning.py"))

    # add calibration for this file purpose only
    if "calibration/" not in folder_path:
        folder_path.insert(0, "calibration/")

    i = 0
    for f in folder_path:
        folder_path[i] = os.path.join(data_path, f)
        # print(folder_path[i])
        i += 1

    count_file = 0
    for folder_path_i in folder_path:
        # scan all files
        path, dirs, files = next(os.walk(folder_path_i))

        for file in files:
            # print(file)

            file_path = os.path.join(folder_path_i, file)
            # print(file_path)

            conditioning_header(file_path, file)
            move_column_position(file_path, column="Impedance", index=1)
            conditioning_phase(file_path, file)

            count_file += 1

    print("Succesfully writing %s file(s)" %(count_file))


def choose_csv_conditioning(data_path, folder_path):
    flag = True
    while flag:
        key = str( input("Run %s? (y/n) " %("csv_conditioning.py")) )

        if key == "y":
            flag = False
            process_csv_conditioning(data_path, folder_path)
        elif key == "n":
            flag = False


if __name__ == "__main__":
    choose_csv_conditioning(data_path, folder_path)