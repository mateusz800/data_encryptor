import socket
import threading
import os

from components.received_file import ReceivedFile
from components.message_receiver import MessageReceiver


class ReceiveThread(threading.Thread):
    def __init__(self, widget: ReceivedFile, message_receiver: MessageReceiver, get_public_key_func, decrypt_session_key_func , show_modal_func, host: str = '0.0.0.0', port: int = 8080):
        """
        :param  ReceivedFile widget: widget object that shows information about received file
        :param str host: ip address of the sender ,default to 0.0.0.0 what's mean all IPv4 addresses on the local machine)
        :param int port: port, defaults to 8080
        """
        super().__init__()
        self._host: str = host
        self._port: int = port
        self._socket = socket.socket()
        self._file_widget = widget
        self._message_receiver = message_receiver
        self._show_modal_func = show_modal_func
        self._get_public_key_func = get_public_key_func
        self._decrypt_session_key_func = decrypt_session_key_func 
        self._key = None
        self._send_key = False
        self._send_host = ''
        self._send_port = ''


    def run(self):
        """
        Implementation of server.
        It in infinite loop waits for connection and when the connection will
        be established receive the data and write it to the file.
        """
        
        self._running = True
        self._socket.bind((self._host, self._port))
        self._socket.listen()
        while self._running:
            if self._send_key:
                with socket.socket() as s:
                    with open('keys/public_key.txt', 'rb') as file:
                        key = file.read()
                    s.connect((self._send_host, self._send_port))
                    s.send('3'.encode())
                    s.send(key)
                self._send_key = False
            try:
                conn, addr = self._socket.accept()
            except ConnectionAbortedError:
                break
            print('Got connection from ', addr)
            self._send_port = self._port
            self._send_host = addr[0]
            if not os.path.isdir('files'):
                os.makedirs('files')
            with conn:
                flag = conn.recv(len('0'.encode())).decode()
                if flag == '2':
                    # request for public key
                    self._send_key = True
                    # set the flag to true and send key (implementation above)
                elif flag =='3':
                    # get receiver public key
                    key = conn.recv(1024)
                    self._get_public_key_func(key)
                elif flag =='4':
                    # get session key
                    enc_session_key = conn.recv(1024)
                    self._decrypt_session_key_func(enc_session_key)
                elif flag== '0':
                    #receive file or message
                    file_name = conn.recv(1024).decode()
                    if file_name != 'message.txt':
                        # file receiving
                        path = f'files/{file_name}'
                        mode = conn.recv(3).decode()
                        with open(path, 'wb') as file:
                            while True:
                                data = conn.recv(1024)
                                if not data:
                                    break
                                file.write(data)
                        self._file_widget.set_file(path, encrypted=True)
                    else:
                        # message receiving
                        mode = conn.recv(3).decode()
                        with open('files/message_received.txt', 'wb') as file:
                            while True:
                                data = conn.recv(1024)
                                if not data:
                                    break
                                file.write(data)
                        self._message_receiver.set_message('files/message_received.txt', mode)


    def stop(self):
        """
        Stop the thread loop
        """
        self._running = False
        self._socket.close()

    def set_key(self, key):
        self._key = key
