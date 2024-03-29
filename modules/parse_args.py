import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Test the device's modem with AT commands using commands from the given configuration file.")

    parser.add_argument(
        "-c",
        "--connection",
        required=True,
        help="The type of connection for connection to the device",
        choices=["serial", "ssh"]
    )

    parser.add_argument(
        "-dev",
        "--device",
        required=True,
        help="Name of the device to be connected. (For example: RUTX11, TRM240, etc.)"
    )

    parser.add_argument(
        "-host",
        "--hostname",
        required=True,
        help="Hostname for ssh connection or port name for serial connection"
    )

    parser.add_argument(
        "-u",
        "--username",
        help="The user name for logging in to the device. Not required if device is TRM series"
    )

    parser.add_argument(
        "-p",
        "--password",
        help="The password for logging in to the device. Not required if device is TRM series"
    )

    parser.add_argument(
        "-rate",
        "--baud-rate",
        help="Baud rate for serial connection"
    )

    args = parser.parse_args()

    if args.device[:3].upper() != 'TRM':
        if not args.username or not args.password:
            parser.error('Username and password parameters are required if the device is not a TRM series.')

    #baud rate required if connection is serial
    if args.connection == 'serial':
        if not args.baud_rate:
            parser.error('Please specify baud rate for serial connection')

    return args.connection, args.device.upper(), args.hostname, args.username, args.password, args.baud_rate