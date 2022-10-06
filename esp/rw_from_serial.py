import os
import sys
from time import sleep
import serial

# arduino_port = "/dev/cu.usbmodem14201"      # for mac
arduino_port = "COM4"   # for windows
baud = 9600 #arduino uno runs at 9600 baud
path = "D:/My_Project/body-impedance-measurement/esp/data_retrieved"
file_name = "analog-data.csv"       # default name to generate
file_path = os.path.join(path, file_name)

# used as mark if the system want to start next sweeping
initial_text = "Sweep frequency ..."
complete_text = "Frequency sweep complete!"
initial_flag = 0;
complete_flag = 0;

# header contains parameters want to saved
header = ["Frequency", "Impedance", "Real", "Imaginer"]


ser = serial.Serial(arduino_port, baud)
print("Connecting to port: " + arduino_port)

#add the data to the file
while True:
    #display the data to the terminal
    getData = str(ser.readline())
    data = getData[0:][:-4]
    data = getData[2:-5]

    if data == initial_text and initial_flag == 0:
        key = 0
        while (key != "y") and (key != "n"):
            key = input("\nRetrieve data? (y/n) ")
            
            # if yes, clear the file first
            if key == "y":
                initial_flag = 1
            
                # set filename
                file_name = input("Input filename (without file format): ")
                file_path = os.path.join(path, file_name + ".csv")

                # create the file
                with open(file_path, "w") as f:
                    f.write("")

                print("Retrieving data ...\n")
                # sleep(5)
                    
            elif key == "n": sys.exit("Exiting ... Done")

    if (initial_flag and not(complete_flag)):    # if flag to retrieve data is HIGH
        # write data
        with open(file_path, "a") as f:
            # create header first
            if data == initial_text:
                data = ""
                for i in range(len(header)):
                    if i != len(header)-1:
                        data += "%s," %header[i]
                    else:
                        data += "%s" %header[i]     # last header
            elif data == complete_text:
                complete_flag = 1
            else:
                # if data != complete_text
                # data is FREQ, IMPEDANCE, REAL, IMAG
                print(data)     # print the data written to the file
                f.write(data + "\n")