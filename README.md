# sftp-receiver
Receive compressed data from sftp server and extract gz file

# Usage

`usage: sftpReceiver.py [-h] [-d] [-tf TIMEFRAME] [-t]

optional arguments:
  -h, --help            show this help message and exit
  -d, --delete          Delete file from sftp server after received
  -tf TIMEFRAME, --timeframe TIMEFRAME
                        Time interval in minutes for files to download
  -t, --tryagain        Retry for can't downloaded files before`
