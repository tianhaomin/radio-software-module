import datetime
import os
import pandas
import pymysql as mdb
def read_file(file):
    path = "E://"+file
    retain_time = 0
    for filename in os.listdir(path):
        if filename[-5] == 's':
            retain_time = int(filename[27:-5])
            break
    file1 = file[:10]+' '+file[11:13]+':'+file[14:16]+':'+file[17:19]
    start_time = datetime.datetime.strptime(file1, "%Y-%m-%d %H:%M:%S")
    end_time = start_time + datetime.timedelta(seconds=retain_time)
    sql = "select startFreq,endFreq from minitor_task where Task_Name='%s'"%(file)
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    c = pandas.read_sql(sql, con)
    con.commit()
    con.close()
    start_freq = c['startFreq'][0]
    end_freq = c['endFreq'][0]

    return str(start_time),str(end_time),float(start_freq),float(end_freq)
