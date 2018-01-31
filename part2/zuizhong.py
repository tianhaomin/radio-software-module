from ctypes import *
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn
import pandas
from pandas import DataFrame
import datetime
import time
import pymysql as mdb
from decimal import Decimal

from scipy.interpolate import spline
def connect():
    os.chdir("E:/项目/洪（私）/pro\RSA_API/lib/x64")
    rsa = cdll.LoadLibrary("RSA_API.dll")
    numFound = c_int(0)
    intArray = c_int * 10
    deviceIDs = intArray()
    deviceSerial = create_string_buffer(8)
    deviceType = create_string_buffer(8)
    rsa.DEVICE_Search(byref(numFound), deviceIDs, deviceSerial, deviceType)
    if numFound.value < 1:
        print('No instruments found . Exiting script.')
        exit()
    elif numFound.value == 1:
        print('One device found.')
        print('Device type:{}'.format(deviceSerial.value))
        rsa.DEVICE_Connect(deviceIDs[0])
        print('The device has connected')
    else:
        print('Unexpected number of devices found, exiting script.')
        exit()
    # return deviceSerial.value
def diconncet():
    os.chdir("E:/项目/洪（私）/pro/RSA_API/lib/x64")
    rsa300 = WinDLL("RSA_API.dll")
    print('Disconnecting.')
    rsa300.Disconnect()
def bandwidth(peakPower,peakFreq,trace,freq):
    peak_index1 = np.argmax(trace)
    peak_index2 = np.argmax(trace)
    a1 = 0
    a2 = len(trace) - 1
    while peak_index1>0:
        if trace[peak_index1]>peakPower-3:
            pass
        else:
            a1 = peak_index1
            break
        peak_index1 -= 1
    while peak_index2<len(trace):
        if trace[peak_index2]>peakPower-3:
            pass
        else:
            a2 = peak_index2
            break
        peak_index2 += 1
    bandWidth = freq[a2] - freq[a1]
    freq_cf = freq[a1]+bandWidth/2
    return bandWidth,freq_cf
# 噪声监测
def detectNoise():
   os.chdir("E:/项目/洪（私）/pro/RSA_API/lib/x64")
   rsa300 = WinDLL("RSA_API.dll")

   # create Spectrum_Settings data structure
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
   cf = c_double(20e6)  # center freq
   refLevel = c_double(0)  # ref level
   ready = c_bool(False)  # ready
   timeoutMsec = c_int(500)  # timeout
   trace = c_int(0)  # select Trace 1
   detector = c_int(1)  # set detector type to max

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
   specSet.span = c_double(40e6)
   specSet.rbw = c_double(300e3)
   specSet.enableVBW = c_bool(True)
   specSet.vbw = c_double(100)
   specSet.traceLength = c_int(801)
   # specSet.window =
   # specSet.verticalUnit =
   specSet.actualStartFreq = c_double(0)
   specSet.actualStopFreq = c_double(40e6)
   specSet.detector = detector
   # specSet.actualFreqStepSize =c_double(50000.0)
   # specSet.actualRBW =
   specSet.actualVBW = c_double(100)
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
   average = sum(trace) / len(trace)
   # print('Disconnecting.')
   # rsa300.Disconnect()
   print(average)
   return average
