import device_connection.connection as connection
import client.client as client

def check_and_configure_socat(shell_client : connection.ShellConnection, client : client.Client, printer):
    _timeout_value = 60

    if not shell_client.send_shell_command('opkg list-installed | grep socat'):
        printer('socat is not installed, cannot perform tests')

        test = input('Install socat? y/n ')

        if test != 'y':
            printer('Exiting program as without socat cannot continue...')
            exit(1)

        client.change_timeout(_timeout_value)
        try:
            size = shell_client.send_shell_command('opkg info socat | grep -i size')[-1].split()[-1]
            if size.isnumeric():
                size = round(int(size)/1024)
                printer(f'Installing socat ({size} KiB)...')
        except:
            printer('Installing socat...')
            
        update_status = shell_client.send_shell_command('opkg update --force_feeds /etc/opkg/openwrt/distfeeds.conf')

        if not update_status[-1]:
            raise Exception(f'Could not install socat: {update_status[-2]}')        

        shell_client.send_shell_command('opkg install socat --force_feeds /etc/opkg/openwrt/distfeeds.conf')

        if shell_client.send_shell_command('opkg list-installed | grep socat'):
            printer('socat has been successfully installed!')
        else:
            raise Exception('Could not install socat. Cannot perform tasks without socat.')
        
        client.restore_timeout()