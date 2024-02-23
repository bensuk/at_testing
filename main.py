from modules import configuration, validation
import parse_args

def main():
    conf_file = 'configuration.json'
    connection_type, device_name, device, username, password = parse_args.parse_args()
    
    conf = configuration.getConfiguration(conf_file, device_name)
    validation.validate_connection_type(conf, connection_type)

    #ssh, serial_modem, serial_console
    if connection_type.lower() == 'serial':
        if device_name[:3].upper() == 'TRM':
            import serial_modem
            serial_modem.serial_modem(conf, device)
        else:
            import serial_console
            serial_console.serial_console(conf, device, username, password)
    else:
        import ssh
        ssh.ssh(conf, device, username, password)

if __name__ == '__main__':
    main()