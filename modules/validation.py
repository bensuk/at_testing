import connection

def validate_connection_type(configuration, connection_type):
    connection_type = connection_type.lower()

    for connection in configuration['connection']:
        if connection.lower() == connection_type:
            return True
    else:
        raise Exception(f'Given {connection_type} is not valid for this device. {configuration["device"]} device supports {configuration["connection"]} connections')
    
def validate_device_name(shell : connection.ShellConnection, device_name):
    command = 'uci show system.system.device_code'

    try:
        name = shell.send_shell_command(command)[0]
        if not device_name.upper() in name:
            raise Exception(f'Connected device is not {device_name}')
    except IndexError as err:
        raise Exception('Could not get device name from device itself')
    
def validate_modem(shell : connection.ShellConnection, modem_name):
    command = {"command": "AT+GMM", "arguments": [], "expected_code": "OK", "max_response_time": 300}
    results = shell.send_at_command(command)['results']

    if results:
        if results[0].upper() == modem_name.upper():
            return True
    raise Exception('Device modem does not match the modem in the configuration')

def validate_file_extension(file, extension):
    if file.lower().endswith(extension.lower()):
        return True
    return False