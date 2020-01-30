import socket
from multiprocessing.connection import Client
import subprocess
import pickle
import logging
import time
import os

#Thhis should be the path to the python.exe file in the CEpy27 environment set up by conda.
WAIT_TIME = 0.075 # Time in seconds to wait between server calls.
cwd = os.getcwd()
cwd = cwd.split('\\')
USER = cwd[2]
PYTHON2_PATH = r"C:\Users\{}\Miniconda3\envs\CEpy27\python.exe".format(USER)
SERVER_FILE = r'C:\Users\{}\Documents\Barracuda\BarracudaQt\hardware\MicroControlServer.py'.format(USER)
class MicroControlClient:
    authkey = b'barracuda'
    server = None # subprocess.Popen object
    conn = None
    def __init__(self, port=5030):
        self.address = ('localhost', port)
        #self.start_server()

    def start_connection(self):
        self.conn = Client(self.address, authkey=b'barracuda')

    def send_command(self, cmd):
        self.conn.send_bytes(pickle.dumps(cmd, 2))
        time.sleep(WAIT_TIME)

    def read_response(self):
        response = self.conn.recv_bytes()
        response = pickle.loads(response, encoding='bytes')
        time.sleep(WAIT_TIME)
        return response

    def close_server(self):
        self.conn.send_bytes(pickle.dumps('close',2))
        self.conn.close()
        self.server.terminate()

    def start_server(self):
        """
        Opens the python2 subprocess that will run the server and micromanager code.
        :return:
        """
        self.server = subprocess.Popen([PYTHON2_PATH,
                                        SERVER_FILE, '{}'.format(self.address[1])], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        time.sleep(1)
    def open(self):
        """ Opens the Python 2 server and starts the connection"""
        if self.conn is None:
            self.start_server()
            self.start_connection()
        elif self.conn.closed:
            self.start_server()
            self.start_connection()
        return True

    def close(self):
        self.close_server()
        return True

    @staticmethod
    def ok_check(response,msg):
        """ Checks the response if it was recieved OK."""

        if str(response.decode())!= 'Ok':
            logging.error('{}. Recieved: {}'.format(msg,response))
            return False
        return True

