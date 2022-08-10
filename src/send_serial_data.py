from serial import Serial
from json_function import read_filejson

# Define the serial port and baud rate.
# Ensure the 'COM#' corresponds to what was seen in the Windows Device Manager
port = "COM4"
baudrate = 9600

ser = Serial(port, baudrate)


def send_serial_data(data_str, debug_flag=False):
    data_byte = bytes(data_str, "utf-8")
    # send every character to arduino from serials
    ser.write(data_byte)

    if debug_flag:
        for i in range(len(data_byte)):
            # read every character in data_byte. for debugging purpose
            print(ser.readline()[:-2])  # format: b'49\r\n' --> b'49'


# i need to send data to arduino via serial: internal factor & model coefficient
def send_serial_internal_factor(file_path="tmp/training_internal_factor.json"):
    data = read_filejson(file_path)
    keys = list( data.keys() )

    for key in keys:
        arr = data[key]     # get the array of delta_z & delta_phase
        for i in range(len(arr)):   # iterate in each element of that array
            num = arr[i]
            num_str = "{:.4f}".format(num)
            send_serial_data(num_str)
        break



if __name__ == "__main__":
    test_str = "1007.81"
    data_byte = send_serial_data(test_str, debug_flag=True)

    send_serial_internal_factor()