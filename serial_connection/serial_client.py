from time import sleep, localtime, strftime
import pathlib

import serial

from client import client
from modules import print_information

class SerialClient(client.Client):
    _read_timeout = 1
    _write_timeout = 1

    def __init__(self, device, baudrate, debug = False):
        self._debug = debug

        if debug:
            debug_path = pathlib.Path('debug/read_bytes.txt')
            if not debug_path.parent.exists():
                debug_path.parent.mkdir(mode=0o775)
            self._log_file = open(debug_path, 'a')

        self._connect(device, baudrate)
        
    def __del__(self):
        if hasattr(self, '_serial'):
            self._serial.close()

        if self._debug:
            self._log_file.close()

    def _connect(self, device, baudrate):
        self._serial = serial.Serial(
            port = device,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            rtscts=True,
            write_timeout=self._write_timeout, 
            timeout=self._read_timeout
        )

    #Client methods
    def send(self, command):
        if not isinstance(command, bytes):
            command = bytes(command, 'utf-8')

        sleep(.1)
        self._serial.write(command.strip() + b'\r')

    def read_line(self):
        results = self._serial.readline()

        if self._debug:
            time = strftime('%H:%M:%S', localtime())
            self._log_file.write(f'{time} | read_line:\n{results}\n')
            self._log_file.write('\n')

        return results
    
    def read_bytes(self, size):
        results = self._serial.read(size)

        if self._debug:
            time = strftime('%H:%M:%S', localtime())
            self._log_file.write(f'{time} | read_bytes:\nsize: {size}\ndata: {results}\n')
            self._log_file.write('\n')

        return results
    
    def read_until(self, value):
        if not isinstance(value, bytes):
            value = bytes(value, 'utf-8')

        results = self._serial.read_until(value)

        if self._debug:
            time = strftime('%H:%M:%S', localtime())
            self._log_file.write(f'{time} | read_until:\nvalue: {value}\ndata: {results}\n')
            self._log_file.write('\n')

        return results
    
    def read_all(self):
        results = self._serial.read_all()

        if self._debug:
            time = strftime('%H:%M:%S', localtime())
            self._log_file.write(f'{time} | read_all:\n{results}\n')
            self._log_file.write('\n')

        return results
    
    def get_username(self):
        return None
    
    def change_timeout(self, value : int | float):
        self._serial.timeout = value

    def restore_timeout(self):
        self._serial.timeout = self._read_timeout
    
class SerialClientWithShell(SerialClient):
    _connected = False

    def __init__(self, device, baudrate, username, password, printer):
        super().__init__(device, baudrate)
        self._invoke_shell(username, password, printer)
        self._username = username
        
    def __del__(self):
        # logout
        if self._connected:
            self.send('exit')
        super().__del__()

    def _invoke_shell(self, username, password, printer):
        login_input = b'login: '
        password_input = b'Password: '
        connected_line = bytes(username + '@', 'utf-8')

        self.send('')
        self.read_line()
        line = self.read_bytes(len(connected_line if len(connected_line) < len(login_input) else login_input))
        printer('Logging in...')
        
        while True:
            if line.endswith(connected_line):
                printer(f'Already logged in as {username}')
                self._connected = True
                return
            elif line.endswith(login_input):
                self.send(username)
                line = self.read_until(password_input)

                if line.endswith(password_input):
                    self.send(password)
                    line = self.read_until(connected_line)

                    if line.endswith(connected_line):
                        printer('Successfully connected!')
                        self._connected = True
                        return
                raise Exception('Could not login: incorrect password or username')
            elif line.endswith(password_input):
                self.send(password)
                line = self.read_until(connected_line)

                if line.endswith(connected_line):
                    printer('Successfully connected!')
                    self._connected = True
                    return
                raise Exception('Could not login: incorrect password or username')
            else:
                char = self.read_bytes(1)
                if char:
                    line += char
                else:
                    raise Exception('Could not connect to device')
                
    def get_username(self):
        return self._username