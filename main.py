from importlib import import_module

from modules import configuration, validation, parse_args, print_information, run_configuration_commands, ftp, send_email
from report import csv_report
from device_connection import connection

def main():
    conf_file = 'configuration.json'
    connection_type, device_name, device, username, password, baud_rate = parse_args.parse_args()
    device_name : str = device_name.upper()
    
    device_conf = configuration.get_device_configuration(conf_file, device_name)
    validation.validate_connection_type(device_conf['connection'], connection_type, device_name)

    printer = print_information.PrintInformation()

    module = import_module(f'{connection_type}_connection.{connection_type}')
    function = getattr(module, connection_type)

    device_connection : connection.Connection
    device_connection, service_status = function(device_conf, device, username, password, baud_rate, device_name, printer)

    printer.print_on_current_line(f'Testing {device_name} device')
    printer.print_new_line()
    printer.print_new_line()

    device_connection.enable_echo(printer.print_on_current_line)

    validation.validate_modem(device_connection, device_conf['modem'], printer)

    manufacturer = device_connection.send_at_command(
        {"command": "AT+GMI", "arguments": [], "expected_code": "OK", "max_response_time": 300}, 
        printer)['results'][0]
    
    csv_file = csv_report.create_csv_file(device_name, manufacturer, device_conf['modem'])

    run_commands = run_configuration_commands.RunConfigurationCommands(device_connection, csv_file, printer)
    results = run_commands.run_commands(device_conf['commands'], True)

    getattr(module, 'reenable_service')(device_connection, service_status)

    ftp_configuration = configuration.get_ftp_configuration(conf_file)
    ftp.send_report(ftp_configuration['hostname'], ftp_configuration['username'], ftp_configuration['password'], ftp_configuration['port'], csv_file)

    subject = f"{device_conf['device']} device completed test"
    email_message = f"""Test completed!\n\nTested commands: {results['completed_commands']}
        Passed: {results['successful_commands']}
        Failed: {results['completed_commands'] - results['successful_commands']}"""
    
    email_configuration = configuration.get_email_configuration(conf_file)
    send_email.send_message(email_configuration, subject, email_message)

if __name__ == '__main__':
    main()