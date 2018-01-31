import os
from ctypes import *
def diconncet():
    os.chdir("E:/项目/洪（私）/pro/RSA_API/lib/x64")
    rsa300 = WinDLL("RSA_API.dll")
    print('Disconnecting.')
    rsa300.Disconnect()