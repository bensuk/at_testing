import pathlib
from time import sleep, localtime, strftime
import re

import paramiko

from client.client import Client

class SSHClient(Client):
    _buffer = [b'']
    _read_size = 1024
    _active = False
    _timeout = 5

    def __init__(self, hostname, username, password, device_name, debug = False):
        self._debug = debug
        self._username = username
        self._device = device_name.upper()
        self._setup_debug()
        self._connect(hostname, username, password)
        self._invoke_shell()

    def __del__(self):
        if hasattr(self, '_stdout'):
            self._stdout.close()
        if hasattr(self, '_channel'):
            self._channel.close()
        if hasattr(self, '_ssh_client'):
            self._ssh_client.close()

        if self._debug:
            self._log_file.close()

    def _connect(self, hostname, username, password):
        self._ssh_client = paramiko.SSHClient()
        # TODO think about key policy
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        self._ssh_client.connect(
            hostname=hostname,
            username=username,
            password=password,
            timeout=self._timeout
        )
    
    def _invoke_shell(self):
        self._channel = self._ssh_client.invoke_shell()
        self._channel.settimeout(self._timeout)
        self._stdout = self._channel.makefile('rb')

        try:
            self.wait_for_ready_to_send()
            self._active = True
        except TimeoutError:
            raise(Exception('Could not invoke shell'))
        #TODO add another exception?
        
    def _setup_debug(self):
        if self._debug:
            debug_path = pathlib.Path('debug/debug.txt')
        if not debug_path.parent.exists():
            debug_path.parent.mkdir(mode=0o775)
        self._log_file = open(debug_path, 'a') 

    def wait_for_ready_to_send(self):
        self.read_lines_until_regex(f'^{self._username}@{self._device}:.+# $')

    #Client methods
    def send(self, command):
        if not isinstance(command, bytes):
            command = bytes(command, 'utf-8')

        command = command.strip() + b'\r'

        if self._debug:
            time = strftime('%H:%M:%S', localtime())
            self._log_file.write(f'{time} | send |\n')
            self._log_file.write(f'\t{command}\n')
            self._log_file.write('\n')

        #TODO what about sleep?
        # sleep(.1)
        self._channel.sendall(command)

    def read_line(self):
        while True:
            read_data = (self._buffer[-1] + self._channel.recv(self._read_size)).split(b'\n')

            for i, line in enumerate(read_data):
                if line[-2:] == b'\r\r' and len(read_data) > i+1:
                    read_data[i] = line[:-2] + read_data[i+1]
                    del read_data[i+1]
                
                read_data[i] = read_data[i].rstrip(b'\r')

            last_element = read_data[-1]
            read_data = list(filter(None, read_data[:-1]))
            read_data.append(last_element)

            self._buffer[-1:] = read_data

            if self._debug:
                time = strftime('%H:%M:%S', localtime())
                self._log_file.write(f'{time} | read_line |\n')
                self._log_file.write(f'\t{self._buffer}\n')
                self._log_file.write('\n')

            if len(self._buffer) > 1:
                return self._buffer.pop(0)

    def read_bytes(self, size):
        required = size
        results = []

        while True:
            read_data = (self._buffer[-1] + self._channel.recv(self._read_size)).split(b'\n')

            # TODO create generic method 
            for i, line in enumerate(read_data):
                if line[-2:] == b'\r\r' and len(read_data) > i+1:
                    read_data[i] = line[:-2] + read_data[i+1]
                    del read_data[i+1]
                
                read_data[i] = read_data[i].rstrip(b'\r')

            last_element = read_data[-1]
            read_data = list(filter(None, read_data[:-1]))
            read_data.append(last_element)

            self._buffer[-1:] = read_data

            if self._debug:
                time = strftime('%H:%M:%S', localtime())
                self._log_file.write(f'{time} | read_bytes |\n')
                self._log_file.write(f'\t{self._buffer}\n')
                self._log_file.write('\n')

            for i, line in enumerate(self._buffer):
                if len(line) > required:
                    required = 0
                    results.append(line[:required])
                    self._buffer[i] = line[required:]
                else:
                    required -= len(line)
                    results.append(line)
                    self._buffer[i] = b''

                if required <= 0:
                    last_element = self._buffer[-1]
                    self._buffer = list(filter(None, self._buffer))
                    self._buffer.append(last_element)
                    
                    return results

            self._buffer = [b'']
    
    def read_until(self, value):
        if not isinstance(value, bytes):
            value = bytes(value, 'utf-8')

        while True:
            if self._debug:
                time = strftime('%H:%M:%S', localtime())
                self._log_file.write(f'{time} | read_until |\n')
                self._log_file.write(f'\tvalue: {value}\n')
                self._log_file.write(f'\tdata: {self._buffer}\n')
                self._log_file.write('\n')

            read_data = (self._buffer[-1] + self._channel.recv(self._read_size)).split(b'\n')

            # TODO create generic method 
            for i, line in enumerate(read_data):
                if line[-2:] == b'\r\r' and len(read_data) > i+1:
                    read_data[i] = line[:-2] + read_data[i+1]
                    del read_data[i+1]
                
                read_data[i] = read_data[i].rstrip(b'\r')

            last_element = read_data[-1]
            read_data = list(filter(None, read_data[:-1]))
            read_data.append(last_element)

            for i, line in enumerate(read_data):
                if value in line:
                    return_data = self._buffer[:-1] + read_data[:i+1]

                    if read_data[i+1:]:
                        self._buffer = read_data[i+1:]
                    else:
                        self._buffer = [b'']
                    
                    return return_data
                
            self._buffer[-1:] = read_data

    def read_lines_until_regex(self, regex_expr):
        if not isinstance(regex_expr, bytes):
            regex_expr = bytes(regex_expr, 'utf-8')

        while True:
            if self._debug:
                time = strftime('%H:%M:%S', localtime())
                self._log_file.write(f'{time} | read_until_regex |\n')
                self._log_file.write(f'\tvalue: {regex_expr}\n')
                self._log_file.write(f'\tdata: {self._buffer}\n')
                self._log_file.write('\n')

            read_data = (self._buffer[-1] + self._channel.recv(self._read_size)).split(b'\n')

            # TODO create generic method 
            for i, line in enumerate(read_data):
                if line[-2:] == b'\r\r' and len(read_data) > i+1:
                    read_data[i] = line[:-2] + read_data[i+1]
                    del read_data[i+1]
                
                read_data[i] = read_data[i].rstrip(b'\r')

            last_element = read_data[-1]
            read_data = list(filter(None, read_data[:-1]))
            read_data.append(last_element)

            for i, line in enumerate(read_data):
                match = re.search(regex_expr, line)

                if match:
                    return_data = self._buffer[:-1] + read_data[:i+1]

                    if read_data[i+1:]:
                        self._buffer = read_data[i+1:]
                    else:
                        self._buffer = [b'']

                    return return_data
                
            self._buffer[-1:] = read_data

    def read_all(self):
        read_data = (self._buffer[-1] + self._channel.recv(self._read_size)).split(b'\n')

        # TODO create generic method 
        for i, line in enumerate(read_data):
            if line[-2:] == b'\r\r' and len(read_data) > i+1:
                read_data[i] = line[:-2] + read_data[i+1]
                del read_data[i+1]
            
            read_data[i] = read_data[i].rstrip(b'\r')

        last_element = read_data[-1]
        read_data = list(filter(None, read_data[:-1]))
        read_data.append(last_element)

        results = self._buffer[:-1] + read_data
        self._buffer = [b'']

        if self._debug:
            time = strftime('%H:%M:%S', localtime())
            self._log_file.write(f'{time} | read_all |\n')
            self._log_file.write(f'\t{results}\n')
            self._log_file.write('\n')

        return results
    
    def get_username(self):
        return self._username
    
    def change_timeout(self, value : int | float):
        self._channel.settimeout(value)

    def restore_timeout(self):
        self._channel.settimeout(self._timeout)

    def is_active(self):
        return self._active