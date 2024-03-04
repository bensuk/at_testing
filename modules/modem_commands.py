import modules.print_information as print_information

import client.client as client

def validate_command(command : str, printer : print_information.PrintInformation, print_warnings):
    if command[:2].upper() != 'AT':
        if command == '+++' or command.upper() == 'A/':
            return True
        else:
            if print_warnings:
                printer.print_new_line(f'Incorrect AT command "{command}" - AT commands should be started with "AT"\n\n')
            return False
    return True

def send_command(client : client.Client, command : str, printer : print_information.PrintInformation, print_warnings):
    try:
        client.send(command)
        
        lines = command.split()
        for line in lines:
            line = line.strip()
            results = client.read_until(line)
            
            if results[-len(line):].decode('utf-8') != line:
                if print_warnings:
                    printer.print_new_line(f'The command/argument "{command}" has not been sent correctly\n\n')
                return False
        return True
    except TimeoutError as err:
        if print_warnings:
            printer.print_new_line(f'The command/argument "{command}" has not been sent correctly (TimeOutError exception)\n\n')
        return False

def get_results(client : client.Client, printer : print_information.PrintInformation, print_warnings):
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
                if print_warnings:
                    printer.print_new_line('Error with reading lines\n\n')
                return ('read_error', results)
    except TimeoutError as err:
        if print_warnings:
            printer.print_new_line('Error with reading lines (TimeOutError exception)\n\n')
        return ('read_error', results)