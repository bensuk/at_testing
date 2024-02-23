from time import sleep

import client

def validate_command(command : str):
    if command[:2].upper() != 'AT':
        if command == '+++' or command.upper() == 'A/':
            return True
        else:
            print(f'Incorrect AT command {command} - AT commands should be started with "AT"')
            return False
    return True

def send_command(client : client.Client, command : str):
    try:
        client.send(command)
        
        lines = command.split()
        for line in lines:
            line = line.strip()
            results = client.read_until(line)
            
            if results[-len(line):].decode('utf-8') != line:
                print(f'The command/argument "{command}" has not been sent correctly.')
                return False
        return True
    except TimeoutError as err:
        print(f'The command/argument "{command}" has not been sent correctly. (TimeOutError exception)')
        return False


def get_results(client : client.Client):
    try:
        results = []
        while True:
            line = client.read_line()
            if line:
                line = line.rstrip().decode('utf-8')

                if line == 'OK':
                    return (line, results)
                elif 'ERROR' in line:
                    return (line, results)
                elif len(line) > 1:
                    results.append(line)
            else:
                print('Error with reading lines')
                return ('read_error', results)
    except TimeoutError as err:
        print('Error with reading lines (TimeOutError exception)')
        return ('read_error', results)