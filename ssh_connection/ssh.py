from device_connection import connection
from ssh_connection import ssh_client
from modules import gsmd, socat, validation, print_information

def ssh(conf, hostname, username, password, baud_rate, device_name, printer : print_information.PrintInformation):
    client = ssh_client.SSHClient(hostname, username, password, debug=True, device_name=device_name)
    shell = connection.ShellConnection(client, printer, conf['modem_port'])

    validation.validate_device_name(shell, device_name)
    socat.check_and_configure_socat(shell, client, printer.print_on_current_line)
    initial_gsmd_status = gsmd.check_and_configure_gsmd(shell, printer.print_on_current_line)

    return shell, initial_gsmd_status

def reenable_service(shell, service_status):
    gsmd.reenable_gsmd(shell, service_status)