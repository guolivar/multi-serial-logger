#!/usr/bin/env python
# Load the libraries
import serial  # Serial communications
import time  # Timing utilities
import os, sys  # OS utils to keep working directory
import boto3  # AWS S3 library
from datetime import datetime, timedelta  # To check dates and handle filenames
import csv
import argparse

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

def main():
    parser = argparse.ArgumentParser(description="Multi-Serial Logger")
    parser.add_argument(
        "--config",
        default="settings.txt",
        help="Path to the configuration file (default: settings.txt)",
    )
    args = parser.parse_args()

    # Load credentials
    # Check for legacy secret_aws.txt or default to environment/AWS config
    if os.path.exists("./_secret_aws.txt"):
        try:
             with open("./_secret_aws.txt", "r") as f:
                reader = csv.reader(f, delimiter=";")
                rows = list(reader)
                if len(rows) >= 2:
                    os.environ["AWS_ACCESS_KEY_ID"] = rows[0][1]
                    os.environ["AWS_SECRET_ACCESS_KEY"] = rows[1][1]
                    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-2"
        except Exception as e:
            print(f"Error reading _secret_aws.txt: {e}")
            print("Falling back to standard AWS credentials chain.")

    
    # Set the time constants
    rec_time = time.gmtime()
    timestamp = time.strftime("%Y/%m/%d %H:%M:%S GMT", rec_time)
    
    today = datetime.now().strftime("%Y%m%d")
    end_of_day = datetime.now().replace(hour=23, minute=59, second=59)

    # Read the settings from the settings file
    try:
        settings_file = open(args.config)
    except FileNotFoundError:
        print(f"Error: Configuration file '{args.config}' not found.")
        sys.exit(1)

    # How many serial ports? -- MUST match the number of serial config lines in the settings file
    try:
        nports = int(settings_file.readline().strip())
    except ValueError:
        print("Error: Invalid number of ports in settings file.")
        sys.exit(1)

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
        try:
            settings_line = settings_file.readline().rstrip("\n").split(",")
            prefixes.append(settings_line[0])
            ports.append(settings_line[1])
            bauds.append(int(settings_line[2]))
            xpars.append(settings_line[3])
            xbytes.append(int(settings_line[4]))
            if settings_line[5] == "r":
                eols.append(b"\r")
            elif settings_line[5] == "nr":
                eols.append(b"\n\r")
            else:
                eols.append(b"\n")
        except (IndexError, ValueError) as e:
             print(f"Error parsing settings line {i+1}: {e}")
             sys.exit(1)
             
    print(ports)
    # path for data files
    # e.g. "/home/logger/data/"
    datapath = settings_file.readline().rstrip("\n")
    print(datapath)
    
    # Ensure datapath exists
    if not os.path.exists(datapath):
        try:
            os.makedirs(datapath)
        except OSError as e:
             print(f"Error creating data directory '{datapath}': {e}")
             sys.exit(1)


    # LOG some info
    current_LOG_name = os.path.join(datapath, time.strftime("%Y%m%d.LOG", rec_time))
    current_file = open(current_LOG_name, "a")
    current_file.write(timestamp + " Logging starts\n")
    current_file.write(",".join(prefixes))
    current_file.write("\n")
    current_file.write(",".join(ports))
    current_file.write("\n")
    current_file.write(",".join(map(str, bauds)))
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
        try:
            s = serial.Serial()
            s.port = ports[i]
            s.baudrate = bauds[i]
            s.parity = xpars[i]
            s.bytesize = xbytes[i]
            s.open()
            s.flushInput()
            s.flushOutput()
            ser.append(s)
            current_file.write("Port " + ports[i] + " flushed\n")
            print("Port " + ports[i] + " flushed")
        except serial.SerialException as e:
             print(f"Error opening port {ports[i]}: {e}")
             current_file.write(f"Error opening port {ports[i]}: {e}\n")
             # Depending on requirements, we might want to exit or continue with other ports
             # For now, we'll exit as it seems critical
             sys.exit(1)


    # Close the settings file
    settings_file.close()
    # Close the LOG file for now
    current_file.flush()
    current_file.close()

    # Start the logging
    try:
        while True:
            for i in range(nports):
                # print(ports[i]) # Reduced verbosity
                try:
                    # Hacks to work with custom end of line
                    leneol = len(eols[i])
                    bline = bytearray()
                    # Get a line of data from the port
                    # Using in_waiting to avoid blocking indefinitely if possible, 
                    # but original code blocked. Keeping it simple but adding a small timeout logic could be better.
                    # reusing original logic for compatibility.
                    
                    if ser[i].in_waiting > 0:
                        while True:
                            c = ser[i].read(1)
                            bline += c
                            if bline[-leneol:] == eols[i]:
                                break
                        
                        ## Parse the data line
                        line = bline.decode("utf-8", errors='replace').rstrip()
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
                        with open(current_file_name, "a") as current_file:
                             current_file.write(file_line + "\n")
                        
                        file_line = ""
                        bline = bytearray()
                except Exception as e:
                    # Log error to LOG file
                    rec_time = time.gmtime()
                    timestamp = time.strftime("%Y/%m/%d %H:%M:%S GMT", rec_time)
                    current_LOG_name = os.path.join(datapath, time.strftime("%Y%m%d.LOG", rec_time))
                    with open(current_LOG_name, "a") as current_file:
                        current_file.write(
                            timestamp + " Unexpected error with port " + ports[i] + ": " + str(e) + "\n"
                        )
                        current_file.write(timestamp + " No data recorded\n")

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
                        current_LOG_name = os.path.join(datapath, time.strftime("%Y%m%d.LOG", rec_time))
                        with open(current_LOG_name, "a") as current_file:
                             current_file.write(
                                timestamp + f" File move or upload error: {e} " + ports[i] + "\n"
                            )
                            
                    # Reset today and end_of_day for the next iteration
                    today = (datetime.now() + timedelta(days=1)).strftime(prefixes[i] + "_%Y%m%d")
                    end_of_day = (datetime.now() + timedelta(days=1)).replace(
                        hour=23, minute=59, second=59
                    )
            time.sleep(0.01) # Small sleep to prevent high CPU usage
    except KeyboardInterrupt:
        print("Stopping logger...")
        for s in ser:
            s.close()
        print("Done.")

if __name__ == "__main__":
    main()
