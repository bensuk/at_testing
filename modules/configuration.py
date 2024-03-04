import json

def get_device_configuration(configurationFile, device):
    required_fields = ['device', 'modem', 'connection', 'commands']
    required_command_fields = ['command', 'arguments', 'expected_code', 'max_response_time']

    try:
        with open(configurationFile, "r") as data_file:
            results = json.load(data_file)

        for configuration in results['devices_commands']:
            if configuration['device'].upper() == device.upper():
                if validate_configuration(configuration, required_fields):
                    for command in configuration['commands']:
                        if not validate_configuration(command, required_command_fields):
                            raise Exception('Incorrect configuration file')
                    return configuration
                else:
                    raise Exception('Incorrect configuration file')
        else:
            raise Exception(f'There is no configuration for "{device}" device')
    except KeyError as err:
        raise Exception(f'Missing {err} field in configuration file. Configuration file is incorrect')

def get_ftp_configuration(configurationFile):
    fields = ['hostname', 'port', 'username', 'password']

    try:
        with open(configurationFile, "r") as data_file:
            results = json.load(data_file)

        configuration = results['ftp_server']

        if validate_configuration(configuration, fields):
            return configuration
        else:
            raise Exception('Incorrect configuration file. Unable to retrieve the required configuration for the FTP server') 
    except KeyError as err:
        raise Exception(f'Missing {err} field in the configuration file. Unable to retrieve the required configuration for the FTP server')
    
def get_email_configuration(configurationFile):
    fields = ['port', 'smtp_server', 'sender_email', 'password', 'receiver_email']

    try:
        with open(configurationFile, "r") as data_file:
            results = json.load(data_file)

        configuration = results['smtp']

        if validate_configuration(configuration, fields):
            return configuration
        else:
            raise Exception('Incorrect configuration file. Unable to retrieve the required configuration for the email') 
    except KeyError as err:
        raise Exception(f'Missing {err} field in the configuration file. Unable to retrieve the required configuration for the email')
    
def validate_configuration(configuration, fields):
    for field in fields:
        if not field in configuration:
            return False
    return True