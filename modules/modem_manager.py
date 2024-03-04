import subprocess

def check_and_configure(printer):
    check_modem_manager = 'systemctl is-active ModemManager.service'
    disable_modem_manager = 'systemctl stop ModemManager.service'

    printer('Checking if ModemManager is active...')
    if subprocess.run(check_modem_manager.split(), stdout=subprocess.DEVNULL).returncode == 0:
        printer('Disabling ModemManager...')
        subprocess.run(disable_modem_manager.split(), stdout=subprocess.DEVNULL)
        reenable_ModemManager = True

        if subprocess.run(check_modem_manager.split(), stdout=subprocess.DEVNULL).returncode != 0:
            printer('ModemManager is successfully disabled!')
        else:
            raise Exception('Could not disable ModemManager')
    else:
        reenable_ModemManager = False
        printer('ModemManager is already disabled')
    return reenable_ModemManager

def reenable_modem_manager(reenable):
    check_modem_manager = 'systemctl is-active ModemManager.service'
    enable_modem_manager = 'systemctl start ModemManager.service'

    if reenable:
        subprocess.run(enable_modem_manager.split(), stdout=subprocess.DEVNULL)
        if subprocess.run(check_modem_manager.split(), stdout=subprocess.DEVNULL).returncode == 0:
            print('ModemManager is now re-enabled')
        else:
            print('Could not re-enable ModemManager')