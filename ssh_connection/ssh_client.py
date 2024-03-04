import pathlib
from time import sleep, localtime, strftime

import paramiko

from client import client

class SSHClient(client.Client):
    _timeout = 1

    def __init__(self, hostname, username, password, debug = False):
        self._debug = debug
        if debug:
            debug_path = pathlib.Path('debug/read_bytes.txt')
            if not debug_path.parent.exists():
                debug_path.parent.mkdir(mode=0o775)
            self._log_file = open(debug_path, 'a')

        self._connect(hostname, username, password)
        self._invoke_shell(username)
        self._username = username

    def __del__(self):
        if hasattr(self, '_stdout'):
            self._stdout.close()
        # if hasattr(self, '_channel'):
        #     self._channel.close()
        if hasattr(self, '_ssh_client'):
            self._ssh_client.close()

        if self._debug:
            self._log_file.close()

    def _connect(self, hostname, username, password):
        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        self._ssh_client.connect(
            hostname=hostname,
            username=username,
            password=password,
            timeout=self._timeout
        )
    
    def _invoke_shell(self, username):
        self._channel = self._ssh_client.invoke_shell()
        self._channel.settimeout(self._timeout)
        self._stdout = self._channel.makefile('rb')

        connected_line = bytes(username + '@', 'utf-8')
        try:
            self.read_until(connected_line)
        except TimeoutError:
            raise(Exception('Could not invoke shell'))

    #Client methods
    def send(self, command):
        if not isinstance(command, bytes):
            command = bytes(command, 'utf-8')

        sleep(.1)
        self._channel.sendall(command.strip() + b'\r')

    def read_line(self):
        results = self._stdout.readline()

        if self._debug:
            time = strftime('%H:%M:%S', localtime())
            self._log_file.write(f'{time} | read_line:\n{results}\n')
            self._log_file.write('\n')

        return results

    def read_bytes(self, size):
        results = self._stdout.read(size)

        if self._debug:
            time = strftime('%H:%M:%S', localtime())
            self._log_file.write(f'{time} | read_bytes:\nsize: {size}\ndata: {results}\n')
            self._log_file.write('\n')

        return results
    
    def read_until(self, value):
        if not isinstance(value, bytes):
            value = bytes(value, 'utf-8')

        data = b''
        read_size = len(value)

        if self._debug:
            time = strftime('%H:%M:%S', localtime())
            self._log_file.write(f'{time} | read_until:\nvalue: {value}\ndata: {data}\n')
            self._log_file.write('\n')

        while True:
            data += self.read_bytes(read_size)

            if self._debug:
                time = strftime('%H:%M:%S', localtime())
                self._log_file.write(f'{time} | read_until:\nvalue: {value}\ndata: {data}\n')

            if data[-len(value):] == value:
                return data

            for i in range(read_size, 0, -1):
                if value[:i] == data[-i:]:
                    read_size = len(value) - i
                    break
            else:
                read_size = len(value)

    def read_all(self):
        size = 1024
        results = self._channel.recv(size)

        if self._debug:
            time = strftime('%H:%M:%S', localtime())
            self._log_file.write(f'{time} | read_all:\n{results}\n')
            self._log_file.write('\n')

        return results
    
    def get_username(self):
        return self._username
    
    def change_timeout(self, value : int | float):
        self._channel.settimeout(value)

    def restore_timeout(self):
        self._channel.settimeout(self._timeout)