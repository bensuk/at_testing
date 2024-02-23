import connection    

def check_and_configure_socat(shell_client : connection.ShellConnection):
    if not shell_client.send_shell_command('opkg list-installed | grep socat'):
        print('socat is not installed, cannot perform tests')

        #maybe add input if you want to install
        try:
            size = shell_client.send_shell_command('opkg info socat | grep -i size')[-1].split()[-1]
            if size.isnumeric():
                size = round(int(size)/1024)
                print(f'\tinstalling socat ({size} KiB)...')
        except:
            print(f'\tinstalling socat...')
            
        shell_client.send_shell_command('opkg update')
        shell_client.send_shell_command('opkg install socat')

        if shell_client.send_shell_command('opkg list-installed | grep socat'):
            print("\tsocat has been successfully installed!")
        else:
            raise Exception('cannot perform tasks without socat installed')
        print()