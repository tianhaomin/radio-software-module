# 根据选择摸一个台站进行匹配
# 输入经纬度起始终止频率返回[测试点经度，维度，起始频率，终止频率，中心频点，带宽]
import pandas
import pymysql as mdb
def reflect_inf(freq_lc,freq_uc,longitude,latitude):
    sql2 = "select FreQ_B,FreQ_E,FREQ_CF,FreQ_BW from spectrum_identified where FreQ_B >= %s and FreQ_E<=%s and LOGITUDE=%s and LATITUDE=%s" % (
    float(freq_lc), float(freq_uc), float(longitude), float(latitude))
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    ref = pandas.read_sql(sql2, con)
    print(ref)
    result = []
    if len(ref) == 0:
        print('no match data')
    else:
        result = [ref['FreQ_B'][0], ref['FreQ_E'][0], ref['FREQ_CF'][0], ref['FreQ_BW'][0]]
    return result