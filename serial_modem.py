import serial_client
import connection
from modules import modem_manager, validation
import run_configuration_commands
import csv_report

def serial_modem(configuration, device, baudrate = 115200):
    reenable_ModemManager = modem_manager.check_and_configure()

    client = serial_client.SerialClient(device, baudrate)
    session = connection.Connection(client)

    print(f'Testing {configuration["device"]} device...\n')

    print('Enabling AT echoing')
    session.enable_echo()
    print()

    validation.validate_modem(session, configuration['modem'])
    
    manufacturer = session.send_at_command(
        {"command": "AT+GMI", "arguments": [], "expected_code": "OK", "max_response_time": 300})['results'][0]
    
    csv_file = csv_report.create_csv_file(configuration['device'], manufacturer, configuration['modem'])

    run_configuration_commands.run_commands_multiprocessing(session, configuration['commands'], csv_file)

    modem_manager.reenable_modem_manager(reenable_ModemManager)