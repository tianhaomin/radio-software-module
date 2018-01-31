"""
Simple IQ Streaming Example using API for RSA306
Author: Morgan Allison
Date created: 10/5/15
Date edited: 11/18/15
Windows 7 64-bit
Python 2.7.9 64-bit (Anaconda 3.7.0)
NumPy 1.8.1, MatPlotLib 1.3.1
To get Anaconda: http://continuum.io/downloads
Anaconda includes NumPy and MatPlotLib
"""

import os
from ctypes import *

"""
################################################################
C:\Tektronix\RSA306 API\lib\x64 needs to be added to the
PATH system environment variable
################################################################
"""
os.chdir("E:/项目/洪（私）/pro\RSA_API/lib/x64")
rsa = WinDLL("RSA_API.dll")
# search/connect variables
numFound = c_int(0)
intArray = c_int*10
deviceIDs = intArray()
deviceSerial = create_string_buffer(8)
deviceType = create_string_buffer(8)
# search/connect
rsa.DEVICE_Search(byref(numFound),deviceIDs,deviceSerial,deviceType)
if numFound.value<1:
    print('No instruments found . Exiting script.')
    exit()
elif numFound.value == 1:
    print('One device found.')
    print('Device type:{}'.format(deviceSerial.value))
    rsa.DEVICE_Connect(deviceIDs[0])
else:
    print('Unexpected number of devices found, exiting script.')
    exit()

# initialize/assign variables
GNSS_Enable = c_bool(True)
GNSS_Power = c_bool(True)
GNSS_Power_Status = c_bool(True)
GNSS_Location_MsgLen = c_int(0)
GNSS_Location_Meg = c_char_p(b'')
rsa.GNSS_ClearNavMessageData
print('clear GNSS Message Data')
rsa.GNSS_SetEnable(GNSS_Enable)
rsa.GNSS_SetAntennaPower(GNSS_Power)
rsa.Run()
rsa.GNSS_GetAntennaPower(byref(GNSS_Power_Status))
print('The power of GNSS_Antenna is '+str(GNSS_Power_Status.value))
rsa.GNSS_GetEnable(byref(GNSS_Power_Status))
print(GNSS_Power_Status.value)
rsa.GNSS_GetNavMessageData(byref(GNSS_Location_MsgLen),byref(GNSS_Location_Meg))
print(GNSS_Location_Meg.value)
print(GNSS_Location_MsgLen.value)

rsa.DEVICE_Disconnect()
print('The device is disconnecting')
