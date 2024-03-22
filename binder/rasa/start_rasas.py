import requests
from threading import Thread
import subprocess
import os
import time
flag = True
insFlag = True

def run_pip_install():
    global insFlag
    
    try:
        import rasa
        print("RASA imported")
        insFlag = False
    except ImportError:
        print("RASA package not available")
        print('Installing RASA')
        rasa_command = "pip install -q --upgrade pip && pip install -q rasa"
        # process = subprocess.run(rasa_command, shell=True, capture_output=True, text=True)
        process = subprocess.Popen(rasa_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
        import rasa
        print("RASA installed and imported")       
        insFlag = False
    
def run_bash_command(command):
    # process = subprocess.run(command, shell=True, capture_output=True, text=True)
    # print("Rasa command")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print('Starting RASA Server',end='')
    for line in iter(process.stdout.readline, ''):
        print(line, end='')
        if 'up and running' in line:
          print("SERVER READY")
    
    
if __name__ == '__main__':

    # Define your Bash command
    bash_command = "rasa run --enable-api"
    
    bash_thread1 = Thread(target=run_pip_install)
    bash_thread1.start()
    
    while True:
        time.sleep(3)
        if not insFlag:
            print('RASA package ready to use')
            break
        else:
            print(".",end='')
    
    bash_thread1.join()
    
    # Start Flask app in a separate thread
    # bash_thread2 = Thread(target=run_bash_command, args=(bash_command,))
    # bash_thread2.daemon = True
    # bash_thread2.start()
    run_bash_command(bash_command)
