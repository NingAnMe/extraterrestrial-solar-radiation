#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2020-05-13 16:48
# @Author  : NingAnMe <ninganme@qq.com>
import os
import sys
import argparse
from numpy import loadtxt
from numpy import cos as np_cos
from numpy import sin as np_sin
from numpy import radians, arcsin, rad2deg, cumsum
from numpy import ones
from numpy import int16, int8
from numpy import object as np_object
from numpy import array
from numpy import logical_and, logical_or
from numpy import full_like
from pandas import DataFrame, read_excel, concat
from datetime import datetime
from dateutil.relativedelta import relativedelta
import warnings

warnings.filterwarnings('ignore')

root_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

Eq_file = os.path.join(root_dir, 'aid', 'Eq.csv')
Eq_lut = loadtxt(Eq_file, delimiter=',')


def cos(x):
    return np_cos(radians(x))


def sin(x):
    return np_sin(radians(x))


def get_Lc(Lg):
    return 4 * (Lg - 120) / 60.


def get_Ct(hour, minute):
    return hour + minute / 60.


def get_Eq(year, month, day):
    index = logical_and(year % 4 == 0, year % 100 == 0)
    index = logical_or(year % 400 == 0, index)
    day[~index] -= 1
    return Eq_lut[day, month]


def get_Tt(Ct, Lc, Eq):
    eq_60 = Eq / 60
    ct_lc = Ct + Lc
    return ct_lc + eq_60


def get_Omiga(Tt):
    return (Tt - 12) * 15


def get_Delta(n):
    return 23.45 * sin(360 / 365 * (284 + n))


def get_EDNI(doy):
    E0 = 1366.1
    EDNI = E0 * (1 + 0.033 * cos(360. / 365 * doy))
    return EDNI


def get_sha_cos(Phi, Delta, Omiga):
    shz_cos_ = cos(Phi) * cos(Delta) * cos(Omiga) + sin(Phi) * sin(Delta)
    return shz_cos_


def get_EHI(edni, sha_cos):
    EHI_ = edni * sha_cos
    EHI_ = array(EHI_)
    EHI_[EHI_ < 0] = 0
    return EHI_


def get_SHA(Phi, Delta, Omiga):
    sha_cos_ = get_sha_cos(Phi, Delta, Omiga)
    sha_radian = arcsin(sha_cos_)
    sha_degree = rad2deg(sha_radian)
    return sha_degree


def get_REHI(ehi, frequency='minute'):
    if len(ehi) <= 1:
        rehi = array(0)
    else:
        if frequency == 'minute':
            rehi = ehi * 60 / 1e6
        elif frequency == 'hour':
            rehi = ehi * 3600 / 1e6
        else:
            raise ValueError('frequency must be minute or hour')
        rehi = cumsum(rehi)
        rehi[1:] = rehi[0:-1]
        rehi[0] = 0.0
    return rehi


def EDNI_EHI_SHA(longitude, latitude, doy, year, month, day, hour, minute):
    Phi = latitude
    Lc_ = get_Lc(longitude)
    Ct_ = get_Ct(hour, minute)
    Eq_ = get_Eq(year, month, day)
    Tt_ = get_Tt(Ct_, Lc_, Eq_)
    Omiga_ = get_Omiga(Tt_)
    Delta_ = get_Delta(doy)
    sha_cos_ = get_sha_cos(Phi, Delta_, Omiga_)
    EDNI_ = get_EDNI(doy)
    EHI_ = get_EHI(EDNI_, sha_cos_)
    SHA_ = get_SHA(Phi, Delta_, Omiga_)
    if DEBUG:
        print(f'Lc_: {Lc_}')
        print(f'Ct_: {Ct_}')
        print(f'Eq_: {Eq_}')
        print(f'Tt_: {Tt_}')
        print(f'Omiga_: {Omiga_}')
        print(f'Delta_: {Delta_}')
        print(f'sha_cos_: {sha_cos_}')
        print(f'EDNI_: {EDNI_}')
        print(f'EHI_: {EHI_}')
        print(f'SHA_: {SHA_}')
    return EDNI_, EHI_, SHA_


