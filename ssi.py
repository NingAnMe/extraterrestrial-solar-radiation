#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2020-04-01 15:10
# @Author  : NingAnMe <ninganme@qq.com>
from dateutil.relativedelta import relativedelta
import numpy as np

G0_Correct = 0.75  # 使用G0订正Itol的系数

ER_TXT = 'er.txt'
EP_TXT = 'ep.txt'


def cos(x):
    return np.cos(np.radians(x))


def sin(x):
    return np.sin(np.radians(x))


def isleap(y):
    y = int(y)
    return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0


def calDoy(y, m, d):
    y = int(y)
    m = int(m)
    d = int(d)
    Doy = 0
    a = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if isleap(y):
        a[1] = 29
    for x in a[0:m - 1]:
        Doy += x
    return Doy + d


def calDelta(Doy):
    # print "360/365*(284 + Doy) is %f" % (360.0/365*(284 + Doy))
    return 23.45 * sin(360.0 / 365 * (284 + Doy))


def calOmega(hr, min, lon, E):
    print(hr, min, lon, E)
    TT = hr + min / 60.0 + 4 * (lon - 120) / 60.0 + E / 60.0
    print('TT', TT)
    return (TT - 12) * 15


def calCosThetaz(lat, Delta, Omega):
    print('lat, Delta, Omega', lat, Delta, Omega)
    return cos(lat) * cos(Delta) * cos(Omega) + sin(lat) * sin(Delta)


def calEDNI(Doy):
    return 1366.1 * (1 + 0.033 * cos(360.0 / 365 * Doy))


def calG0(Doy, CosThetaz):
    EDNI = calEDNI(Doy)
    print(EDNI)
    return EDNI * CosThetaz


def calRb(lat, Beta, Delta, Omega, CosThetaz):
    return (cos(lat - Beta) * cos(Delta) * cos(Omega) + sin(lat - Beta) * sin(Delta)) / CosThetaz


def calGt(Ib, Id, Ai, Rb, Beta, Itol):
    return (Ib + Id * Ai) * Rb + Id * (1 - Ai) * (1 + cos(Beta)) / 2.0 + Itol * 0.2 * (1 - cos(Beta)) / 2.0


def assignTime(date):
    """
    DEBUG函数assignTime，原来的函数直接在hour加8可能超过24
    :param date:
    :return:
    """
    date += relativedelta(hours=8)  # 修改时间为北京时
    print(date)
    datestrf = date.strftime('%Y-%m-%d-%H-%M-%S')
    y, m, d, h, mm, s = datestrf.split('-')
    return [int(i) for i in (y, m, d, h, mm)]


def assignE(y, m, d):
    """
    assignE
    :param y:
    :param m:
    :param d:
    :return:
    """
    y = int(y)
    m = int(m)
    d = int(d)
    if isleap(y):
        e_file = ER_TXT
    else:
        e_file = EP_TXT
    e_data = np.loadtxt(e_file)
    md = int('{:02d}{:02d}'.format(m, d))

    index = np.where(e_data == md)
    row = index[0]
    if row.size != 0:
        return e_data[row, 1]
    else:
        raise ValueError('没有找到E值： {}'.format((y, m, d)))


def cal_tol(date_time, lons, lats):
    """
    计算理论太阳能辐照度
    :param date_time: 世界时时间
    :return:
    """
    y, m, d, hr, minus = assignTime(date_time)
    e = assignE(y, m, d)
    doy = calDoy(y, m, d)
    delta = calDelta(doy)
    print('delta', delta)
    Omega = calOmega(hr, minus, lons, e)
    print('Omega', Omega)
    cos_the_taz = calCosThetaz(lats, delta, Omega)
    print('cos_the_taz', cos_the_taz)
    G0 = calG0(doy, cos_the_taz)
    print('G0', G0)
    itol = G0_Correct * G0
    return itol


if __name__ == '__main__':
    from datetime import datetime
    date_time = datetime.strptime('19990101060000', '%Y%m%d%H%M%S')
    print(date_time)
    print(cal_tol(date_time, 116.55, 40.12))