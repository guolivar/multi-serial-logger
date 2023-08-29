#!/usr/bin/env python
# Load the libraries
import serial  # Serial communications
import time  # Timing utilities
import os, sys  # OS utils to keep working directory
import boto3  # AWS S3 library
from datetime import datetime, timedelta  # To check dates and handle files
import pandas as pd  # Only to read a CSV ... unbelievable!


def upload_to_s3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket"""
    s3_client = boto3.client("s3")

    if object_name is None:
        object_name = file_name

    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return False
    return True


# Change working directory to the script's path
os.chdir(os.path.dirname(sys.argv[0]))

# Load credentials
secret_aws = pd.read_csv("./_secret_aws.txt", delimiter=";", header=None)

# Set environment variables for AWS
os.environ["AWS_ACCESS_KEY_ID"] = secret_aws.iloc[0, 1]
os.environ["AWS_SECRET_ACCESS_KEY"] = secret_aws.iloc[1, 1]
os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-2"

# Set the time constants
rec_time = time.gmtime()
timestamp = time.strftime("%Y/%m/%d %H:%M:%S GMT", rec_time)
prev_minute = rec_time[4]
today = datetime.now().strftime("%Y%m%d")
end_of_day = datetime.now().replace(hour=23, minute=59, second=59)
# Read the settings from the settings file
settings_file = open("./settings.txt")
# How many serial ports? -- MUST match the number of serial config lines in the settings file
nports = eval(settings_file.readline().rstrip("\n"))
# Initialise the lists of data to hold parameters for each instrument
prefixes = []
ports = []
bauds = []
xpars = []
xbytes = []
eols = []
# Read each of the serial config lines from the settings file
for i in range(nports):
    # e.g. "instrumentX,/dev/ttyUSB0,9600,N,8,n"
    settings_line = settings_file.readline().rstrip("\n").split(",")
    prefixes.append(settings_line[0])
    ports.append(settings_line[1])
    bauds.append(settings_line[2])
    xpars.append(settings_line[3])
    xbytes.append(eval(settings_line[4]))
    if settings_line[5] == "r":
        eols.append(b"\r")
    elif settings_line[5] == "nr":
        eols.append(b"\n\r")
    else:
        eols.append(b"\n")
print(ports)
# path for data files
# e.g. "/home/logger/data/"
datapath = settings_file.readline().rstrip("\n")
print(datapath)
# Format for filenames
fnamefmt = "%Y%m%d.txt"
# LOG some info
current_LOG_name = datapath + time.strftime("%Y%m%d.LOG", rec_time)
current_file = open(current_LOG_name, "a")
current_file.write(timestamp + " Logging starts\n")
current_file.write(",".join(prefixes))
current_file.write("\n")
current_file.write(",".join(ports))
current_file.write("\n")
current_file.write(",".join(bauds))
current_file.write("\n")
current_file.write(",".join(xpars))
current_file.write("\n")
current_file.write(",".join(str(xbytes)))
current_file.write("\n")
current_file.write(",".join(str(eols)))
current_file.write("\n")
current_file.write(datapath)
current_file.write("\n")

# Setup the Serial ports for communication
ser = []
for i in range(nports):
    current_file.write("Opening port " + ports[i] + "\n")
    ser.append(serial.Serial())
    ser[i].port = ports[i]
    ser[i].baudrate = bauds[i]
    ser[i].parity = xpars[i]
    ser[i].bytesize = xbytes[i]
    ser[i].open()
    ser[i].flushInput()
    ser[i].flushOutput()
    current_file.write("Port " + ports[i] + " flushed\n")
    print("Port " + ports[i] + " flushed")

# Close the settings file
settings_file.close()
# Close the LOG file for now
current_file.flush()
current_file.close()

# Start the logging
while True:
    for i in range(nports):
        print(ports[i])
        try:
            # Hacks to work with custom end of line
            leneol = len(eols[i])
            bline = bytearray()
            # Get a line of data from the port
            while True:
                c = ser[i].read(1)
                bline += c
                if bline[-leneol:] == eols[i]:
                    break
            ## Parse the data line
            line = bline.decode("utf-8").rstrip()
            # Set the time for the record
            rec_time = time.gmtime()
            timestamp = time.strftime("%Y/%m/%d %H:%M:%S GMT", rec_time)
            # Build the line to save to file
            file_line = timestamp + "\t" + line
            print(file_line)
            # Save it to the appropriate file
            current_file_name = (
                datapath + prefixes[i] + time.strftime("_%Y%m%d.txt", rec_time)
            )
            current_file = open(current_file_name, "a")
            current_file.write(file_line + "\n")
            current_file.flush()
            current_file.close()
            file_line = ""
            bline = bytearray()
        except:
            current_LOG_name = datapath + time.strftime("%Y%m%d.LOG", rec_time)
            current_file = open(current_LOG_name, "a")
            current_file.write(
                timestamp + " Unexpected error with port " + ports[i] + "\n"
            )
            current_file.write(timestamp + " No data recorded\n")
            current_file.flush()
            current_file.close()
        if datetime.now() > end_of_day:
            # Upload file to S3
            try:
                # Upload the file to Amazon S3
                if upload_to_s3(
                    datapath + f"{today}.txt", "serialdata", object_name=f"{today}.txt"
                ):
                    print(f"File {today}.txt uploaded successfully to S3")
                else:
                    print(f"Failed to upload {today}.txt to S3")
            except Exception as e:
                print(f"File move or upload error: {e}")
                # log error to your LOG file
                current_LOG_name = datapath + time.strftime("%Y%m%d.LOG", rec_time)
                current_file = open(current_LOG_name, "a")
                current_file.write(
                    timestamp + " File move or upload error: {e} " + ports[i] + "\n"
                )
                current_file.flush()
                current_file.close()
        # Reset today and end_of_day for the next iteration
        today = (datetime.now() + timedelta(days=1)).strftime(prefixes[i] + "_%Y%m%d")
        end_of_day = (datetime.now() + timedelta(days=1)).replace(
            hour=23, minute=59, second=59
        )
print("I'm done now")
