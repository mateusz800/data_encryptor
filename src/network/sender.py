import os
import socket
import threading
import math
import time

from file import File
from key import Key


def send_key(host: str, key: Key, iv: bytes,password:str, port: int = 8080):
    """
    Send encrypted keys to other machines
    """
    encrypted_key = key.encrypt_with_password(iv, password)
    with socket.socket() as s:
        s.connect((host, port))
        s.send('1'.encode())
        s.send(encrypted_key)
        s.send(iv)


class SendThread(threading.Thread):
    def __init__(self, file, mode:str, host:str, port: int = 8080, show_progress_func=None):
        """
        :param str host: ip address of the sender
        :param int port: port, defaults to 8080
        """
        super().__init__()
        self._host: str = host
        self._port: int = port
        self._file = file
        self._mode = mode
        self._show_progress_func = show_progress_func

    def run(self):
        chunk_size = 1024
        file_size = os.path.getsize(self._file.path)
        steps = math.ceil(file_size/chunk_size)
        sended = 0
        with socket.socket() as s:
            s.connect((self._host, self._port))
            s.send('0'.encode())
            time.sleep(.1)
            file_name = f'{self._file.name}.{self._file.extension}'
            s.send(file_name.encode())
            time.sleep(.1)
            s.send(self._mode.encode())
            for i in range(steps):     
                s.send(self._file.encrypted_data[sended:sended+chunk_size])
                sended += chunk_size
                if self._show_progress_func:
                    self._show_progress_func(int((sended/file_size)*100))

