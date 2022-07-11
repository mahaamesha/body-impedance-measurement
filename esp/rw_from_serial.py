import os
import sys
import serial

# arduino_port = "/dev/cu.usbmodem14201"      # for mac
arduino_port = "COM4"   # for windows
baud = 9600 #arduino uno runs at 9600 baud
path = "D:/My_Project/body-impedance-measurement/esp/data_retrieved"
file_name = "analog-data.csv" #name of the CSV file generated
file_path = os.path.join(path, file_name)

# used as mark if the system want to start next sweeping
complete_text = "Frequency sweep complete!"

# header contains parameters want to saved
header = ["Frequency", "Real", "Imaginer", "Impedance"]


ser = serial.Serial(arduino_port, baud)
print("Connected to Arduino port:" + arduino_port)

#add the data to the file
flag = False    # is start to write data?
while True:
    #display the data to the terminal
    getData = str(ser.readline())
    data = getData[0:][:-4]
    data = getData[2:-5]

    if data == complete_text:
        key = 0
        while (key != "y") and (key != "n"):
            key = input("Retrieve data? (y/n)")
            
            # if yes, clear the file first
            if key == "y":
                flag = True
                with open(file_path, "w") as f:
                    f.write("")
                print("Retrieving data ...")
                    
            elif key == "n": sys.exit("Exiting ... Done")

    if flag:
        with open(file_path, "a") as f:
            # create header first
            if data == complete_text:
                data = ""
                for i in range(len(header)):
                    if i != len(header)-1:
                        data += "%s, " %header[i]
                    else:
                        data += "%s" %header[i]

            print(data)     # print the data written to the file
            f.write(data + "\n")