def get_datetime(datetime_start, datetime_end, frequency='minute'):
    if frequency == 'minute':
        delta = int((datetime_end - datetime_start).total_seconds() / 60)
    elif frequency == 'hour':
        datetime_start = datetime_start.strftime("%Y%m%d%H")
        datetime_start = datetime.strptime(datetime_start, '%Y%m%d%H')
        datetime_end = datetime_end.strftime("%Y%m%d%H")
        datetime_end = datetime.strptime(datetime_end, '%Y%m%d%H')
        delta = int((datetime_end - datetime_start).total_seconds() / 3600)
    else:
        raise ValueError('frequency must be minute or hour')
    datetimes = ones((delta + 1,), dtype=np_object)
    doy = ones((delta + 1,), dtype=int16)
    year = ones((delta + 1,), dtype=int16)
    month = ones((delta + 1,), dtype=int8)
    day = ones((delta + 1,), dtype=int16)
    hour = ones((delta + 1,), dtype=int8)
    minute = ones((delta + 1,), dtype=int8)
    index = 0
    while datetime_start <= datetime_end:
        datetimes[index] = datetime_start.strftime('%Y%m%d%H%M')
        doy[index] = int(datetime_start.strftime('%j'))
        year[index] = datetime_start.year
        month[index] = datetime_start.month
        day[index] = datetime_start.day
        hour[index] = datetime_start.hour
        minute[index] = datetime_start.minute
        index += 1
        if frequency == 'minute':
            datetime_start += relativedelta(minutes=1)
        elif frequency == 'hour':
            datetime_start += relativedelta(hours=1)
        else:
            raise ValueError('frequency must be minute or hour')
    return datetimes, doy, year, month, day, hour, minute


def format_result(result):
    result['经度'] = result['经度'].map(lambda x: '{:0.2f}'.format(x))
    result['纬度'] = result['纬度'].map(lambda x: '{:0.2f}'.format(x))
    result['太阳高度角'] = result['太阳高度角'].map(lambda x: '{:0.2f}'.format(x))
    result['EDNI（W/m2）'] = result['EDNI（W/m2）'].map(lambda x: '{:0.2f}'.format(x))
    result['EHI（W/m2）'] = result['EHI（W/m2）'].map(lambda x: '{:0.2f}'.format(x))
    result['累积辐照量（MJ/m2）'] = result['累积辐照量（MJ/m2）'].map(lambda x: '{:0.2f}'.format(x))
    result['累积辐照量（kWh/m2）'] = result['累积辐照量（kWh/m2）'].map(lambda x: '{:0.2f}'.format(x))
    return result


def get_start(date):
    d = date.strftime('%Y%m%d')
    return datetime.strptime(d, '%Y%m%d')


def get_end(date):
    d = date.strftime('%Y')
    return datetime.strptime(d + '12312359', '%Y%m%d%H%M')


def get_start_end(date):
    s = get_start(date)
    e = get_end(date)
    return s, e


def get_datetime_start_end(datetime_start, datetime_end):
    starts = list()
    ends = list()
    delta = datetime_end.year - datetime_start.year
    if delta == 0:
        starts.append(datetime_start)
        ends.append(datetime_end)
    elif delta == 1:
        end = get_end(datetime_start)
        starts.append(datetime_start)
        ends.append(end)
        start = get_start(datetime_end)
        starts.append(start)
        ends.append(datetime_end)
    else:
        end = get_end(datetime_start)
        starts.append(datetime_start)
        ends.append(end)
        for i in range(1, delta):
            start, end = get_start_end(datetime_start + relativedelta(years=i))
            starts.append(start)
            ends.append(end)
        start = get_start(datetime_end)
        starts.append(start)
        ends.append(datetime_end)
    return starts, ends


