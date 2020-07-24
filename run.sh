#! /bin/bash    
cd /opt/sftp-receiver
source venv/bin/activate
python sftpReceiver.py
/usr/bin/find /opt/sftp-receiver/logs/*.log -maxdepth 0 -type f ! -mmin -10080 -exec rm {} \;
