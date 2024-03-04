from device_connection import connection
from serial_connection import serial_client
from modules import print_information, modem_manager

def serial_modem(conf, device, baudrate, printer : print_information.PrintInformation):
    client = serial_client.SerialClient(device, baudrate)
    session = connection.Connection(client)
    
    reenable_ModemManager = modem_manager.check_and_configure(printer.print_on_current_line)

    return session, reenable_ModemManager 