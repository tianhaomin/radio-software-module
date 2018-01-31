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
# create Spectrum_Settings data structure
class Spectrum_Settings(Structure):
    __fields__ = [('span',c_double),
                  ('rbw',c_double),
                  ('vbw',c_double),
                  ('traceLength',c_int),
                  ('window',c_int),
                  ('verticalUnit',c_int),
                  ('actualStartFreq',c_double),
                  ('actualStopFreq',c_double),
                  ('actualFreqStepSize',c_double),
                  ('actualRBW',c_double),
                  ('actualVBW',c_double),
                  ('actualNumIQSamples',c_double)]

refLevel = c_double(-40)
rsa.CONFIG_SetReferenceLevel(refLevel)
# acquisition IQ data
rsa.DEVICE_Run()
# data transfer variables
recordLength = c_int(1024)
actLength = c_int(0)
iqArray = c_float*recordLength.value
iData = iqArray()
qData = iqArray()
timeoutMsec = c_int(1000)
ready = c_bool(False)
rsa.DEVICE_Run()
# check for data ready
while ready.value == False:
    rsa.IQBLK_WaitForIQDataReady(timeoutMsec,byref(ready))
# query Q and I data
rsa.IQBLK_GetIQDataDeinterleaved(byref(iData),byref(qData),
                                 byref(actLength),recordLength)
print('Got IQ data')
rsa.DEVICE_Stop()
# plot IQ figure
from ctypes import *
import numpy as np
import matplotlib.pyplot as plt
bla = np.arange(1,5)
print(bla)
I = np.ctypeslib.as_array(iData)
Q = np.ctypeslib.as_array(qData)
recordLength = c_int(0)
iqSampleRate = c_double(0)
rsa.IQBLK_GetIQSampleRate(byref(iqSampleRate))
rsa.IQBLK_GetRecordLength(byref(recordLength))
time = np.linspace(0,recordLength.value/iqSampleRate.value,recordLength.value)
# PLOTS
plt.suptitle('I and Q vs Time',fontsize='20')
plt.subplot(211,axisbg='k')
plt.plot(time*1e3,I,c='red')
plt.ylabel('I(V)')
plt.subplot(212,axisbg='k')
plt.plot(time*1e3,Q,c='blue')
plt.xlabel('Time(msec)')
plt.show()
print('Disconnecting.')
ret = rsa.DEVICE_Disconnect()
# plot spectrum
cf = c_double(1e9) # center freq
refLevel = c_double(0)
rsa.CONFIG_SetCenterFreq(cf)
rsa.CONFIG_SetReferenceLevel(refLevel)
# create an instance of the Spectrum_Settings struct
specSet = Spectrum_Settings()
# configure desired spectrum settings
# some fields are left blank because the default
# values set by SPECTRUM_SetDefault() are acceptable
specSet.span = c_double(40e6)
specSet.rbw = c_double(30e3)
# specSet.enableVBW =
# specSet.vbw =
specSet.traceLength = c_int(801)
# specSet.window =
# specSet.verticalUnit =
# specSet.actualStartFreq =
# specSet.actualFreqStepSize =
# specSet.actualRBW =
# specSet.actualVBW =
# specSet.actualNumIQSamples =
enable = c_bool(True)
rsa.SPECTRUM_SetEnable(enable)
rsa.SPECTRUM_SETDEFAULT()
rsa.SPECTRUM_GetSettings(byref(specSet))
# set desired spectrum settings
rsa.SPECTRUMSetSettings(specSet)
rsa.SPECTRUM_GetSettings(byref(specSet))
traceArray = c_float * specSet.traceLength
traceData = traceArray()
outTracePoints = c_int()
# generate frequency array for plotting the spectrum
freq = np.arange(specSet.actualStartFreq,
                 specSet.actualStartFreq+specSet.actualFreqStepSize*specSet.traceLength,
                 specSet.actualFreqStepSize)
# start acquisition
rsa.DEVICE_Run()
while ready.value == False:
    rsa.SPECTRUM_WaitForDataReady(timeoutMsec,byref(ready))
rsa.SPEXTRUM_GetTrace(c_int(0),specSet.traceLength,
                      byref(traceData),byref(outTracePoints))
rsa.DEVICE_Stop()
# plot the spectrum trace
plt.figure(1)
plt.subplot(111,axisbg='k')
plt.plot(freq,traceData,'y')
plt.ylabel('Amplitude (dBm)')
plt.xlabel('Frequency (Hz)')
plt.title('Spectrum')


