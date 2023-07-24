import os
import sys
import subprocess
import time
import threading
import TxttoXlsx
from win32com.client import *
from win32com.client.connect import *


application = win32com.client.DispatchEx("CANalyzer.Application")

application.Open(r"C:\Users\GFLTTM2.AUDI\Desktop\IPC_Tests\IPC_Simulator\IPC_Simulatore.cfg")

application.measurement.start()

time.sleep(30)

application.measurement.stop()

file_path=os.chdir(r'C:\Users\GFLTTM2.AUDI\Desktop\IPC_Tests')

TxttoXlsx.create_xlsx_file(file_path)










 







