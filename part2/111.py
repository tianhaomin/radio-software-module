def rmbt_freq_occupancy(span,start_time,end_time,startFreq,stopFreq,longitude,latitude,height,trace1,average mfid='11000001400001',addr='aasfasdfasfasdf',amplitudeunit='01'):
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
    z = pandas.DataFrame({})
    point = np.arange(0,801,1)
    z['freq_point'] = point
    z['freq_startFreq'] = trace1['frequency'][0:801]
    peak_list = []
    mid_list = []
    occ = []
    for i in z['freq_startFreq']:
        temp = trace1[trace1['frequency']==i]
        temp1 = np.sort(temp['power'])
        peak = np.max(temp['power'].values)
        mid = temp1[int(len(temp)/2)]
        occ = len(temp[temp['power']>average+6])/float(len(temp))
        occ = round(occ,2)
        occ.append(occ*100)
        mid_list.append(mid)
        peak_list.append(peak)
    z['Max_peak'] = peak_list
    z['mid'] = mid_list
    z['occ'] = occ
    z['threshold'] = 6
    z.to_csv(path1)
    file = open(path1)
    load_file = file.read()
    file.close()
    with con:
        # 获取连接的cursor，只有获取了cursor，我们才能进行各种操作
        cur = con.cursor()  # 一条游标操作就是一条数据插入，第二条游标操作就是第二条记录，所以最好一次性插入或者日后更新也行
        # print([str_time, start_time, str_time1, float(t), float(s_c), path, deviceSerial, anteid, count])
        cur.execute("INSERT INTO RMBT_FREQ_OCCUPANCY VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [mfid,str(start_time), str(end_time), startFreq1, stopFreq1, step1, longitude1, latitude1, height1,
                     addr, amplitudeunit, load_file])
        cur.close()
    con.commit()
    con.close()



def rmbt_facility_freqband_emenv(task_name,span,start_time,end_time,longitude,latitude,mfid='11000001400001', statismode='04',serviceid='1',address='aasfasdfasfasdf',threshold=6,occ2=0,height=0):
    sql2 = "select FreQ_BW,count1,legal from SPECTRUM_IDENTIFIED where Task_Name='%s'" % (
        task_name) + "&& Start_time between DATE_FORMAT('%s'," % (
        start_time) + "'%Y-%m-%d %H:%i:%S')" + "and DATE_FORMAT('%s'," % (end_time) + "'%Y-%m-%d %H:%i:%S')"
    con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
    inf = pandas.read_sql(sql2, con)
    statisstartday = str(start_time)
    statisendday = str(end_time)
    latitude = Decimal(latitude).quantize(Decimal('0.000000000'))
    longitude = Decimal(longitude).quantize(Decimal('0.000000000'))
    frame_num = len(inf['COUNT1'].drop_duplicates())
    sig = np.sum(inf['FreQ_BW'].values)
    occ = (float(sig)*100) / (span*frame_num)
    bandoccupancy = Decimal(occ).quantize(Decimal('0.00'))
    threshold = Decimal(threshold).quantize(Decimal('0.00'))
    height = Decimal(height).quantize(Decimal('0.00'))
    ######legal=1是合法0是非法
    legal_sig = inf[inf['legal']==1]
    legal_frame_num = len(legal_sig['COUNT1'].drop_duplicates())
    legal_band = np.sum(legal_sig['FreQ_BW'].values)
    occ1 = float(legal_band*100)/(span*legal_frame_num)
    occ1 = Decimal(occ1).quantize(Decimal('0.00'))
    occ2 = Decimal(occ2).quantize(Decimal('0.00'))
    occ3  =100 - occ1
    occ3 = Decimal(occ3).quantize(Decimal('0.00'))
    con.close()
    con = mdb.connect('localhost', 'root', '17704882970', '110000_rmdsd')
    with con:
        # 获取连接的cursor，只有获取了cursor，我们才能进行各种操作
        cur = con.cursor()  # 一条游标操作就是一条数据插入，第二条游标操作就是第二条记录，所以最好一次性插入或者日后更新也行
        cur.execute("INSERT INTO rmbt_facility_freqband_emenv VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [mfid, statisstartday, statisendday, statismode, serviceid, bandoccupancy, threshold, occ1, occ2, occ3,
                     latitude, longitude, height, address])
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
        temp = np.sort(df_r[sig]['peakpower'])
        mid = temp[int(len(temp) / 2)]
        midamplitude = mid
        midamplitude = Decimal(midamplitude).quantize(Decimal('0.00'))
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