import os


data_path = "E:/_TUGAS/_ITBOneDrive/OneDrive - Institut Teknologi Bandung/_Kuliah/_sem7/7_kerja praktek/data/pengukuran tangan modul"
folder_name = ["calibration/", "id001 dwi/", "id002 angga/", "id003 avima/", "id004 aldian/"]
folder_path = folder_name.copy()

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
        print("Writing %s ... Done" %file)
        count_file += 1


print("\nSuccesfully writing %s file(s)" %(count_file))