# sftp-receiver
Receive compressed data from sftp server and extract gz file.

if you wish delete file from sftp server after recevied data or specify a time frame, you can customize using script arguments. Also, you can forward data to splunk using inputs configuration and delete it to save space after sending.

# Installation and Configuration

Firstly, create a virtual environment and install requirements as the following;

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Parameters in config.py file must be filled as required.


# Usage
```
<usage: sftpReceiver.py [-h] [-d] [-tf TIMEFRAME] [-t]

optional arguments:
  -h, --help            show this help message and exit
  -d, --delete          Delete file from sftp server after received
  -tf TIMEFRAME, --timeframe TIMEFRAME
                        Timeframe in minutes for files to download
  -t, --tryagain        Retry for can't downloaded files before
```
