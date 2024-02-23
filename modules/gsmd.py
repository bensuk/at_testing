import connection    

def check_and_configure_gsmd(shell_client : connection.ShellConnection):
    stop_gsmd_cmd = 'service gsmd stop'
    gsmd_status_cmd = 'service gsmd status'
    initial_status = ''

    print('Checking gsmd status...')
    try:
        gsmd_status = shell_client.send_shell_command(gsmd_status_cmd)[0]
        initial_status = gsmd_status
        print('\tservice gsmd status:', gsmd_status)

        if gsmd_status == 'inactive':
            print('\tgsmd service is already disabled')
        else:
            print('\tdisabling gsmd service...')
            shell_client.send_shell_command(stop_gsmd_cmd)
            gsmd_status = shell_client.send_shell_command(gsmd_status_cmd)[0]

            if gsmd_status == 'inactive':
                print('\tgsmd service is now inactive!')
            else:
                raise Exception("could not disable gsmd service")
            
        print()
        return initial_status 
    
    except IndexError as err:
        raise Exception('could not receive information about gsmd service')
    
def reenable_gsmd(shell_client : connection.ShellConnection, initial_gsmd_status):
    start_gsmd_cmd = 'service gsmd start'
    gsmd_status_cmd = 'service gsmd status'

    if initial_gsmd_status == 'running':
        print('enabling gsmd service')
        shell_client.send_shell_command(start_gsmd_cmd)
        try:
            gsmd_status = shell_client.send_shell_command(gsmd_status_cmd)[0]
            if gsmd_status == 'running':
                print('\tgsmd service reenabled')
            else:
                print('\tcould not enable gsmd service')
        except IndexError as err:
            print('\tcould not receive information about gsmd service')