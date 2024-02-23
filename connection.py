from time import sleep

import client, at

#directly connected to AT
class Connection:
    def __init__(self, client : client.Client):
        self._client = client

    def send_at_command(self, command):
        # print(f'Executing {command}...')

        if not at.validate_command(command['command']):
            return {'command': command["command"], 'result_code': 'validation_error', 'results': []}
        
        if not at.send_command(self._client, command['command']):
            return {'command': command["command"], 'result_code': 'send_error', 'results': []}
        
        if command['arguments']:
            sleep(1)
            error = b'ERROR'
            data = self._client.read_all().split(b'\n')

            for line in data:
                if error in line:
                    print(f'Command "{command["command"]}" produced ERROR, not sending any arguments')
                    return {'command': command["command"], 'result_code': line.strip().decode('utf-8'), 'results': []}

            for argument in command['arguments']:
                if not at.send_command(self._client, argument):
                    self._client.send('\x1a')
                    return {'command': command["command"], 'result_code': 'send_error', 'results': []}
                
            self._client.send('\x1a')

        self._client.change_timeout(command['max_response_time'])

        code, results = at.get_results(self._client)

        self._client.restore_timeout()

        return {'command': command['command'], 'result_code': code, 'results': results}

    def send_many_at_commands(self, commands):
        results = []
        for command in commands:
            results.append(self.send_at_command(command))
        else:
            return results
        
    def send_many_at_commands_multiprocessing(self, commands : list, results : list):
        for command in commands:
            results.append(self.send_at_command(command))
            
    def enable_echo(self):
        self._client.send('ATE1')
        code, results = at.get_results(self._client)

        if code != 'OK':
            raise(Exception('Could not enable echo mode'))
    
#RUT and RUTX routers
class ShellConnection(Connection):
    _command = b'socat /dev/tty,raw,echo=0,escape=0x03 /dev/ttyUSB3,raw,setsid,sane,echo=0,nonblock ; stty sane\r'
    
    def __init__(self, client):
        super().__init__(client)

    def send_shell_command(self, command):
        try:
            self._client.send(command)

            echo_command = 'echo done'
            self._client.send(echo_command)

            results = []
            add = False
            while True:
                line = self._client.read_line()
                if line:
                    line = line.rstrip().decode('utf-8')

                    if line == 'done':
                        return results
                    elif add and echo_command not in line:
                        results.append(line)
                    elif line[-len(command):] == command:
                        add = True
                else:
                    raise(Exception('Error sending shell command'))
        except TimeoutError as err:
            raise(Exception('Error sending shell command (TimeoutError)'))

    def send_at_command(self, command):
        self.connect_to_modem()
        result = super().send_at_command(command)
        self.disconnet_from_modem()
        
        return result
    
    def send_many_at_commands(self, commands):    
        self.connect_to_modem()

        results = []
        for command in commands:
            results.append(super().send_at_command(command))
        else:
            self.disconnet_from_modem()
            return results
        
    def send_many_at_commands_multiprocessing(self, commands : list, results : list):
        self.connect_to_modem()

        for command in commands:
            results.append(super().send_at_command(command))
        
        self.disconnet_from_modem()
    
    def connect_to_modem(self):
        try:
            self._client.send(self._command)

            line = b''
            append = False
            while True:
                current_line = self._client.read_line()

                if not current_line:
                    raise Exception('Could not connect to modem, cannot send AT commands')

                if append:
                    line += current_line.strip()
                else:
                    line = current_line.strip()

                append = current_line[-3:] == b'\r\r\n'

                if self._command.strip() in line:
                    # print('ready to send AT commands')
                    return
        except TimeoutError as err:
            raise Exception('Could not connect to modem, cannot send AT commands (TimeoutError)')
    
    def disconnet_from_modem(self):
        try:
            self._client.send('\x03')

            connected_line = bytes(f'{self._client.get_username()}@', 'utf-8')
            data = self._client.read_until(connected_line)

            if data[-len(connected_line):] == connected_line:
                return
            else:
                raise Exception('Could not disconnect from modem')
        except TimeoutError as err:
            raise Exception('Could not disconnect from modem (TimeoutError)')
    
    def enable_echo(self):
        self.connect_to_modem()
        super().enable_echo()
        self.disconnet_from_modem()