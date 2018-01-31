# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 10:06:05 2017

@author: Administrator
"""

"""
Peak Power Detect using API for RSA306
Author: Morgan Allison
Date created: 6/24/15
Date edited: 11/18/15
Windows 7 64-bit
Python 2.7.9 64-bit (Anaconda 3.7.0)
NumPy 1.8.1, MatPlotLib 1.3.1
To get Anaconda: http://continuum.io/downloads
Anaconda includes NumPy and MatPlotLib
"""
# 一次扫频
import pymysql as mdb
from ctypes import *
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn
import pandas
from pandas import DataFrame
#from part2 import detectNoise
#average = detectNoise.detectNoise()
from part2 import spectrum0
import datetime
from part2 import bandwidth
# 开始扫频
"""
################################################################
C:\Tektronix\RSA306 API\lib\x64 needs to be added to the
PATH system environment variable
################################################################
"""


'''
os.chdir("E:/项目/洪（私）/pro/RSA_API/lib/x64")
rsa300 = WinDLL("RSA_API.dll")
# 获取并设置设置起始频率和终止频率
startFreq = c_double(float(input()))
stopFreq = c_double(float(input()))
# set span
span = c_double(float(input()))
# 设置rbw
rbw = c_double(float(input()))
'''
# 一次扫频参数：噪声均值、起始频率、终止频率、频率跨度、rbw、任务名、计数、某一次扫频的具体时间
def spectrum(average, startFreq, stopFreq, span, rbw, str_time, count, str_tt1, str_tt2):
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
    specSet.span = span
    specSet.rbw = rbw
    # specSet.enableVBW =
    # specSet.vbw =
    specSet.traceLength = c_int(801)#c_int(int(span.value/step_size.value))#c_int(801)
    # specSet.window =
    # specSet.verticalUnit =
    specSet.actualStartFreq = startFreq
    specSet.actualStopFreq = stopFreq
    specSet.actualFreqStepSize = c_double(span.value/801)#step_size c_double(span.value/801)   # c_double(50000.0)
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
    print('Got trace data.')

    # convert trace data from a ctypes array to a numpy array
    trace = np.ctypeslib.as_array(traceData)

    # Peak power and frequency calculations
    peakPower = np.amax(trace)
    peakPowerFreq = freq[np.argmax(trace)]
    print('Peak power in spectrum: %4.3f dBm @ %d Hz' % (peakPower, peakPowerFreq))

    # plot the spectrum trace (optional)
    plt.plot(freq, traceData)
    # 绘制方框
    a = []
    b = []  # 存储频率
    c = []
    d = []  # 存储电平
    # 得到局部数据
    for i in range(801):
        if traceData[i] > average + 6:
            a.append(freq[i])
            c.append(trace[i])
        else:
            b.append(a)
            d.append(c)
            a = []
            c = []

    # 获取局部框架的数量,用来绘制局部的子图
    rest_freq = []
    rest_power = []
    for i in range(len(b)):
        if len(b[i]) != 0:
            rest_freq.append(b[i])
            rest_power.append(d[i])

    j1 = 0
    for i in range(len(b)):
        # 跳过空数据
        if len(b[i]) > 0:
            j1 += 1
            s1_x = b[i][0]
            s1_y = average + 6
            s2_x = b[i][-1]
            s2_y = average + 6
            # s3_x = b[i][0]
            s3_y = np.amax(d[i])
            # s4_x = b[i][-1]
            # s4_y = np.amax(b[i])
            # 画出四条线
            plt.plot([s1_x, s1_x], [s1_y, s3_y])
            plt.plot([s1_x, s2_x], [s3_y, s3_y])
            plt.plot([s2_x, s2_x], [s3_y, s1_y])
            plt.plot([s1_x, s2_x], [s1_y, s2_y])
            plt.text((b[i][0]+b[i][-1])/2,s3_y,'%s'%j1)

    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (dBm)')
    plt.title('Spectrum')

    # BONUS clean up plot axes
    xmin = np.amin(freq)
    xmax = np.amax(freq)
    plt.xlim(xmin, xmax)
    ymin = np.amin(trace) - 10
    ymax = np.amax(trace) + 10

    plt.show()
    # 分别绘制局部的子图
    j = 0
    for i in range(len(b)):
        if len(b[i]) > 0:
            j += 1
            b_f = float(b[i][0])
            e_f = float(b[i][-1])
            band_t, peak_t, peak_tf = spectrum0.spectrum0(b_f, e_f, str_time, j, count, str_tt1, str_tt2)
            ''' plt.plot(b[i], d[i])
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Amplitude (dBm)')
            plt.title('Spectrum')
            plt.show()
            '''
            # 输出监测到的信号的真实信号带宽，中心频率，峰值信息
            print(band_t, peak_t, peak_tf)
    # 后台自动保存这一次扫频频谱数据
    df1 = DataFrame({
        'datetime':str_tt1,
        'frequency': freq,
        'power': trace
    })


    # print('Disconnecting.')
    # rsa300.Disconnect()
    return df1, rest_freq, rest_power
# 返回原始的频谱数据











