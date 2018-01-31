# 进行无人机的频谱监测
import os
from ctypes import *
import numpy as np
import matplotlib.pyplot as plt
from part2 import bandwidth
import pandas
import datetime
from pandas import DataFrame
# 绘制实时的无人机频谱图，顺便计算出带宽
def uav0():
    # create Spectrum_Settings data structure
    os.chdir("E:/项目/洪（私）/pro/RSA_API/lib/x64")
    rsa300 = WinDLL("RSA_API.dll")

    class Spectrum_Settings(Structure):
        _fields_ = [('span', c_double),
                    ('rbw', c_double),
                    ('enableVBW', c_bool),
                    ('vbw', c_double),
                    ('traceLength', c_int),
                    ('window', c_int),
                    ('verticalUnit', c_int),
                    ('actualStartFreq', c_double),
                    ('actualStopFreq', c_double),
                    ('actualFreqStepSize', c_double),
                    ('actualRBW', c_double),
                    ('actualVBW', c_double),
                    ('actualNumIQSamples', c_double)]

    # initialize variables
    specSet = Spectrum_Settings()
    longArray = c_long * 10
    deviceIDs = longArray()
    deviceSerial = c_wchar_p('')
    numFound = c_int(0)
    enable = c_bool(True)  # spectrum enable
    # cf = c_double(9e8)            #center freq
    refLevel = c_double(0)  # ref level
    ready = c_bool(False)  # ready
    timeoutMsec = c_int(500)  # timeout
    trace = c_int(0)  # select Trace 1
    detector = c_int(1)  # set detector type to max
    # 由起始频率和终止频率直接可以得到中心频率
    # set cf
    startFreq = c_double(840.5e6)
    stopFreq = c_double(845e6)
    cf = c_double((startFreq.value + stopFreq.value) / 2)
    '''
    # search the USB 3.0 bus for an RSA306
    ret = rsa300.Search(deviceIDs, byref(deviceSerial), byref(numFound))
    if ret != 0:
        print('Error in Search: ' + str(ret))
    if numFound.value < 1:
        print('No instruments found. Exiting script.')
        exit()
    elif numFound.value == 1:
        print('One device found.')
        print('Device Serial Number: ' + deviceSerial.value)
    else:
        print('2 or more instruments found.')
        # note: the API can only currently access one at a time

    # connect to the first RSA306
    ret = rsa300.Connect(deviceIDs[0])
    if ret != 0:
        print('Error in Connect: ' + str(ret))
'''
    # preset the RSA306 and configure spectrum settings
    rsa300.Preset()
    rsa300.SetCenterFreq(cf)
    rsa300.SetReferenceLevel(refLevel)
    rsa300.SPECTRUM_SetEnable(enable)
    rsa300.SPECTRUM_SetDefault()
    rsa300.SPECTRUM_GetSettings(byref(specSet))

    # configure desired spectrum settings
    # some fields are left blank because the default
    # values set by SPECTRUM_SetDefault() are acceptable
    span = c_double(stopFreq.value - startFreq.value)
    specSet.span = span
    specSet.rbw = c_double(300e3)
    # specSet.enableVBW =
    # specSet.vbw =
    specSet.traceLength = c_int(801)  # c_int(int(span.value/step_size.value))#c_int(801)
    # specSet.window =
    # specSet.verticalUnit =
    specSet.actualStartFreq = startFreq
    specSet.actualStopFreq = stopFreq
    specSet.actualFreqStepSize = c_double(
        span.value / 801)  # step_size c_double(span.value/801)   # c_double(50000.0)
    # specSet.actualRBW =
    # specSet.actualVBW =
    # specSet.actualNumIQSamples =

    # set desired spectrum settings
    rsa300.SPECTRUM_SetSettings(specSet)
    rsa300.SPECTRUM_GetSettings(byref(specSet))

    # uncomment this if you want to print out the spectrum settings

    # print out spectrum settings for a sanity check
    # print('Span: ' + str(specSet.span))
    # print('RBW: ' + str(specSet.rbw))
    # print('VBW Enabled: ' + str(specSet.enableVBW))
    # print('VBW: ' + str(specSet.vbw))
    # print('Trace Length: ' + str(specSet.traceLength))
    # print('Window: ' + str(specSet.window))
    # print('Vertical Unit: ' + str(specSet.verticalUnit))
    # print('Actual Start Freq: ' + str(specSet.actualStartFreq))
    # print('Actual End Freq: ' + str(specSet.actualStopFreq))
    # print('Actual Freq Step Size: ' + str(specSet.actualFreqStepSize))
    # print('Actual RBW: ' + str(specSet.actualRBW))
    # print('Actual VBW: ' + str(specSet.actualVBW))

    # initialize variables for GetTrace
    traceArray = c_float * specSet.traceLength
    traceData = traceArray()
    outTracePoints = c_int()

    # generate frequency array for plotting the spectrum
    freq = np.arange(specSet.actualStartFreq,
                     specSet.actualStartFreq + specSet.actualFreqStepSize * specSet.traceLength,
                     specSet.actualFreqStepSize)

    # start acquisition
    rsa300.Run()
    while ready.value == False:
        rsa300.SPECTRUM_WaitForDataReady(timeoutMsec, byref(ready))

    rsa300.SPECTRUM_GetTrace(c_int(0), specSet.traceLength,
                             byref(traceData), byref(outTracePoints))
    # print('Got trace data.')

    # convert trace data from a ctypes array to a numpy array
    trace = np.ctypeslib.as_array(traceData)

    # Peak power and frequency calculations
    peakPower = np.amax(trace)
    peakPowerFreq = freq[np.argmax(trace)]
    # print('Peak power in spectrum: %4.3f dBm @ %d Hz' % (peakPower, peakPowerFreq))

    # plot the spectrum trace (optional)
    plt.plot(freq, traceData)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (dBm)')
    plt.title('uav-Spectrum')
    plt.show()
    # 显示无人机实时监测出来的信号频谱中心频点等
    band = bandwidth.bandwidth(peakPower, peakPowerFreq, trace, freq)
    print(peakPower, peakPowerFreq, band)
    return peakPowerFreq, band, peakPower

