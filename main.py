from importlib import import_module

from modules import configuration, validation, parse_args, print_information, run_configuration_commands
from device_connection import connection

def main():
    conf_file = 'configuration.json'
    connection_type, device_name, device, username, password, baud_rate = parse_args.parse_args()
    
    device_conf = configuration.get_device_configuration(conf_file, device_name)
    validation.validate_connection_type(device_conf['connection'], connection_type, device_name)

    printer = print_information.PrintInformation()

    module = import_module(f'{connection_type}_connection.{connection_type}')
    function = getattr(module, connection_type)

    device_connection : connection.Connection
    device_connection, service_status = function(device_conf, device, username, password, baud_rate, device_name, printer)

    printer.print_testing_start(device_name)

    validation.validate_modem(device_connection, device_conf['modem'], printer)

    run_configuration_commands.RunConfigurationCommands(device_connection, printer, device_conf, conf_file).run_commands(True)

    getattr(module, 'reenable_service')(device_connection, service_status)

if __name__ == '__main__':
    main()