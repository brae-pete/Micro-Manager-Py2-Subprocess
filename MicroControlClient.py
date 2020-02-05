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
PYTHON2_PATH = r"C:\Users\{}\Anaconda3\envs\CEpy27\python.exe".format(USER)
SERVER_FILE = os.path.join(os.getcwd(), r'MicroManagerProcess\MicroControlServer.py')


class MicroControlClient:
    """
    The client will initiate a second python process that will run Micromanager. Micromanager at this time
    is only supported in Python2.7. After the Python2 process has been started the
    MicroControlClient can be used to send commands to the MicroControlServer. The server compares the commands
    to a dictionary and run the corresponding Micromanager function.
    # Create the Microcontrol Client
    >>> mmc = MicroControlClient(port = 6812)
    >>> mmc.open() # Open creates the python 2 server
    >>> mmc.send_command(r'camera,get_image\n' ) # Send a command
    >>> img = mmc.read_response() # Read a response
    >>> mmc.close() # Close the connection

    """
    authkey = b'amazingKey'
    server = None # subprocess.Popen object
    conn = None
    def __init__(self, port=5030):
        self.address = ('localhost', port)
        #self.start_server()

    def start_connection(self):
        self.conn = Client(self.address, authkey=self.authkey)

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

if __name__== "__main__":
    SERVER_FILE = r'C:\Users\Luke\Desktop\Luke\MicroManagerProcess\MicroControlServer.py'
    mcc = MicroControlClient(port=4531)
    mcc.start_server()
