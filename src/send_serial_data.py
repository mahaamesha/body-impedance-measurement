from serial import Serial
from json_function import read_filejson

# Define the serial port and baud rate.
# Ensure the 'COM#' corresponds to what was seen in the Windows Device Manager
port = "COM4"
baudrate = 9600

ser = Serial(port, baudrate)


def send_serial_data(data, debug_flag=False, max_chr=16):
    data_str = str(data)[:max_chr]       # extract only first n character
    data_byte = bytes(data_str, "utf-8")
    # send every character to arduino from serials
    ser.write(data_byte)
    print(data_str, data_byte)

    if debug_flag:
        for i in range(len(data_byte)):
            # read every character in data_byte. for debugging purpose
            incoming_byte = ser.readline()[:-2]     # format: b'49\r\n' --> b'49'
            if int.from_bytes(incoming_byte, "big") >= 45 and int.from_bytes(incoming_byte, "big") <= 57:     # only "-" until "9"
                print("%s\t: %s" %(i, incoming_byte))


# i need to send data to arduino via serial: internal factor & model coefficient
def send_serial_internal_factor(file_path="tmp/training_internal_factor.json"):
    data = read_filejson(file_path)
    keys = list( data.keys() )
    

    for key in keys:    # delta_z & delta_phase
        arr_num = data[key]     # get the array of delta_z & delta_phase
        for i in range(len(arr_num)):   # iterate in each element of that array
            num = arr_num[i]      # num is float type

            # send every num through serial communication
            send_serial_data(num, debug_flag=True, max_chr=8)
        
        print(len(arr_num))



if __name__ == "__main__":
    test_str = 2.1763591420376414691
    send_serial_data(test_str, debug_flag=True)

    # send_serial_internal_factor()