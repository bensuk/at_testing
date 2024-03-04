from modules import gsmd, modem_manager
from device_connection import connection

def serial(configuration, device, username, password, baudrate, device_name, printer):
    if device_name[:3].upper() == 'TRM':
        from serial_connection import serial_modem
        return serial_modem.serial_modem(configuration, device, baudrate, printer)
    else:
        from serial_connection import serial_console
        return serial_console.serial_console(configuration, device, username, password, baudrate, device_name, printer)
    
def reenable_service(conn, service_status):
    if isinstance(conn, connection.ShellConnection):
        gsmd.reenable_gsmd(conn, service_status)
    else:
        modem_manager.reenable_modem_manager(service_status)