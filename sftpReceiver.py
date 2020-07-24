import paramiko
from datetime import datetime, timedelta
import os
import gzip
import re
import zlib
import logging
from paramiko.auth_handler import AuthenticationException, SSHException
import sys
import subprocess
import time
import config as conf
import argparse

logger = logging.getLogger('sftpReceiver')
handler = logging.FileHandler('logs/log_{:%Y-%m-%d}.log'.format(datetime.now()),mode='a')
formatter = logging.Formatter('%(asctime)s - %(levelname)s -  %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)

class sftpReceiver:
	
	sftp_client = None
	local_data_path = os.getcwd()+"/data"

	def __init__(self,delete,timeframe):
		self.host = conf.host
		self.port = conf.port
		self.user = conf.user
		self.password = conf.password
		self.root_file_path = conf.root_file_path
		self.tf_file_list=[]
		self.received_file_list=[]
		self.delete=delete
		self.timeframe=timeframe+2
		
	def ssh_connection_and_sftp_session(self):
		transport = paramiko.Transport((self.host,self.port))
		try:
			transport.connect(None,self.user,self.password)
		except AuthenticationException as error:
        		logger.error(error)
        		sys.exit(1)
		except SSHException as error:
			logger.error(error)
			sys.exit(1)
	
		self.sftp_client = paramiko.SFTPClient.from_transport(transport)

	def create_fileList(self):
		try:
			dir_list = self.sftp_client.listdir(self.root_file_path)
		except Exception as error:
			logger.error(error)
			sys.exit(1)

		for d in dir_list:
			utime = self.sftp_client.stat(self.root_file_path+"/"+d).st_mtime
			last_modified = datetime.fromtimestamp(utime)
			diff = datetime.now()-last_modified
			if diff<=timedelta(minutes=self.timeframe) and diff>=timedelta(minutes=2):
				self.tf_file_list.append(d)

	def receive_file(self):
		for i in self.tf_file_list:
			tmp_local_path = self.local_data_path+"/"+i
			tmp_remote_path = self.root_file_path+"/"+i
			try:
				self.sftp_client.get(tmp_remote_path,tmp_local_path)
				self.received_file_list.append(i)
				if self.delete:
					self.remove_file_from_sftp(tmp_remote_path)
			except Exception as error:
				logger.error(error)
				self.not_received_file(i)
		self.remove_empty_file()

	def not_received_file(self, file_name):
		try:
			with open("notRecvFile.txt","r+") as f:
				exists = any(file_name in line for line in f)
				if not exists:
					f.seek(0,os.SEEK_END)
					f.write(file_name)
					f.write("\n")
		except FileNotFoundError as error:
			logger.error(error)
			with open("notRecvFile.txt","a+") as f:
				f.write(file_name)
				f.write("\n")
		except IOError as error:
			logger.error(error)
			pass

	def remove_empty_file(self):
		for root,dirs,files in os.walk(self.local_data_path):
			for name in files:
				filename = os.path.join(root,name)
				if os.stat(filename).st_size == 0:
					os.remove(filename)

	def extract_gz_file(self):
		for i in self.received_file_list:
			tmp_local_path = self.local_data_path+"/"+i
			tmp_extract_fname = re.findall("(.*?)\.gz",i)[0]
			tmp_extract_path = self.local_data_path+"/"+tmp_extract_fname
			try:
				input = gzip.GzipFile(tmp_local_path,'rb')
				s = input.read()
				input.close()
			except IOError as error:
				logger.error(error)
				d = zlib.decompressobj(16+zlib.MAX_WBITS)
				input = open(tmp_local_path,'rb')
				s = input.read()
				s = d.decompress(s)
				input.close()
			
			output = open(tmp_extract_path,'wb')
			output.write(s)
			output.close()
			
			self.remove_gz_file(tmp_local_path)

	def remove_gz_file(self,file_path):
		try:
			os.remove(file_path)
		except OSError as error:
			logger.error(error)
			pass

	def remove_file_from_sftp(self,file_path):
		try:
			self.sftp_client.remove(file_path)
		except Exception as error:
			logger.error(error)
			pass
	
	def retry_download(self):
		tmp_list = []
		error = False
		try:
			with open("notRecvFile.txt","r") as f:
				lines=f.readlines()
		except IOError as error:
			logger.error(error)
			error = True

		if not error:
			for line in lines:
				if not line in ['\n', '\r\n']:
					line_s=line.strip()
					tmp_local_path = self.local_data_path+"/"+line_s
					tmp_remote_path = self.root_file_path+"/"+line_s
					try:
						self.sftp_client.get(tmp_remote_path,tmp_local_path)
					except Exception as error:
						logger.error(error)
						tmp_list.append(line_s)
			
			try:
				with open("notRecvFile.txt","w") as f:
					for i in tmp_list:
						f.write(i)
						f.write("\n")
			except IOError as error:
				logger.error(error)
				pass
		self.remove_empty_file()

	def close_session(self):
		self.sftp_client.close()

def args_builder():
	parser = argparse.ArgumentParser()
	parser.add_argument('-d','--delete',action='store_true',help="Delete file from sftp server after received",default=False)
	parser.add_argument('-tf','--timeframe',help="Timeframe in minutes for files to download",type=int,default=10)
	parser.add_argument('-t','--tryagain',action='store_true',help="Retry for can't downloaded files before",default=False)
	args = parser.parse_args()
	return args

def main():
	args = args_builder()
	data_receiver=sftpReceiver(args.delete,args.timeframe)
	data_receiver.ssh_connection_and_sftp_session()
	data_receiver.create_fileList()
	data_receiver.receive_file()
	data_receiver.extract_gz_file()
	if args.tryagain:
		data_receiver.retry_download()
	data_receiver.close_session()

if __name__ == '__main__':
	main()
