#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2020-07-15 21:31
# @Author  : NingAnMe <ninganme@qq.com>
import os
app_path = r"dist\e\e.exe"

longitude = 120.1
latitude = 60.1
datetime_start = '201901010000'
datetime_end = '202012312359'
out_file = '{:02f}_{:02f}.csv'.format(longitude, latitude)
frequency = 'minute'


print('<<< :{}'.format(longitude))
print('<<< :{}'.format(latitude))
print('<<< :{}'.format(datetime_start))
print('<<< :{}'.format(datetime_end))
print('<<< :{}'.format(out_file))
os.system("{} --mode one --longitude {} --latitude {} --datetime_start {} --datetime_end {} --outfile {} --frequency {}".format(
    app_path, longitude, latitude, datetime_start, datetime_end, out_file, frequency))
print('>>> {}'.format(out_file))
