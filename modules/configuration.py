import json

def getConfiguration(configurationFile, device):
    try:
        with open(configurationFile, "r") as data_file:
            results = json.load(data_file)

        for configuration in results:
            if configuration['device'].lower() == device.lower():
                return configuration
        else:
            raise Exception(f'There is no configuration for "{device}" device')

    except KeyError as err:
        raise Exception(f'Missing {err} field in configuration file. Configuration file is incorrect')