# 无人机IQ数据
def uav1():
    os.chdir("E:/项目/洪（私）/pro\RSA_API/lib/x64")
    rsa300 = WinDLL("RSA_API.dll")

    class IQHeader(Structure):
        _fields_ = [('acqDataStatus', c_uint16),
                    ('acquisitionTimestamp', c_uint64),
                    ('frameID', c_uint32), ('trigger1Index', c_uint16),
                    ('trigger2Index', c_uint16), ('timeSyncIndex', c_uint16)]

    # initialize/assign variables
    longArray = c_long * 10
    deviceIDs = longArray()
    deviceSerial = c_wchar_p('')
    numFound = c_int(0)
    serialNum = c_char_p(b'')
    nomenclature = c_char_p(b'')
    header = IQHeader()

    refLevel = c_double(0)
    cf = c_double(0.843e9)
    iqBandwidth = c_double(2.5e6)
    recordLength = c_long(1024)
    mode = c_int(0)
    level = c_double(-10)
    iqSampleRate = c_double(0)
    runMode = c_int(0)
    timeoutMsec = c_int(1000)
    ready = c_bool(False)

    # initialize
    rsa300.GetDeviceSerialNumber(serialNum)
    print('Serial Number: ' + str(serialNum.value))
    rsa300.GetDeviceNomenclature(nomenclature)
    print('Device Nomenclature: ' + str(nomenclature.value))

    # configure instrument
    rsa300.Preset()
    rsa300.SetReferenceLevel(refLevel)
    rsa300.SetCenterFreq(cf)
    rsa300.SetIQBandwidth(iqBandwidth)
    rsa300.SetIQRecordLength(recordLength)
    rsa300.SetTriggerMode(mode)
    rsa300.SetIFPowerTriggerLevel(level)

    # begin acquisition
    rsa300.Run()

    # get relevant settings values
    rsa300.GetReferenceLevel(byref(refLevel))
    rsa300.GetCenterFreq(byref(cf))
    rsa300.GetIQBandwidth(byref(iqBandwidth))
    rsa300.GetIQRecordLength(byref(recordLength))
    rsa300.GetTriggerMode(byref(mode))
    rsa300.GetIFPowerTriggerLevel(byref(level))
    rsa300.GetRunState(byref(runMode))
    rsa300.GetIQSampleRate(byref(iqSampleRate))

    # for kicks and giggles
    # print('Run Mode:' + str(runMode.value))
    # print('Reference level: ' + str(refLevel.value) + 'dBm')
    # print('Center frequency: ' + str(cf.value) + 'Hz')
    # print('Bandwidth: ' + str(iqBandwidth.value) + 'Hz')
    # print('Record length: ' + str(recordLength.value))
    # print('Trigger mode: ' + str(mode.value))
    # print('Trigger level: ' + str(level.value) + 'dBm')
    # print('Sample rate: ' + str(iqSampleRate.value) + 'Samples/sec')

    # check for data ready
    while ready.value == False:
        ret = rsa300.WaitForIQDataReady(timeoutMsec, byref(ready))
    # print('IQ Data is Ready')

    # as a bonus, get the IQ header even though it's not used
    ret = rsa300.GetIQHeader(byref(header))
    if ret != 0:
        print('Error in GetIQHeader: ' + str(ret))
    # print('Got IQ Header')

    # initialize data transfer variables
    iqArray = c_float * recordLength.value
    iData = iqArray()
    qData = iqArray()
    startIndex = c_int(0)

    # query I and Q data
    rsa300.GetIQDataDeinterleaved(byref(iData), byref(qData), startIndex, recordLength)
    # print('Got IQ data')

    # convert ctypes array to numpy array for ease of use
    I = np.ctypeslib.as_array(iData)
    Q = np.ctypeslib.as_array(qData)

    # create time array for plotting
    time = np.linspace(0, recordLength.value / iqSampleRate.value, recordLength.value)
    '''
    plt.figure(1)
    plt.subplot(2, 1, 1)
    plt.title('I and Q vs Time')
    plt.plot(time, I)
    plt.ylabel('I (V)')
    plt.subplot(2, 1, 2)
    plt.plot(time, Q)
    plt.ylabel('Q (V)')
    plt.xlabel('Time (sec)')
    plt.show()
    '''
    str_time = str(datetime.datetime.now().strftime('%F-%H-%M-%S'))
    df1 = DataFrame({
        'datetime': str_time,
        'I': I,
        'Q': Q
    })
    return df1

