import device_connection.connection as connection

def validate_connection_type(configuration_connection, connection_type, device_name):
    connection_type = connection_type.lower()

    for connection in configuration_connection:
        if connection.lower() == connection_type:
            return
    else:
        raise Exception(f'Given {connection_type} is not valid for this device. {device_name} device supports {configuration_connection} connections')
    
def validate_device_name(shell : connection.ShellConnection, device_name):
    command = 'uci show system.system.device_code'

    try:
        name = shell.send_shell_command(command)[0]
        if not device_name.upper() in name:
            raise Exception(f'Connected device is not {device_name}')
    except IndexError as err:
        raise Exception('Could not get device name from device itself')
    
def validate_modem(shell : connection.Connection, modem_name, printer):
    command = {"command": "AT+GMM", "arguments": [], "expected_code": "OK", "max_response_time": 300}
    results = shell.send_at_command(command, printer)

    if results['result_code'] == 'OK' and results['results']:
        if results['results'][0].upper() == modem_name.upper():
            return True
        else:
            raise Exception('Device modem does not match the modem in the configuration')
    raise Exception('Could not get modem information')