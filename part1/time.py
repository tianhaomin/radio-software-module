import os
from ctypes import *
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
refTimeSec = c_int(0)
refTimeNsec = c_int(0)
refTimeStamp = c_int(0)
# rsa.REFTIME_SetReferenceTime(refTimeSec,refTimeNsec,refTimeStamp)
# print(refTimeStamp.value)
# get reference time`
rsa.REFTIME_GetReferenceTime(byref(refTimeSec),byref(refTimeNsec),byref(refTimeStamp))
print(refTimeSec.value)
# get current time
o_timeSec = c_int(0)
o_timeNsec = c_int(0)
o_timeStamp = c_int(0)
rsa.REFTIME_GetCurrentTime(byref(o_timeSec),byref(o_timeNsec),byref(o_timeStamp))
print(o_timeSec.value)


