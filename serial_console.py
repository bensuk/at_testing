import serial_client
import connection
from modules import gsmd, socat, validation
import run_configuration_commands
import csv_report

def serial_console(configuration, device, username, password, baudrate = 115200):
    client = serial_client.SerialClientWithShell(device, baudrate, username, password)
    shell = connection.ShellConnection(client)

    validation.validate_device_name(shell, configuration['device'])

    socat.check_and_configure_socat(shell)
    initial_gsmd_status = gsmd.check_and_configure_gsmd(shell)

    print(f'Testing {configuration["device"]} device...\n')

    print('Enabling AT echoing')
    shell.enable_echo()
    print()

    validation.validate_modem(shell, configuration['modem'])

    manufacturer = shell.send_at_command(
        {"command": "AT+GMI", "arguments": [], "expected_code": "OK", "max_response_time": 300})['results'][0]
    
    csv_file = csv_report.create_csv_file(configuration['device'], manufacturer, configuration['modem'])

    run_configuration_commands.run_commands_multiprocessing(shell, configuration['commands'], csv_file)

    gsmd.reenable_gsmd(shell, initial_gsmd_status)