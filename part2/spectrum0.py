from ctypes import *
import numpy as np
import matplotlib.pyplot as plt
import os
from part2 import bandwidth
import seaborn
import pandas
from pandas import DataFrame
import datetime
import time
import pymysql as mdb
from part2 import occupie

# 一次细扫，扫每一个方框的信号；输入参数：起始频率、终止频率、任务名称，方框编号，计数、细扫的时间
def spectrum0(startFreq, stopFreq, str_time, k, count, str_tt1, str_tt2):
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
    cf = c_double((startFreq + stopFreq) / 2)
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
    span = c_double(stopFreq - startFreq)
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
    plt.title('Spectrum-%s'%k)
    plt.show()
    band = bandwidth.bandwidth(peakPower, peakPowerFreq, trace, freq)  # 带宽
    # 存储细扫描数据
    # 将时间改成合法文件名形式
    path = "E:\data111\\" + str_tt2 + "spectrum%d.csv"%k
    df0 = DataFrame({
        'datetime': str_tt1,
        'frequency': freq,
        'power': trace
    })
    df0.to_csv(
        path,
        index=False
    )
    '''
    需要将return的基本数据存在数据库中
    '''
    # 获取业务类型写入表中
    # 需要连接对方数据库
    #con1 = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    #sql = "select ObjectID from RFBT_Allocation where Spectrum_Start <= %f and Spectrum_Stop >= %f" % (peakPowerFreq,peakPowerFreq)
    #objectId = pandas.read_sql(sql,con1)  # 获取信号业务类型的种类编号

    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    with con:
        # 获取连接的cursor，只有获取了cursor，我们才能进行各种操作
        cur = con.cursor()
        cur.execute("INSERT INTO SPECTRUM_IDENTIFIED VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", [str_time, int(k), str_tt1, float(startFreq), float(stopFreq),float(peakPowerFreq),float(band), int(count)])
        cur.close()
    con.commit()
    con.close()
    return band, peakPower, peakPowerFreq
# 返回某一方框信号的带宽，中心频率，中心频率峰值
