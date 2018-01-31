from ctypes import *
import os
os.chdir("E:/项目/洪（私）/pro\RSA_API/lib/x64")
rsa = cdll.LoadLibrary("RSA_API.dll")
# search/connect variables
numFound = c_int(0)
intArray = c_int*10
deviceIDs = intArray()
deviceSerial = create_string_buffer(8)
deviceType = create_string_buffer(8)
def search(numFound,deviceIDs,deviceSerial,deviceType):
    rsa.DEVICE_Search(byref(numFound), deviceIDs, deviceSerial, deviceType)
    if numFound.value < 1:
        print('No instruments found . Exiting script.')
        exit()
    elif numFound.value == 1:
        print('One device found.')
        print('Device type:{}'.format(deviceSerial.value))
        # rsa.DEVICE_Connect(deviceIDs[0])
    else:
        print('Unexpected number of devices found, exiting script.')
        exit()

if __name__ == "__main__":
    search(numFound, deviceIDs, deviceSerial, deviceType)