def product_one_point(datetime_start, datetime_end, longitude, latitude, frequency='minute', outfile=None):
    if DEBUG:
        print('--- product_one_point ---：Start')
        print('--- product_one_point <<< datetime_start：{}'.format(datetime_start))
        print('--- product_one_point <<< datetime_end：{}'.format(datetime_end))
        print('--- product_one_point <<< longitude：{}'.format(longitude))
        print('--- product_one_point <<< latitude：{}'.format(latitude))
        print('--- product_one_point <<< frequency：{}'.format(frequency))
        print('--- product_one_point <<< outfile：{}'.format(outfile))
    datetime_start = datetime.strptime(datetime_start, '%Y%m%d%H%M')
    datetime_end = datetime.strptime(datetime_end, '%Y%m%d%H%M')
    # 2020-06-05：增加按年处理累积
    datetime_starts, datetime_ends = get_datetime_start_end(datetime_start, datetime_end)

    results_df = None
    for datetime_now, datetime_util in zip(datetime_starts, datetime_ends):
        datetimes, doy, year, month, day, hour, minute = get_datetime(datetime_now, datetime_util, frequency)

        EDNI_, EHI_, SHA_ = EDNI_EHI_SHA(longitude, latitude, doy, year, month, day, hour, minute)

        longitude_ = full_like(EDNI_, longitude)
        latitude_ = full_like(EDNI_, latitude)
        REHI = get_REHI(EHI_, frequency)
        results = {
            '经度': longitude_,
            '纬度': latitude_,
            '时间': datetimes,
            '太阳高度角': SHA_,
            'EDNI（W/m2）': EDNI_,
            'EHI（W/m2）': EHI_,
            '累积辐照量（MJ/m2）': REHI,
            '累积辐照量（kWh/m2）': REHI / 3.6,
        }
        if results_df is None:
            results_df = DataFrame(results)
        else:
            results_df = concat((results_df, DataFrame(results)))
    if results_df is not None:
        results = format_result(results_df)
        results = results[['经度', '纬度', '时间', '太阳高度角',
                           'EDNI（W/m2）', 'EHI（W/m2）', '累积辐照量（MJ/m2）', '累积辐照量（kWh/m2）']]
        if outfile is not None:
            results.to_csv(outfile, index=False)
            if DEBUG:
                print('--- product_one_point ---：>>>：{}'.format(outfile))
        if DEBUG:
            print('--- product_one_point ---：End')
        return results


def product_multi_point(infile, outfile, frequency='minute'):
    if DEBUG:
        print('--- product_multi_point ---：Start')
        print('--- product_multi_point <<< infile：{}'.format(infile))
        print('--- product_multi_point <<< outfile：{}'.format(outfile))
    indata = read_excel(infile)
    results = None
    for i in indata.values:
        print(i)
        longitude, latitude, datetime_s, datetime_e = i
        datetime_s = str(int(datetime_s))
        datetime_e = str(int(datetime_e))
        longitude = float(longitude)
        latitude = float(latitude)
        result = product_one_point(datetime_s, datetime_e, longitude, latitude, frequency=frequency)
        if result is not None:
            if results is None:
                results = result
            else:
                results = concat((results, result))
    if results is not None:
        results.to_csv(outfile, index=False)
        if DEBUG:
            print('--- product_multi_point ---：>>>：{}'.format(outfile))
    if DEBUG:
        print('--- product_multi_point ---：End')
    return outfile


