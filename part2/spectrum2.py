from part2 import detectNoise
from ctypes import *
import numpy as np
import sys
import matplotlib.pyplot as plt
import os
import seaborn
import pandas
from pandas import DataFrame
import datetime
import time
from part2 import spectrum1
from part2 import connect
from part2 import uav0
import pymysql as mdb
from part2 import occupie
# 频谱监测（总）
# 输入参数是监测设备信息，天线信息，起始频率，终止频率，频率跨度，rbw，持续时间
def spectrum2(deviceSerial, anteid, startFreq, stopFreq, span, rbw, t):
    os.chdir("E:/项目/洪（私）/pro/RSA_API/lib/x64")
    rsa300 = WinDLL("RSA_API.dll")
    # 进行连接获得检测设备信息
    # print (average)
    # 参数设置
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
    while time.time() - time_ref < t:
        average = detectNoise.detectNoise()
        count += 1
        str_tt1 = str(datetime.datetime.now().strftime('%F %H:%M:%S'))  # 内部扫频的时刻
        str_tt2 = str(datetime.datetime.now().strftime('%F-%H-%M-%S'))  # 作为内部细扫的文件名
        z1, z2, z3, = spectrum1.spectrum(average, startFreq, stopFreq, span, rbw, str_time, count, str_tt1, str_tt2)
        trace = pandas.concat([trace, z1])
        restf.append(z2)
        restp.append(z3)
        # 主检测页面显示无人机频谱监测
        uav0.uav00()

    # 获取测试时间,保存原始频谱数据
    path = "E:\data111\\" + str_time + "spectrum%ds.csv" % t  # 频谱数据粗扫描数据存储路径
    trace.to_csv(
        path,
        index=False
    )
    str_time1 = str(datetime.datetime.now().strftime('%F %H:%M:%S'))  # 结束的准确时间，直接传到数据库中自动转化成datetime格式
    s_c = occupie.spectrum_occ(start_time, str_time1, str_time, startFreq.value, stopFreq.value)
    print('12121212')
    print(s_c)
    # 数据库构建
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    with con:
        # 获取连接的cursor，只有获取了cursor，我们才能进行各种操作
        cur = con.cursor()  # 一条游标操作就是一条数据插入，第二条游标操作就是第二条记录，所以最好一次性插入或者日后更新也行
        cur.execute("INSERT INTO Minitor_Task VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",[str_time, start_time, str_time1, float(t), float(s_c), path, deviceSerial, anteid, count])
        cur.close()
    con.commit()
    con.close()

spectrum2('zze', 'dswd', 1.83e9, 1.84e9, 10e6, 300e3, 30)


