import subprocess
import sys
import os

class Install_Packages:
    get_pckg = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    installed_packages = [r.decode().split('==')[0] for r in get_pckg.split()]
    required_packages = ['xmltodict']    
    for packg in required_packages:
        if packg in installed_packages:
            pass
        else:
            os.system('pip install ' + packg)