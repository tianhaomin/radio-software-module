import numpy as np
import matplotlib.pyplot as plt
import seaborn
import pandas
from pandas import DataFrame
import datetime
import time
import pymysql as mdb
# 计算信道占用度
# 参数：起始时间、终止时间、任务名称、其实频率、终止频率
def channel_occ(start_time,stop_time,task_name,freq_start,freq_stop):
    # 输入就是起始时间、终止时间、任务名称、起始频率、终止频率
    step = float(freq_stop - freq_start) / 40
    sql2 = "select count1 from SPECTRUM_IDENTIFIED where Task_Name='%s'" % (task_name) + "&& Start_time between DATE_FORMAT('%s'," % (start_time) + "'%Y-%m-%d %H:%i:%S')" + "and DATE_FORMAT('%s'," % (stop_time) + "'%Y-%m-%d %H:%i:%S')"
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    b = pandas.read_sql(sql2, con)
    channel_occupied = []
    for i in range(40):
        start_f = freq_start + i * step
        stop_f = freq_start + (i + 1) * step
        sql1 = "select count1 from SPECTRUM_IDENTIFIED where Task_Name='%s' && FREQ_CF between %f and %f "%(task_name, float(start_f), float(stop_f))+"&& Start_time between DATE_FORMAT('%s',"%(start_time)+"'%Y-%m-%d %H:%i:%S')"+"and DATE_FORMAT('%s'," % (stop_time)+"'%Y-%m-%d %H:%i:%S')"
        a = pandas.read_sql(sql1, con)
        a = a.drop_duplicates()  # 去电重复项
        channel_occupied1 = len(a) / float(max(b['count1']) - min(b['count1']))
        channel_occupied.append(channel_occupied1)
    # 绘制柱状图
    axis_x = np.arange(freq_start, freq_stop, 40)
    axis_y = channel_occupied
    plt.bar(axis_x, axis_y, 2)
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
    num = max(c['COUNT1']) - min(c['COUNT1'])
    spectrum_occ = spectrum_occ1 / float(num * spectrum_span)
    return spectrum_occ  # 返回频谱占用度
# 绘制频谱占用度图像
# 参数：起始时间、终止时间、任务名称、其实频率、终止频率
def plot_spectrum_occ(start_time,stop_time,task_name,freq_start,freq_stop):
    starttime = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    stoptime = datetime.datetime.strptime(stop_time, "%Y-%m-%d %H:%M:%S")
    delta = int((stoptime - starttime).seconds/3600)
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