# 仅仅绘制频谱图像
def uav00():
    # create Spectrum_Settings data structure
    os.chdir("E:/项目/洪（私）/pro/RSA_API/lib/x64")
    rsa300 = WinDLL("RSA_API.dll")

    class Spectrum_Settings(Structure):
        _fields_ = [('span', c_double),
                    ('rbw', c_double),
                    ('enableVBW', c_bool),
                    ('vbw', c_double),
                    ('traceLength', c_int),
                    ('window', c_int),
                    ('verticalUnit', c_int),
                    ('actualStartFreq', c_double),
                    ('actualStopFreq', c_double),
                    ('actualFreqStepSize', c_double),
                    ('actualRBW', c_double),
                    ('actualVBW', c_double),
                    ('actualNumIQSamples', c_double)]

    # initialize variables
    specSet = Spectrum_Settings()
    longArray = c_long * 10
    deviceIDs = longArray()
    deviceSerial = c_wchar_p('')
    numFound = c_int(0)
    enable = c_bool(True)  # spectrum enable
    # cf = c_double(9e8)            #center freq
    refLevel = c_double(0)  # ref level
    ready = c_bool(False)  # ready
    timeoutMsec = c_int(500)  # timeout
    trace = c_int(0)  # select Trace 1
    detector = c_int(1)  # set detector type to max
    # 由起始频率和终止频率直接可以得到中心频率
    # set cf
    startFreq = c_double(840.5e6)
    stopFreq = c_double(845e6)
    cf = c_double((startFreq.value + stopFreq.value) / 2)
    '''
    # search the USB 3.0 bus for an RSA306
    ret = rsa300.Search(deviceIDs, byref(deviceSerial), byref(numFound))
    if ret != 0:
        print('Error in Search: ' + str(ret))
    if numFound.value < 1:
        print('No instruments found. Exiting script.')
        exit()
    elif numFound.value == 1:
        print('One device found.')
        print('Device Serial Number: ' + deviceSerial.value)
    else:
        print('2 or more instruments found.')
        # note: the API can only currently access one at a time

    # connect to the first RSA306
    ret = rsa300.Connect(deviceIDs[0])
    if ret != 0:
        print('Error in Connect: ' + str(ret))
'''
    # preset the RSA306 and configure spectrum settings
    rsa300.Preset()
    rsa300.SetCenterFreq(cf)
    rsa300.SetReferenceLevel(refLevel)
    rsa300.SPECTRUM_SetEnable(enable)
    rsa300.SPECTRUM_SetDefault()
    rsa300.SPECTRUM_GetSettings(byref(specSet))

    # configure desired spectrum settings
    # some fields are left blank because the default
    # values set by SPECTRUM_SetDefault() are acceptable
    span = c_double(stopFreq.value - startFreq.value)
    specSet.span = span
    specSet.rbw = c_double(300e3)
    # specSet.enableVBW =
    # specSet.vbw =
    specSet.traceLength = c_int(801)  # c_int(int(span.value/step_size.value))#c_int(801)
    # specSet.window =
    # specSet.verticalUnit =
    specSet.actualStartFreq = startFreq
    specSet.actualStopFreq = stopFreq
    specSet.actualFreqStepSize = c_double(
        span.value / 801)  # step_size c_double(span.value/801)   # c_double(50000.0)
    # specSet.actualRBW =
    # specSet.actualVBW =
    # specSet.actualNumIQSamples =

    # set desired spectrum settings
    rsa300.SPECTRUM_SetSettings(specSet)
    rsa300.SPECTRUM_GetSettings(byref(specSet))

    # uncomment this if you want to print out the spectrum settings

    # print out spectrum settings for a sanity check
    # print('Span: ' + str(specSet.span))
    # print('RBW: ' + str(specSet.rbw))
    # print('VBW Enabled: ' + str(specSet.enableVBW))
    # print('VBW: ' + str(specSet.vbw))
    # print('Trace Length: ' + str(specSet.traceLength))
    # print('Window: ' + str(specSet.window))
    # print('Vertical Unit: ' + str(specSet.verticalUnit))
    # print('Actual Start Freq: ' + str(specSet.actualStartFreq))
    # print('Actual End Freq: ' + str(specSet.actualStopFreq))
    # print('Actual Freq Step Size: ' + str(specSet.actualFreqStepSize))
    # print('Actual RBW: ' + str(specSet.actualRBW))
    # print('Actual VBW: ' + str(specSet.actualVBW))

    # initialize variables for GetTrace
    traceArray = c_float * specSet.traceLength
    traceData = traceArray()
    outTracePoints = c_int()

    # generate frequency array for plotting the spectrum
    freq = np.arange(specSet.actualStartFreq,
                     specSet.actualStartFreq + specSet.actualFreqStepSize * specSet.traceLength,
                     specSet.actualFreqStepSize)

    # start acquisition
    rsa300.Run()
    while ready.value == False:
        rsa300.SPECTRUM_WaitForDataReady(timeoutMsec, byref(ready))

    rsa300.SPECTRUM_GetTrace(c_int(0), specSet.traceLength,
                             byref(traceData), byref(outTracePoints))
    # print('Got trace data.')

    # convert trace data from a ctypes array to a numpy array
    trace = np.ctypeslib.as_array(traceData)

    # Peak power and frequency calculations
    peakPower = np.amax(trace)
    peakPowerFreq = freq[np.argmax(trace)]
    # print('Peak power in spectrum: %4.3f dBm @ %d Hz' % (peakPower, peakPowerFreq))

    # plot the spectrum trace (optional)
    plt.plot(freq, traceData)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (dBm)')
    plt.title('uav-Spectrum')
    plt.show()

