from device_connection import connection
from serial_connection import serial_client
from modules import gsmd, socat, validation, print_information

def serial_console(conf, device, username, password, baudrate, device_name, printer : print_information.PrintInformation):
    client = serial_client.SerialClientWithShell(device, baudrate, username, password, printer.print_on_current_line)
    shell = connection.ShellConnection(client, printer, conf['modem_port'])

    validation.validate_device_name(shell, device_name)
    socat.check_and_configure_socat(shell, client, printer.print_on_current_line)
    initial_gsmd_status = gsmd.check_and_configure_gsmd(shell, printer.print_on_current_line)

    return shell, initial_gsmd_status