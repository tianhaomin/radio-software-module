import pandas
import pymysql as mdb
#返回的result1是台站信息一个字典{编号：[经度，维度，[状态信息，带宽，起始频率，终止频率，调制方式]]}
#返回的result2是测试点信息是一个list[[测试点1的经纬度],[测试点2的经纬度]，.....[]]
def get_station_inf():
    sql1 = "select STAT_TYPE,FREQ_EFB,FREQ_LC,FREQ_UC,FREQ_MOD,STAT_LG,STAT_LA from rsbt_station "
    sql2 = "select LOGITUDE,LATITUDE from spectrum_identified"
    con1 = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    inf1 = pandas.read_sql(sql1, con1)
    inf2 = pandas.read_sql(sql2, con1)
    inf2 = inf2.drop_duplicates()
    # print(inf2)
    result1 = {}
    result2 = {}
    # print(len(inf2))
    for i in range(len(inf2)):
        result2[(i + 1)] = [inf2['LOGITUDE'][i], inf2['LATITUDE'][i]]
    for i in range(len(inf1)):
        result1[(i + 1)] = [inf1['STAT_LG'][i], inf1['STAT_LA'][i],
                            [inf1['STAT_TYPE'][i], inf1['FREQ_EFB'][i], inf1['FREQ_LC'][i], inf1['FREQ_UC'][i],
                             inf1['FREQ_MOD'][i]]]
    print(result1, result2)
    return result1, result2