import subprocess

def check_and_configure():
    check_modem_manager = 'systemctl is-active ModemManager.service'
    disable_modem_manager = 'systemctl stop ModemManager.service'

    print('Checking if ModemManager is active...')
    if subprocess.run(check_modem_manager.split(), stdout=subprocess.DEVNULL).returncode == 0:
        print('\tDisabling ModemManager...')
        subprocess.run(disable_modem_manager.split(), stdout=subprocess.DEVNULL)
        reenable_ModemManager = True

        if subprocess.run(check_modem_manager.split(), stdout=subprocess.DEVNULL).returncode != 0:
            print('\tModemManager is successfully disabled!')
        else:
            raise Exception('Could not disabled ModemManager')
    else:
        reenable_ModemManager = False
        print('\tModemManager is already disabled')

    print()
    return reenable_ModemManager

def reenable_modem_manager(reenable):
    check_modem_manager = 'systemctl is-active ModemManager.service'
    enable_modem_manager = 'systemctl start ModemManager.service'

    if reenable:
        subprocess.run(enable_modem_manager.split(), stdout=subprocess.DEVNULL)
        if subprocess.run(check_modem_manager.split(), stdout=subprocess.DEVNULL).returncode == 0:
            print('ModemManager is successfully (re)activated')
        else:
            print('Could not reenable ModemManager')
    
    print()