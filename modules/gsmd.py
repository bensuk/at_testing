import device_connection.connection as connection

def check_and_configure_gsmd(shell_client : connection.ShellConnection, printer):
    stop_gsmd_cmd = 'service gsmd stop'
    gsmd_status_cmd = 'service gsmd status'
    initial_status = ''

    printer('Checking gsmd status...')
    try:
        gsmd_status = shell_client.send_shell_command(gsmd_status_cmd)[0]
        initial_status = gsmd_status

        if gsmd_status == 'inactive':
            printer('gsmd service is already disabled')
        else:
            printer('Disabling gsmd service...')
            shell_client.send_shell_command(stop_gsmd_cmd)
            gsmd_status = shell_client.send_shell_command(gsmd_status_cmd)[0]

            if gsmd_status == 'inactive':
                printer('gsmd service is now inactive!')
            else:
                raise Exception("could not disable gsmd service")            
        
        return initial_status 
    
    except IndexError as err:
        raise Exception('could not receive information about gsmd service')
    
def reenable_gsmd(shell_client : connection.ShellConnection, initial_gsmd_status):
    start_gsmd_cmd = 'service gsmd start'
    gsmd_status_cmd = 'service gsmd status'

    if initial_gsmd_status == 'running':
        shell_client.send_shell_command(start_gsmd_cmd)
        try:
            gsmd_status = shell_client.send_shell_command(gsmd_status_cmd)[0]
            if gsmd_status == 'running':
                print('gsmd service re-enabled')
            else:
                print('Could not re-enable gsmd service')
        except IndexError as err:
            print('Could not re-enable gsmd service')