import json
from urllib.request import urlopen,quote
import requests,csv
import pandas as pd
import pymysql as mdb

def getInglat(address):
    url = 'http://api.map.baidu.com/geocoder/v2/'
    output = 'json'
    ak = 'bl3XjLKaPBdCcxlIFiTg0GfFQ95jzj5F'
    add = quote(address)
    uri = url+ '?' + 'address=' + add + '&output=' + output + '&ak=' + ak
    req = urlopen(uri)
    res = req.read().decode()
    temp = json.loads(res)
    return temp

file = open(r'E:\\point.json','w') # 建立json文件
sql = "select longitude,latitude from database1"
con = mdb.connect('localhost', 'root', '17704882970', 'ceshi1')
position = pd.read_sql(sql,con)
file.write(position)