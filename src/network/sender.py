import socket
import threading
import math

from file import File
from key import Key


def send_key(host: str, key: Key, iv: bytes, port: int = 8080):
    """
    Send encrypted keys to other machines
    """
    encrypted_key = key.encrypt_with_password(iv, 'password')
    with socket.socket() as s:
        s.connect((host, port))
        s.send(encrypted_key)
        s.send(iv)

def send(host: str, file: File, port: int = 8080):
    """
    Implementation of client.
    It send data to the other computer.

    :param str host: ip address of the receiver
    :param int port: port, defaults to 8080
    """
    with socket.socket() as s:
        s.connect((host, port))
        file_name = f'{file.name}.{file.extension}'
        s.send(file_name.encode())
        s.send(file.encrypted_data)

class SendThread(threading.Thread):
    def __init__(self, file, host: str = '0.0.0.0', port: int = 8080, show_progress_func=None):
        """
        :param str host: ip address of the sender ,default to 0.0.0.0 what's mean all IPv4 addresses on the local machine)
        :param int port: port, defaults to 8080
        """
        super().__init__()
        self._host: str = host
        self._port: int = port
        self._file = file
        self._show_progress_func = show_progress_func

    def run(self):
        chunk_size = 1024
        steps = math.ceil(float(self._file.size.split(' ')[0])/chunk_size)
        sended = 0
        with socket.socket() as s:
            s.connect((self._host, self._port))
            file_name = f'{self._file.name}.{self._file.extension}'
            s.send(file_name.encode())
            for i in range(steps):     
                s.send(file.encrypted_data[sended:sended+chunk_size])
                sended += chunk_size
                if self._show_progress_func:
                    self._show_progress_func(int((sended/self._file.size)*100))