# 一次细扫，扫每一个方框的信号；输入参数：起始频率、终止频率、任务名称，方框编号，计数、细扫的时间
def spectrum0(startFreq, stopFreq, str_time, k, count, str_tt1, str_tt2, vbw, longitude, latitude):
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
    detector = c_int(0)  # set detector type to max
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
    specSet.enableVBW = c_bool(True)
    specSet.vbw = c_double(vbw)
    specSet.traceLength = c_int(801)  # c_int(int(span.value/step_size.value))#c_int(801)
    # specSet.window =
    # specSet.verticalUnit =
    specSet.detector = detector
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
    band, freq_cf = bandwidth(peakPower, peakPowerFreq, trace, freq)  # 带宽
    # 存储细扫描数据
    # 将时间改成合法文件名形式
    path = "E:\\spec\\%s\\" % str_time + "capture\\"+str_tt2 + "spectrum%d.csv" % k  # 频谱数据粗扫描数据存储路径，细扫数据又增加了一层结构
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
    ############改动1#############
    sql1 = "select SERVICEDID from  RMBT_SERVICE_FREQDETAIL where STARTFREQ <= %s and ENDFREQ >= %s" % (float(startFreq),float(stopFreq))
    con1 = mdb.connect('localhost', 'root', '17704882970', '110000_rmdsd')
    c = pandas.read_sql(sql1,con1)
    if len(c) > 0:
        sevice_name = c['Spectrum_Service_Name'][0]
    con2 = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    with con2:
        # 获取连接的cursor，只有获取了cursor，我们才能进行各种操作
        cur = con2.cursor()
        cur.execute("INSERT INTO SPECTRUM_IDENTIFIED VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [str_time, sevice_name, str_tt1, float(startFreq), float(stopFreq),float(freq_cf),float(band), int(count), float(longitude), float(latitude)])
        cur.close()
    con1.commit()
    con1.close()
    return band, freq_cf, peakPowerFreq
# 返回某一方框信号的带宽，中心频率，中心频率峰值
# 一次扫频参数：噪声均值、起始频率、终止频率、频率跨度、rbw、任务名、计数、某一次扫频的具体时间
def spectrum1(average, startFreq, stopFreq, span, rbw, str_time, count, str_tt1, str_tt2, vbw, longitude, latitude):
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
    detector = c_int(0)  # set detector type to max
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
    specSet.enableVBW = c_bool(True)
    specSet.vbw = c_double(vbw)
    specSet.traceLength = c_int(801)#c_int(int(span.value/step_size.value))#c_int(801)
    # specSet.window =
    # specSet.verticalUnit =
    specSet.actualStartFreq = startFreq
    specSet.actualStopFreq = stopFreq
    specSet.actualFreqStepSize = c_double(span.value/801)#step_size c_double(span.value/801)   # c_double(50000.0)
    # specSet.actualRBW =
    # specSet.actualVBW =
    # specSet.actualNumIQSamples =
    # 设置检波方式为正峰检波
    specSet.detector = detector
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
            ########################加一个查询的代码进行信号类型的查询###############
            band_t, peak_t, peak_tf = spectrum0(b_f, e_f, str_time, j, count, str_tt1, str_tt2, vbw, longitude, latitude)
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
# 频谱监测（总）
# 输入参数是监测设备信息，天线信息，起始频率，终止频率，频率跨度，rbw，持续时间
def spectrum2(deviceSerial, anteid, startFreq, stopFreq, span, rbw, t, vbw,mfid, statismode, serviceid, address):
    os.chdir("E:/项目/洪（私）/pro/RSA_API/lib/x64")
    rsa300 = WinDLL("RSA_API.dll")
    # 进行连接获得检测设备信息
    # print (average)
    # 参数设置
    ##################################
    #经纬度接口
    longitude = float(116.41)
    latitude = float(39.85)
    ##################################
    # 获取并设置设置起始频率和终止频率
    startFreq = c_double(float(startFreq))
    stopFreq = c_double(float(stopFreq))
    # set span
    span = c_double(float(span))
    # 设置rbw
    rbw = c_double(float(rbw))
    # 从别的数据库读取出所选用的天线类型
    # 设置step_size
    # step_size = c_double(float(input()))
    t = float(t)  # 持续时间
    time_ref = time.time()
    # 本次扫描的全部数据存储
    trace = DataFrame({})
    restf = []
    restp = []
    count = 0
    '''
    参数配置完之后就可以开始进行数据库的创建，之后具体信号的检测得到的数据在
    之后的程序中写入表中即可
    '''
    # 先建立主表即测试任务，起始时间，持续时间
    str_time = str(datetime.datetime.now().strftime('%F-%H-%M-%S'))  # 整个测试的起始的准确时间用于存储原始文件路径的因为路径中不能有：
    start_time = str(datetime.datetime.now().strftime('%F %H:%M:%S')) # 总表的起始时间
    os.mkdir("E:\\spec\\%s\\" % str_time)
    os.mkdir("E:\\spec\\%s\\"%str_time+"capture\\")  # 新添加了一级目录粗细分开放比较清晰，相应的spectrum0中细扫数据存储的位置也需要改变
    while time.time() - time_ref < t:
        average = detectNoise()
        count += 1
        str_tt1 = str(datetime.datetime.now().strftime('%F %H:%M:%S'))  # 内部扫频的时刻
        str_tt2 = str(datetime.datetime.now().strftime('%F-%H-%M-%S'))  # 作为内部细扫的文件名
        z1, z2, z3, = spectrum1(average, startFreq, stopFreq, span, rbw, str_time, count, str_tt1, str_tt2, vbw, longitude, latitude)
        trace = pandas.concat([trace, z1])
        restf.append(z2)
        restp.append(z3)
        # 主检测页面显示无人机频谱监测
        uav00(rsa300, vbw)

    # 获取测试时间,保存原始频谱数据
    # os.mkdir("E:\\%s\\"%str_time)
    path = "E:\\spec\\%s\\" %str_time+ str_time + "spectrum%ds.csv" % t  # 频谱数据粗扫描数据存储路径
    trace.to_csv(
        path,
        index=False
    )
    str_time1 = str(datetime.datetime.now().strftime('%F %H:%M:%S'))  # 结束的准确时间，直接传到数据库中自动转化成datetime格式
    s_c = spectrum_occ(start_time, str_time1, str_time, startFreq.value, stopFreq.value)
    print(s_c)
    # 数据库构建
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    with con:
        # 获取连接的cursor，只有获取了cursor，我们才能进行各种操作
        cur = con.cursor()  # 一条游标操作就是一条数据插入，第二条游标操作就是第二条记录，所以最好一次性插入或者日后更新也行
        cur.execute("INSERT INTO Minitor_Task VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[str_time, start_time, str_time1, float(t), float(s_c), path, deviceSerial, anteid, count, float(startFreq.value), float(stopFreq.value),float(longitude),float(latitude)])
        cur.close()
    con.commit()
    con.close()
    rmbt_facility_freqband_emenv( str_time,mfid, statismode, serviceid, address,threshold=0, occ1=0,occ2=0, occ3=0, hieght=0)
###################################################################################################################################
# 用DPX实现MAXHOLD无人机检测
##############################################################################################
# 绘制实时的无人机频谱图，顺便计算出带宽，无人机页面调用，调用关系不用改
def uav0(rsa300, vbw):
    # create Spectrum_Settings data structure

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
    detector = c_int(0)  # set detector type to max
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
    specSet.enableVBW = c_bool(True)
    specSet.vbw = c_double(vbw)
    specSet.traceLength = c_int(801)  # c_int(int(span.value/step_size.value))#c_int(801)
    # specSet.window =
    # specSet.verticalUnit =
    specSet.detector = detector
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

    # 绘制无人机频谱检测maxhold频谱图
    # plot the spectrum trace (optional)
    #plt.plot(freq, traceData)
    #plt.xlabel('Frequency (Hz)')
    #plt.ylabel('Amplitude (dBm)')
    #plt.title('uav-Spectrum')
    #plt.show()
    # 显示无人机实时监测出来的信号频谱中心频点等
    band ,freq_cf= bandwidth(peakPower, peakPowerFreq, trace, freq)
    #print(peakPower, peakPowerFreq, band)
    #dpx_example(rsa300)


    return freq_cf, band, peakPower, freq, traceData
# 无人机IQ数据
def uav1(rsa300,freq_cf,band):
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
    cf = c_double(freq_cf)
    iqBandwidth = c_double(band)
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
# 仅仅绘制频谱图像,频谱检测右下角的小图调用
def uav00(rsa300, vbw):
    # create Spectrum_Settings data structure

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
    detector = c_int(0)  # set detector type to max
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
    specSet.detector = detector
    specSet.rbw = c_double(300e3)
    specSet.enableVBW = c_bool(True)
    specSet.vbw = c_double(vbw)
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
# 监测无人机信号，单独服务于无人机界面调用uav0和uav1
def uav(t_r, test_No, deviceSerial, anteid, vbw):  # 参数是持续时间、测试编号、监测设备信息、天线信息
    #deviceSerial = connect.connect()  # 随设备进行连接然后获取设备信息
    os.chdir("E:/项目/洪（私）/pro/RSA_API/lib/x64")
    rsa = WinDLL("RSA_API.dll")
    longitude = float(116.41)
    latitude = float(39.85)
    trace_IQ = DataFrame({})
    #count = 0
    average = detectNoise()
    # a = []  # 存储无人机出现的时间段
    b = []  # 存储无人机信号出现的带宽
    c = []  # 存储无人机信号出现的中心频点
    str_time = str(datetime.datetime.now().strftime('%F-%H-%M-%S'))  # 无人机检测起始时间
    os.mkdir("E:\\IQ\\%s\\" % str_time)
    t_ref = time.time()
    time_list = []
    time1 = 1
    while time.time() - t_ref < t_r:
       time1 = time1+1
       x_y = {}
       x_y[time1] = 0
       time_list.append(time1)
       freq_cf, band, peak, x, y = uav0(rsa, vbw)
       fig = plt.figure()
       ax1 = fig.add_subplot(211)
       ax1.plot(x,y)
       ax1.set_xlabel('frequency(Hz)')
       ax1.set_ylabel("Volts(db)")
       #ax2.plot(x,y)
       #plt.show()
       ax2 = fig.add_subplot(212)
       if peak > average + 6 :
           #count = 1
           b.append(band)
           c.append(freq_cf)
           x_y[time1] = [freq_cf-band/2,freq_cf+band/2]
           #ax2 = fig.add_subplot(212)
           #ax2.plot(x, y)
           #ax2.plot([freq_cf-band/2,freq_cf+band/2],[l,l])
           #plt.hold(True)
           #plt.show()
       #elif peak > average + 6 and count == 1:
           #pass
       if len(x_y) > 20:
           del x_y[time1-20]
       ax2 = fig.add_subplot(212)
       for x_i in x_y:
           if x_y[x_i] == 0:
               pass
           else:
               ax2.plot(x_y[x_i],[x_i,x_i])
       plt.show()
       #else:
           #t2 = time.time()
           #count = 0
           # a.append(t2-t1)
       df1 = uav1(rsa,freq_cf,band)
       trace_IQ = pandas.concat([trace_IQ, df1])
    path = "E:\\IQ\\%s\\" % str_time + str_time + "IQ%s.csv" % t_r  # IQ数据存储路径
    trace_IQ.to_csv(
        path,
        index=False
    )
   # if a==[]:
    #    a.append(t_r)

    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    with con:
        # 操作数据库需要一次性的进行，一条代码就是写入一行所以一次就把表的一行全部写入
        cur = con.cursor()
        cur.execute("INSERT INTO uav VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [int(test_No), str_time, str_time, float(c[0]-b[0]/2), float(c[0] + b[0] / 2), float(b[0]), path, deviceSerial, anteid, float(longitude), float(latitude)])
        cur.close()
    con.commit()
    con.close()
    #return a,b,c
    return b,c
# 计算信道占用度
# 参数：起始时间、终止时间、任务名称、其实频率、终止频率
def channel_occ(start_time,stop_time,task_name,freq_start,freq_stop):
    # 输入就是起始时间、终止时间、任务名称、起始频率、终止频率
    step = float(freq_stop - freq_start) / 10
    sql2 = "select COUNT Task_L from minitor_task where Task_Name='%s'" % (task_name)
    # sql2 = "select count1 from SPECTRUM_IDENTIFIED where Task_Name='%s'" % (task_name) + "&& Start_time between DATE_FORMAT('%s'," % (start_time) + "'%Y-%m-%d %H:%i:%S')" + "and DATE_FORMAT('%s'," % (stop_time) + "'%Y-%m-%d %H:%i:%S')"
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    b = pandas.read_sql(sql2, con)
    channel_occupied = []
    retain_time = float(b['Task_L'])
    l = (stop_time - start_time).seconds
    roid = l/retain_time
    for i in range(10):
        start_f = freq_start + i * step
        stop_f = freq_start + (i + 1) * step
        sql1 = "select count1 from SPECTRUM_IDENTIFIED where Task_Name='%s' && FREQ_CF between %f and %f "%(task_name, float(start_f), float(stop_f))+"&& Start_time between DATE_FORMAT('%s',"%(start_time)+"'%Y-%m-%d %H:%i:%S')"+"and DATE_FORMAT('%s'," % (stop_time)+"'%Y-%m-%d %H:%i:%S')"
        a = pandas.read_sql(sql1, con)
        a = a.drop_duplicates()  # 去电重复项
        # print (a,b)
        channel_occupied1 = len(a) / float(b['COUNT']*roid)
        channel_occupied.append(channel_occupied1)
    # 绘制柱状图
    #print((channel_occupied))
    a1 = np.arange(freq_start, freq_stop, step)
    b1 = channel_occupied
    plt.bar(a1, b1,2)
    plt.xlabel("spectrum")
    plt.ylabel("occ(%)")
    plt.show()
# 计算频谱占用度必须用到原始格式的数据库
# 参数：起始时间、终止时间、任务名称、其实频率、终止频率
def spectrum_occ(start_time,stop_time,task_name,freq_start,freq_stop):
    # 输入就是起始时间、终止时间、任务名称、起始频率、终止频率
    spectrum_span = freq_stop - freq_start
    # 以一个小时为单位
    sql3 = "select FreQ_BW, COUNT1 from SPECTRUM_IDENTIFIED where Task_Name='%s' && FREQ_CF between %f and %f" % (task_name, float(freq_start), float(freq_stop)) + "&& Start_time between DATE_FORMAT('%s'," % (start_time) + "'%Y-%m-%d %H:%i:%S')" + "and DATE_FORMAT('%s'," % (stop_time) + "'%Y-%m-%d %H:%i:%S')"
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    c = pandas.read_sql(sql3, con)
    con.commit()
    con.close()
    spectrum_occ1 = sum(c['FreQ_BW'])
    if len(c['COUNT1'])>0:
        c1 = np.array(c['COUNT1'])
        num = max(c['COUNT1']) - min(c['COUNT1'])+1
        spectrum_occ = spectrum_occ1 / float(num * spectrum_span)
    else:
        spectrum_occ = 0
    return spectrum_occ  # 返回频谱占用度
# 绘制频谱占用度图像
# 参数：起始时间、终止时间、任务名称、其实频率、终止频率
def plot_spectrum_occ(start_time,stop_time,task_name,freq_start,freq_stop):
    starttime = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    stoptime = datetime.datetime.strptime(stop_time, "%Y-%m-%d %H:%M:%S")
    delta = int((stoptime - starttime).seconds/3600.0)
    print (delta)
    occ1 = []
    for i in range(delta):
        s_t = starttime + datetime.timedelta(hours = (i))
        e_t = starttime + datetime.timedelta(hours = (i+1))
        occ1_1 = spectrum_occ(s_t,e_t,task_name,freq_start,freq_stop)
        occ1.append(occ1_1)
    a = np.linspace(1,delta,delta)
    plt.plot(a,occ1)
    plt.xlabel("time")
    plt.ylabel("occ(%)")
    plt.title("spectrum occ%")
    plt.show()
# 获取时间和起始终止频率
def read_file(file):
    path = os.getcwd()+"\\date1\\"+file
    retain_time = 0
    for filename in os.listdir(path):
        if filename[-5] == 's':
            retain_time = int(filename[27:-5])
            break
    file1 = file[:10]+' '+file[11:13]+':'+file[14:16]+':'+file[17:19]
    start_time = datetime.datetime.strptime(file1, "%Y-%m-%d %H:%M:%S")
    end_time = start_time + datetime.timedelta(seconds=retain_time)
    sql = "select startFreq,endFreq from minitor_task where Task_Name=%s"%(file)
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    c = pandas.read_sql(sql, con)
    con.commit()
    con.close()
    start_freq = c['startFreq'][0]
    end_freq = c['endFreq'][0]
    return start_time,end_time,start_freq,end_freq
# 导入导出数据
# 粗扫描，返回某一次任务的初试频率和终止频率以及频率和功率矩阵,起始时间和终止时间
def importData_cu(task_name,file_name,raw_path):#task_name就是文件夹的名字，filename就是粗扫的csv文件名字，raw_path就是文件存储的路径
    sql = "select startFreq,endFreq,Task_B,Task_E from minitor_task where Task_Name='%s'"%(task_name)
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    c_cu = pandas.read_sql(sql, con)
    con.commit()
    con.close()
    start_freq_cu = c_cu['startFreq'][0]
    end_freq_cu = c_cu['endFreq'][0]
    start_time_cu = c_cu['Task_B'][0]
    end_time_cu=c_cu['Task_E'][0]
    path = raw_path+"//"+file_name+'.csv'
    df_cu = pandas.read_csv(path)
    num = int(len(df_cu)/801)
    x_mat = np.array(df_cu['frequency']).reshape(num,801)
    y_mat = np.array(df_cu['power']).reshape(num, 801)
    return start_freq_cu,end_freq_cu,x_mat,y_mat,start_time_cu,end_time_cu
# 细扫描，返回某一次细扫描的起始频率，终止频率，带宽，中心频率，频率数据，功率数据
def importData_xi(task_name,file_name,raw_path):
    start_time = file_name[:10]+' '+file_name[11:13]+':'+file_name[14:16]+':'+file_name[17:19]
    start_time=datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    numb = file_name[27:]
    sql1 = "select FreQ_B, FreQ_E,FreQ_BW，Freq_CF from SPECTRUM_IDENTIFIED where Start_time = DATE_FORMAT('%s'," % (start_time) + "'%Y-%m-%d %H:%i:%S')"+" and Signal_No=%d" % int(numb)
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    c_xi = pandas.read_sql(sql1, con)
    con.commit()
    con.close()
    start_freq_xi = c_xi['FreQ_B'][0]
    end_freq_xi = c_xi['FreQ_E'][0]
    bandwith_xi = c_xi['FreQ_BW'][0]
    cf_xi = c_xi['FreQ_CF'][0]
    path = raw_path+"//"+file_name+'.csv'
    df_xi = pandas.read_csv(path)
    x_freq_xi = np.array(df_xi['frequency'])
    y_power_xi = np.array(df_xi['power'])
    return start_freq_xi,end_freq_xi,bandwith_xi,cf_xi,x_freq_xi,y_power_xi
# 无人机IQ数据导入，输入是文件名和该文件所在的地址
def importData_uav(file_name,raw_path):
    path = raw_path + "//" + file_name + '.csv'
    df_cu = pandas.read_csv(path)
    num = int(len(df_cu) / 1024)
    I_mat = np.array(df_cu['I']).reshape(num, 1024)
    Q_mat = np.array(df_cu['Q']).reshape(num, 1024)
    return I_mat,Q_mat
# 测向输入就是一个频率输出就是对应的强度
def find_direction(freq):
    os.chdir("E:/项目/洪（私）/pro/RSA_API/lib/x64")
    rsa300 = WinDLL("RSA_API.dll")

    # create Spectrum_Settings data structure
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
    cf = c_double(freq)  # center freq
    refLevel = c_double(0)  # ref level
    ready = c_bool(False)  # ready
    timeoutMsec = c_int(500)  # timeout
    trace = c_int(0)  # select Trace 1
    detector = c_int(1)  # set detector type to max

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
    specSet.span = c_double(1e6)
    specSet.rbw = c_double(300e3)
    # specSet.enableVBW =
    # specSet.vbw =
    specSet.traceLength = c_int(801)
    # specSet.window =
    # specSet.verticalUnit =
    specSet.actualStartFreq = c_double(freq-0.5e6)
    specSet.actualStopFreq = c_double(freq+0.5e6)
    # specSet.actualFreqStepSize =c_double(50000.0)
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
    # print('Peak power in spectrum: %4.3f dBm @ %d Hz' % (peakPower, peakPowerFreq))
    return peakPower
# 输入就是大小为36的信号强度的list
def ce_xiang_plot(a):
    N = len(a)
    theta = np.linspace(0.0, 2 * np.pi, N, endpoint=True)
    a = np.array(a)
    xnew = np.linspace(theta.min(),theta.max(),300)
    power_smooth = spline(theta,a,xnew)
    plt.polar(xnew,power_smooth)
    plt.show()
# 测试test_num
def test_no(test_no):
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    sql = "select Test_No from uav where Test_No = %s" %(int(test_no))
    c = pandas.read_sql(sql, con)
    if len(c) == 0:
        print('Right')
    else:
        print('error')
# 台站对比点击地图上的台站站点返回台站信息
def get_station_inf():
    sql1 = "select STAT_TYPE,FREQ_EFB,FREQ_LC,FREQ_UC,FREQ_MOD,STAT_LG,STAT_LA from rsbt_station "
    sql2 = "select LOGITUDE,LATITUDE from spectrum_identified"
    con1 = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    inf1 = pandas.read_sql(sql1, con1)
    inf2 = pandas.read_sql(sql2, con1)
    inf2 = inf2.drop_duplicates()
    #print(inf2)
    result1 = {}
    result2 = {}
    #print(len(inf2))
    for i in range(len(inf2)):
        result2[(i + 1)] = [inf2['LOGITUDE'][i], inf2['LATITUDE'][i]]
    for i in range(len(inf1)):
        result1[(i + 1)] = [inf1['STAT_LG'][i], inf1['STAT_LA'][i],[inf1['STAT_TYPE'][i], inf1['FREQ_EFB'][i], inf1['FREQ_LC'][i], inf1['FREQ_UC'][i],inf1['FREQ_MOD'][i]]]
    print(result1, result2)
    return result1,result2


def reflect_inf(freq_lc,freq_uc,longitude,latitude):
    sql2 = "select FreQ_B,FreQ_E,FREQ_CF,FreQ_BW from spectrum_identified where FreQ_B >= %s and FreQ_E<=%s and LOGITUDE=%s and LATITUDE=%s"%(float(freq_lc),float(freq_uc),float(longitude),float(latitude))
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    ref = pandas.read_sql(sql2,con)
    print(ref)
    result=[]
    if len(ref) == 0:
        print('no match data this test point is illegal')
    else:
        result = [ref['FreQ_B'][0],ref['FreQ_E'][0],ref['FREQ_CF'][0],ref['FreQ_BW'][0]]
    return result

# 数据库写入
def rmbt_facility_freq_emenv(task_name, start_time, end_time, ssid,servicedid, mfid='11000001400001', statismode='04',
                             amplitudeunit='01', threshold=6):
    # sql2 = "select Signal_No, Start_time, FREQ_CF, FreQ_BW, COUNT1, peakpower, channel_no from spectrum_identified where Task_Name='%s'" % (task_name)
    sql2 = "select count1,legal from SPECTRUM_IDENTIFIED where Task_Name='%s'" % (
        task_name) + "&& Start_time between DATE_FORMAT('%s'," % (
        start_time) + "'%Y-%m-%d %H:%i:%S')" + "and DATE_FORMAT('%s'," % (end_time) + "'%Y-%m-%d %H:%i:%S')"
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    inf = pandas.read_sql(sql2, con)
    df = inf
    con.close()
    list1 = df['Signal_no'].drop_duplicates().values
    df_r = []
    for i in range(len(list1)):
        df1 = df[df['Signal_No'] == list1[i]]
        df1["index"] = range(len(df1))
        df1 = df1.set_index(["index"])
        df_r.append(df1)
    for sig in range(len(df_r)):
        occ = len(df_r[sig]['COUNT1'].drop_duplicates()) / float(len(df['COUNT1'].drop_duplicates()))
        if occ == 1:
            occ = Decimal(occ).quantize(Decimal('0.00'))
        else:
            occ = Decimal(occ * 100).quantize(Decimal('0.00'))
        statisstartday = str(start_time)
        statisendday = str(end_time)
        threshold = Decimal(threshold).quantize(Decimal('0.00'))
        con = mdb.connect('localhost', 'root', '17704882970', '110000_rmdsd')
        with con:
            # 获取连接的cursor，只有获取了cursor，我们才能进行各种操作
            cur = con.cursor()  # 一条游标操作就是一条数据插入，第二条游标操作就是第二条记录，所以最好一次性插入或者日后更新也行
            cur.execute("INSERT INTO rmbt_facility_freq_emenv VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        [str(mfid), statisstartday, statisendday, str(statismode), str(servicedid), cf_avg,band_avg,
                         str(ssid), str(amplitudeunit), maxamplitude, midamplitude, occ, threshold])
            cur.close()
        con.commit()
        con.close()

def rmbt_facility_freq_emenv(task_name,start_time,end_time,ssid,mfid='11000001400001',statismode='04',amplitudeunit='01',threshold=6):
    #sql2 = "select Signal_No, Start_time, FREQ_CF, FreQ_BW, COUNT1, peakpower, channel_no from spectrum_identified where Task_Name='%s'" % (task_name)
    sql2 = "select count1 from SPECTRUM_IDENTIFIED where Task_Name='%s'" % (
        task_name) + "&& Start_time between DATE_FORMAT('%s'," % (
        start_time) + "'%Y-%m-%d %H:%i:%S')" + "and DATE_FORMAT('%s'," % (end_time) + "'%Y-%m-%d %H:%i:%S')"
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    inf = pandas.read_sql(sql2, con)
    df = inf
    con.close()
    list1 = df['Signal_no'].drop_duplicates().values
    df_r = []
    point_r = []
    for i in range(len(list1)):
        point = [0]
        df1 = df[df['Signal_No'] == list1[i]]
        df1["index"] = range(len(df1))
        df1 = df1.set_index(["index"])
        df_r.append(df1)
        for j in range(1,len(df1)):
            if df1['COUNT1'][j] - df1['COUNT1'][j-1] > 1:
                point.append(i)
        point_r.append(point)
    for sig in range(len(df_r)):
        occ = len(df_r[sig]['COUNT1'].drop_duplicates()) / float(len(df['COUNT1'].drop_duplicates()))
        if occ == 1:
            occ = Decimal(occ).quantize(Decimal('0.00'))
        else:
            occ = Decimal(occ * 100).quantize(Decimal('0.00'))
        if len(point_r[sig]) == 0:
            statisstartday = str(df_r[sig]['Start_time'][0])
            statisendday = str(df_r[sig]['Start_time'][len(df_r[sig])-1])
            servicedid = df_r[sig]['Signal_No'][0]
            cf = df_r[sig]['FREQ_CF'].values
            cf_avg = np.average(cf) / 10e6
            cf_avg = Decimal(cf_avg).quantize(Decimal('0.0000000'))
            bandwidth = df_r[sig]['FreQ_BW'].values
            band_avg = np.average(bandwidth) / 10e6
            band_avg = Decimal(band_avg).quantize(Decimal('0.0000000'))
            maxamplitude = np.max(df_r[sig]['peakpower'].values)
            maxamplitude = Decimal(maxamplitude).quantize(Decimal('0.00'))
            midamplitude = maxamplitude / 2
            threshold = Decimal(threshold).quantize(Decimal('0.00'))
            con = mdb.connect('localhost', 'root', '17704882970', '110000_rmdsd')
            with con:
                # 获取连接的cursor，只有获取了cursor，我们才能进行各种操作
                cur = con.cursor()  # 一条游标操作就是一条数据插入，第二条游标操作就是第二条记录，所以最好一次性插入或者日后更新也行
                cur.execute("INSERT INTO rmbt_facility_freq_emenv VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            [str(mfid), statisstartday, statisendday, str(statismode), str(servicedid), cf_avg, band_avg, str(ssid),str(amplitudeunit), maxamplitude,midamplitude, occ, threshold])
                cur.close()
            con.commit()
            con.close()
        else:
            point_r[sig].append(len(df_r[sig])-1)
            for i in range(1,len(point_r[sig])):
                start_index = point_r[sig][i-1]
                end_index = point_r[sig][i]-1
                statisstartday = str(df_r[sig]['Start_time'][start_index])
                statisendday = str(df_r[sig]['Start_time'][end_index])
                servicedid = df_r[sig]['Signal_No'][0]
                cf = df_r[sig]['FREQ_CF'][start_index:end_index].values
                cf_avg = np.average(cf)/10e6
                cf_avg = Decimal(cf_avg).quantize(Decimal('0.0000000'))
                bandwidth = df_r[sig]['FreQ_BW'][start_index:end_index].values
                band_avg = np.average(bandwidth)/10e6
                band_avg = Decimal(band_avg).quantize(Decimal('0.0000000'))
                maxamplitude = np.max(df_r[sig]['peakpower'][start_index:end_index].values)
                maxamplitude = Decimal(maxamplitude).quantize(Decimal('0.00'))
                midamplitude = maxamplitude / 2
                threshold = Decimal(threshold).quantize(Decimal('0.00'))
                con = mdb.connect('localhost', 'root', '17704882970', '110000_rmdsd')
                with con:
                    # 获取连接的cursor，只有获取了cursor，我们才能进行各种操作
                    cur = con.cursor()  # 一条游标操作就是一条数据插入，第二条游标操作就是第二条记录，所以最好一次性插入或者日后更新也行
                    cur.execute(
                        "INSERT INTO rmbt_facility_freq_emenv VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        [str(mfid), statisstartday, statisendday, str(statismode), str(servicedid), cf_avg, band_avg, str(ssid),str(amplitudeunit), maxamplitude,midamplitude, occ, threshold])
                    cur.close()
                con.commit()
                con.close()

def rmbt_facility_freq_emenv0(task_name,start_time,end_time,ssid,mfid='11000001400001',statismode='04',amplitudeunit='01',threshold=6):
    #sql2 = "select Signal_No, Start_time, FREQ_CF, FreQ_BW, COUNT1, peakpower, channel_no from spectrum_identified where Task_Name='%s'" % (task_name)
    sql2 = "select count1 from SPECTRUM_IDENTIFIED where Task_Name='%s'" % (
        task_name) + "&& Start_time between DATE_FORMAT('%s'," % (
        start_time) + "'%Y-%m-%d %H:%i:%S')" + "and DATE_FORMAT('%s'," % (end_time) + "'%Y-%m-%d %H:%i:%S')"
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    inf = pandas.read_sql(sql2, con)
    df = inf
    con.close()
    list1 = df['Signal_no'].drop_duplicates().values
    df_r = []
    for i in range(len(list1)):
        df1 = df[df['Signal_No'] == list1[i]]
        df1["index"] = range(len(df1))
        df1 = df1.set_index(["index"])
        df_r.append(df1)
    for sig in range(len(df_r)):
        occ = len(df_r[sig]['COUNT1'].drop_duplicates()) / float(len(df['COUNT1'].drop_duplicates()))
        if occ == 1:
            occ = Decimal(occ).quantize(Decimal('0.00'))
        else:
            occ = Decimal(occ * 100).quantize(Decimal('0.00'))
        statisstartday = str(start_time)
        statisendday = str(end_time)
        servicedid = df_r[sig]['Signal_No'][0]
        cf = df_r[sig]['FREQ_CF'].values
        cf_avg = np.average(cf) / 10e6
        cf_avg = Decimal(cf_avg).quantize(Decimal('0.0000000'))
        bandwidth = df_r[sig]['FreQ_BW'].values
        band_avg = np.average(bandwidth) / 10e6
        band_avg = Decimal(band_avg).quantize(Decimal('0.0000000'))
        maxamplitude = np.max(df_r[sig]['peakpower'].values)
        maxamplitude = Decimal(maxamplitude).quantize(Decimal('0.00'))
        midamplitude = maxamplitude / 2
        threshold = Decimal(threshold).quantize(Decimal('0.00'))
        con = mdb.connect('localhost', 'root', '17704882970', '110000_rmdsd')
        with con:
            # 获取连接的cursor，只有获取了cursor，我们才能进行各种操作
            cur = con.cursor()  # 一条游标操作就是一条数据插入，第二条游标操作就是第二条记录，所以最好一次性插入或者日后更新也行
            cur.execute("INSERT INTO rmbt_facility_freq_emenv VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        [str(mfid), statisstartday, statisendday, str(statismode), str(servicedid), cf_avg, band_avg,
                         str(ssid), str(amplitudeunit), maxamplitude, midamplitude, occ, threshold])
            cur.close()
        con.commit()
        con.close()

def rmbt_facility_freq_emenv1(task_name,start_time,end_time,ssid,mfid='11000001400001',statismode='04',amplitudeunit='01',threshold=6):
    sql1 = "select count1 from SPECTRUM_IDENTIFIED where Task_Name='%s'" % (
    task_name) + "&& Start_time between DATE_FORMAT('%s'," % (
    start_time) + "'%Y-%m-%d %H:%i:%S')" + "and DATE_FORMAT('%s'," % (end_time) + "'%Y-%m-%d %H:%i:%S')"
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    inf = pandas.read_sql(sql1, con)
    df = inf
    con.close()
    list1 = df['channel_no'].drop_duplicates().values
    #for i in range(len(list1)):



def rmbt_freq_occupancy():
    pass



def taizhan_in(str_time,start_freq,stop_freq,longgitude,latitude,cf_freq,bandwidth):
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    with con:
        # 获取连接的cursor，只有获取了cursor，我们才能进行各种操作
        cur = con.cursor()  # 一条游标操作就是一条数据插入，第二条游标操作就是第二条记录，所以最好一次性插入或者日后更新也行
        cur.execute("INSERT INTO new_inf VALUES(%s,%s,%s,%s,%s,%s,%s)",[str_time,float(start_freq),float(stop_freq),longgitude,latitude,cf_freq,bandwidth])
        cur.close()
    con.commit()
    con.close()

def taizhan_out(task_name):
    reflect_inf = {1: [], 2: [], 3: [], 4: [], 5: []}
    sql = "select cf,bf,ef,band,logitude,latitude from SPECTRUM_IDENTIFIED where task_name=%s" % (task_name)
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    inf = pandas.read_sql(con, sql)
    inf1 = inf.drop_duplicates(['channel_no'])
    cf = []
    bf = []
    ef = []
    band = []
    longitude = []
    latitude = []
    illegal = []
    for i in inf1.values:
        cf.append(i[0])
        bf.append(i[1])
        ef.append(i[2])
        band.append(i[3])
        longitude.append(i[4])
        latitude.append(i[5])
    ##########台站对比###########


def rmbt_freq_occupancy(span,start_time,end_time,startFreq,stopFreq,longitude,latitude,height,mfid='11000001400001',addr='aasfasdfasfasdf',amplitudeunit='01'):
    txt = str(0)
    step = span / float(801)
    startFreq1 = Decimal(startFreq).quantize(Decimal('0.0000000'))
    stopFreq1 = Decimal(stopFreq).quantize(Decimal('0.0000000'))
    step1 = Decimal(step).quantize(Decimal('0.0000000'))
    longitude1 = Decimal(longitude).quantize(Decimal('0.000000000'))
    latitude1 = Decimal(latitude).quantize(Decimal('0.000000000'))
    height1 = Decimal(height).quantize(Decimal('0.00'))
    con = mdb.connect(mysql_config['host'], mysql_config['user'], mysql_config['password'],
                      mysql_config['database'])
    # con = mdb.connect('localhost', 'root', 'cdk120803', 'ceshi1')
    with con:
        # 获取连接的cursor，只有获取了cursor，我们才能进行各种操作
        cur = con.cursor()  # 一条游标操作就是一条数据插入，第二条游标操作就是第二条记录，所以最好一次性插入或者日后更新也行
        # print([str_time, start_time, str_time1, float(t), float(s_c), path, deviceSerial, anteid, count])
        cur.execute("INSERT INTO RMBT_FREQ_OCCUPANCY VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [mfid,str(start_time), str(end_time), startFreq1, stopFreq1, step1, longitude1, latitude1, height1,
                     addr, amplitudeunit, txt])
        cur.close()
    con.commit()
    con.close()












#connect()
#a,b=get_station_inf()
#print(a,b)
#a = reflect_inf(0,2e9,float(116.41),float(39.85))
#uav(10, 3, 'we', 'dsds', 300e3)
#spectrum2('dsds','dsds',1e9,2e9,1e9,300e3,50,300e3)
#channel_occ('2017-09-25 16:49:05','2017-09-25 16:49:56','2017-09-26-11-12-04',1000000000,2000000000)
#plot_spectrum_occ('2017-09-25 16:49:05','2017-09-25 16:49:56','2017-09-25-16-49-05',1000000000,2000000000)
#ce_xiang_plot([12,14,12,1,21,2,12,12,23])
#detectNoise()
'''
更改：
spectrum2中给细扫描新增了一个文件夹，粗单独放细放在文件夹中
频谱数据和IQ数据都分spec和IQ两个文件夹存储
新增了importData_cu导入频谱粗扫数据importData_xi导入细扫描数据并且返回带宽中心频点起始时间啥的importData_uav导入无人机IQ数据
无人机的程序一共有uav,uav0,uav1,uav00，uav00是在频谱检测中那个小图上直接调用的，其他三个是专门为无人机检测调用的，uav调用uav1存储IQ数据调用uav0求检测到的所有无人机信号
最后返回3个list。a,b,c,a代表驻留时间，b存储无人机信号的带宽，c存储无人机信号的中心频点
每个函数对应的都进行了注释
'''