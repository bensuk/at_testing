from time import sleep

from client import client
from modules import print_information, modem_commands

#directly connected to AT
class Connection:
    def __init__(self, client : client.Client, printer : print_information.PrintInformation):
        self._client = client
        self._printer = printer
        self.enable_echo()

    def send_at_command(self, command, print_warnings = True):
        self._printer.print_on_current_line(f'Sending "{command["command"]}" command...')

        if not modem_commands.validate_command(command['command'], self._printer, print_warnings):
            return {'command': command["command"], 'result_code': 'validation_error', 'results': []}
        
        if not modem_commands.send_command(self._client, command['command'], self._printer, print_warnings):
            return {'command': command["command"], 'result_code': 'send_error', 'results': []}
        
        if command['arguments']:
            sleep(1)
            error = b'ERROR'
            data = self._client.read_all().split(b'\n')

            for line in data:
                if error in line:
                    if print_warnings:
                        self._printer.print_new_line(f'Command "{command["command"]}" produced ERROR, not sending any arguments\n\n')
                    return {'command': command["command"], 'result_code': line.strip().decode('utf-8'), 'results': []}

            for argument in command['arguments']:
                if not modem_commands.send_command(self._client, argument, self._printer, print_warnings):
                    self._client.send('\x1a')
                    return {'command': command["command"], 'result_code': 'send_error', 'results': []}
                
            self._client.send('\x1a')

        self._client.change_timeout(command['max_response_time'])

        code, results = modem_commands.get_results(self._client, self._printer, print_warnings)

        self._client.restore_timeout()

        return {'command': command['command'], 'result_code': code, 'results': results}

    def send_many_at_commands(self, commands, print_warnings = True):
        results = []
        for command in commands:
            results.append(self.send_at_command(command, print_warnings))
        else:
            return results

    def send_many_at_commands_callback(self, commands, process_result, print_warnings = True):
        count = len(commands)

        for i, command in enumerate(commands):
            self._printer.print_on_current_line(f'Testing "{command["command"]}" command ({i+1} of {count}):\n')
            results = self.send_at_command(command, print_warnings)
            process_result(results)

    def enable_echo(self, print_warnings = True):
        self._printer.print_on_current_line('Enabling AT echoing...')
        
        self._client.send('ATE1')
        code, results = modem_commands.get_results(self._client, self._printer, print_warnings)

        if code != 'OK':
            raise(Exception('Could not enable echo mode'))
        
    def get_modem_manufacturer(self):
        return self.send_at_command(
            {"command": "AT+GMI", "arguments": [], "expected_code": "OK", "max_response_time": 300},
            self._printer)['results'][0]
    
#RUT and RUTX routers
class ShellConnection(Connection):
    _default_modem_port = '/dev/ttyUSB3'

    def __init__(self, client, printer : print_information.PrintInformation, modem_port=_default_modem_port):
        self.set_modem_connection_command(modem_port)
        super().__init__(client, printer)

    def send_shell_command(self, command):
        try:
            self._client.send(command)

            connected_line = bytes(f'{self._client.get_username()}@', 'utf-8')
            lines = self._client.read_until(connected_line).split(b'\n')

            echo_command = 'echo done'
            self._client.send(echo_command)

            results = []
            add = False
            while True:
                line = lines.pop(0) if lines else self._client.read_line()
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
        
    def set_modem_connection_command(self, port):
        self._command = bytes(f'socat /dev/tty,raw,echo=0,escape=0x03 {port},raw,setsid,sane,echo=0,nonblock ; stty sane\r', 'utf-8')

    def send_at_command(self, command, print_warnings = True):
        self.connect_to_modem()
        result = super().send_at_command(command, print_warnings)
        self.disconnet_from_modem()
        
        return result
    
    def send_many_at_commands(self, commands, print_warnings = True):    
        self.connect_to_modem()

        results = []
        for command in commands:
            results.append(super().send_at_command(command, print_warnings))
        else:
            self.disconnet_from_modem()
            return results

    def send_many_at_commands_callback(self, commands, process_result, print_warnings = True):
        self.connect_to_modem()
        count = len(commands)

        for i, command in enumerate(commands):
            self._printer.print_on_current_line(f'Testing "{command["command"]}" command ({i+1} of {count}):\n')
            results = super().send_at_command(command, print_warnings)
            process_result(results)

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
    
    def enable_echo(self, print_warnings = True):
        self.connect_to_modem()
        super().enable_echo(print_warnings)
        self.disconnet_from_modem()