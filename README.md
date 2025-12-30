# MUlti-SErial-LOgger

Simple serial logger that listens to an arbitrary number of serial ports and timestamps and logs the incoming messages.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/guolivar/multi-serial-logger.git
    cd multi-serial-logger
    ```

2.  **Install the package**:
    It is recommended to use a virtual environment.
    ```bash
    pip install .
    ```
    This will install the package and its dependencies (`pyserial` and `boto3`).

## Usage

### Configuration

Create a configuration file (e.g., `settings.txt`). The format is as follows:

```text
2
grimm,/dev/ttyUSB0,9600,N,8,n
cpc3772,/dev/ttyUSB1,9600,N,8,n
./data/
```

**Format Details:**
1.  **Number of Ports**: The first line specifies the number of serial ports to listen to (e.g., `2`).
2.  **Port Settings**: Followed by one line per port with the following comma-separated values:
    - `Name Prefix`: Prefix for the log files.
    - `Port`: The serial port device path (e.g., `/dev/ttyUSB0` or `COM1`).
    - `Baudrate`: Speed of the connection (e.g., `9600`).
    - `Parity`: Parity bit (`N`=None, `E`=Even, `O`=Odd).
    - `Byte Size`: Number of data bits (e.g., `8`).
    - `Line Termination`: Character indicating end of line (`n`=newline, `r`=carriage return, `nr`=newline+return).
3.  **Data Path**: The last line specifies the directory where logs will be saved (e.g., `./data/`).

### AWS Credentials

The logger supports uploading logs to AWS S3. You can provide credentials in two ways:

1.  **Environment Variables / Standard AWS Config** (Recommended):
    Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables, or configure `~/.aws/credentials`.

2.  **Legacy File**:
    Create a `_secret_aws.txt` file in the current directory with the following format (semicolon delimiter):
    ```text
    AWS_ACCESS_KEY_ID;YOUR_ACCESS_KEY
    AWS_SECRET_ACCESS_KEY;YOUR_SECRET_KEY
    ```

### Running the Logger

Once installed, you can run the logger using the command line:

```bash
multi-serial-logger --config settings.txt
```

If you don't specify `--config`, it defaults to looking for `settings.txt` in the current directory.

## Deployment

For detailed instructions on how to deploy this on a Raspberry Pi (including setting up a systemd service and permissions), please see [DEPLOYMENT.md](DEPLOYMENT.md).

## Development

To install in editable mode for development:

```bash
pip install -e .
```