if __name__ == '__main__':

    # ######################### 业务运行 ###################################
    parser = argparse.ArgumentParser(description='地外太阳能数据生产工具')
    parser.add_argument('--mode', '-r', help='模式: one（单点），multi（多点）')
    parser.add_argument('--frequency', '-f', help='频次: minute（分钟），hour（小时）', default='minute')
    parser.add_argument('--datetime_start', '-s', help='开始时间(北京时)，YYYYmmddHHMM(201901010000)')
    parser.add_argument('--datetime_end', '-e', help='结束时间（北京时），YYYYmmddHHMM(201901010000)')
    parser.add_argument('--longitude', '-g', help='经度，数值')
    parser.add_argument('--latitude', '-t', help='纬度，数值')
    parser.add_argument('--infile', '-i', help='输入文件，绝对路径')
    parser.add_argument('--outfile', '-o', help='输出文件，绝对路径')
    parser.add_argument('--DEBUG', help='是否DEBUG', default=False)
    parser.add_argument('--TEST', help='是否TEST', default=False)
    args = parser.parse_args()

    DEBUG = args.DEBUG
    TEST = args.TEST

    if TEST:
        # test EDNI_EHI_SHA
        print('||| test EDNI_EHI_SHA')
        datetime_test = datetime.strptime('199905011400', '%Y%m%d%H%M')
        doy_test = array(int(datetime_test.strftime('%j')))
        longitude_test = array(116.55)
        latitude_test = array(40.12)
        year_test = array(datetime_test.year)
        month_test = array(datetime_test.month)
        day_test = array(datetime_test.day)
        hour_test = array(datetime_test.hour)
        minute_test = array(datetime_test.minute)
        EDNI_test, EHI_test, SHA_test = EDNI_EHI_SHA(longitude_test, latitude_test, doy_test,
                                                     year_test, month_test, day_test, hour_test, minute_test)
        print(EDNI_test, EHI_test, SHA_test)

        # test product_one_point
        print('||| test product_one_point')
        datetime_s_test = '199901010800'
        datetime_e_test = '199901010800'
        longitude_test = array(116.55)
        latitude_test = array(40.12)
        outfile_test = 'test_out_product_one_point.csv'
        product_one_point(datetime_s_test, datetime_e_test, longitude_test, latitude_test, frequency='minute',
                          outfile=outfile_test)

        print('||| test product_one_point')
        datetime_s_test = '199901010800'
        datetime_e_test = '199901011700'
        longitude_test = array(116.55)
        latitude_test = array(40.12)
        outfile_test = 'test_out_product_one_point2.csv'
        product_one_point(datetime_s_test, datetime_e_test, longitude_test, latitude_test, frequency='minute',
                          outfile=outfile_test)

        # test product_one_point
        print('||| test product_one_point')
        datetime_s_test = '199901010800'
        datetime_e_test = '199901010800'
        longitude_test = array(116.55)
        latitude_test = array(40.12)
        outfile_test = 'test_out_product_one_point3.csv'
        product_one_point(datetime_s_test, datetime_e_test, longitude_test, latitude_test, frequency='hour',
                          outfile=outfile_test)

        print('||| test product_one_point')
        datetime_s_test = '199901010800'
        datetime_e_test = '199901011700'
        longitude_test = array(116.55)
        latitude_test = array(40.12)
        outfile_test = 'test_out_product_one_point4.csv'
        product_one_point(datetime_s_test, datetime_e_test, longitude_test, latitude_test, frequency='hour',
                          outfile=outfile_test)

        # test product_multi_point
        print('||| test product_multi_point')
        infile_test = 'test_in_product_multi_point.xls'
        outfile_test = 'test_out_product_multi_point_minute.csv'
        result_test = product_multi_point(infile_test, outfile_test)
        print(result_test)

        # test product_multi_point
        print('||| test product_multi_point')
        infile_test = 'test_in_product_multi_point.xls'
        outfile_test = 'test_out_product_multi_point_hour.csv'
        result_test = product_multi_point(infile_test, outfile_test, frequency='hour')
        print(result_test)

    mode = args.mode
    freq = args.frequency.lower()
    if args.mode == 'one':
        longi = array(float(args.longitude))
        lati = array(float(args.latitude))
        resu = product_one_point(args.datetime_start, args.datetime_end, longi, lati, freq, args.outfile)
        if resu is not None:
            sys.exit(0)
        else:
            sys.exit(-1)
    elif args.mode == 'multi':
        resu = product_multi_point(args.infile, args.outfile, frequency=freq)
        if resu is not None:
            sys.exit(0)
        else:
            sys.exit(-1)
    else:
        parser.print_help()
        sys.exit(-1)
