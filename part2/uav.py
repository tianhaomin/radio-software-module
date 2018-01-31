import datetime
import time
from part2 import uav0
from part2 import detectNoise
import pandas
from pandas import DataFrame
from part2 import connect
import pymysql as mdb
# 监测无人机信号
def uav(t_r, test_No, deviceSerial, anteid):  # 参数是持续时间、测试编号、监测设备信息、天线信息
    #deviceSerial = connect.connect()  # 随设备进行连接然后获取设备信息
    trace_IQ = DataFrame({})
    count = 0
    average = detectNoise.detectNoise()
    a = []  # 存储无人机出现的时间段
    b = []  # 存储无人机信号出现的带宽
    c = []  # 存储无人机信号出现的中心频点
    str_time = str(datetime.datetime.now().strftime('%F-%H-%M-%S'))  # 无人机检测起始时间
    t_ref = time.time()
    while time.time() - t_ref < t_r:
       peakFreq, band, peak = uav0.uav0()
       if peak > average + 6 and count == 0:
           t1 = time.time()
           count = 1
           b.append(band)
           c.append(peakFreq)
       elif peak > average + 6 and count == 1:
           pass
       else:
           t2 = time.time()
           count = 0
           a.append(t2-t1)
       df1 = uav0.uav1()
       trace_IQ = pandas.concat([trace_IQ, df1])
    path = "E:\data11\\" + str_time + "IQ%s.csv" % t_r   # IQ数据存储路径
    trace_IQ.to_csv(
        path,
        index=False
    )
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    with con:
        # 操作数据库需要一次性的进行，一条代码就是写入一行所以一次就把表的一行全部写入
        cur = con.cursor()
        cur.execute("INSERT INTO uav VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", [int(test_No), str_time, str_time, float(c[0]-b[0]/2), float(c[0] + b[0] / 2), float(b[0]), path, deviceSerial, anteid])
        cur.close()
    con.commit()
    con.close()
    return a



