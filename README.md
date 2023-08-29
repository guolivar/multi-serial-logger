# MUlti-SErial-LOgger

Simple serial logger that listens to an arbitrary number of serial ports and timestamps and logs the incoming messages.

## Installation

1. install Python (>3.5) [Start here](https://www.python.org/about/gettingstarted/).
2. Install the required modules:
    - **pyserial** following [these instructions](https://github.com/pyserial/pyserial).
    - **boto3** to interact with AWS. Following [these instructions](https://pypi.org/project/boto3/)
    - **pandas** to parse text files. Following [these instructions](https://pypi.org/project/pandas/)
3. Download a ZIP file with this repository [from here](https://github.com/guolivar/multi-serial-logger/archive/master.zip) or if you're familiar with Git, clone this repository to your system.

## Use

Make sure that the files `multilogger.py` and `settings.txt` are in the same folder and edit the `settings.txt` file to suit your needs.

```
2
grimm,/dev/pts/5,9600,N,8,n
cpc3772,/dev/pts/8,9600,N,8,n
./data/

## Only the first lines are processed.

1. <Number of serial ports to read from>
2. <prefix for this serial data>,<SERIAL PORT INFO: address, baudrate, parity, byte>,<line termination character (**n**=new line;r=carriage return;nr=new line and carriage return)> (This line repeats as many times as serial ports to read from)
3. <DATA SAVE PATH>
```

Then, just run the script using python

```bash
python multilogger.py
```

You'll see a number of messages on screen, including the data being captured from the serial ports.

For details contact Gustavo Olivares
