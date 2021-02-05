
"""
根据已有经纬度位置计算太阳天顶角;网上程序
!!!正确的！
"""
import numpy as np
from datetime import datetime
import math
import time

def daynum_in_year(time):
    fmt = '%Y%m%d'
    dt = datetime.strptime(time, fmt)
    tt = dt.timetuple()
    return tt.tm_yday


def jd_to_time(time):
    dt = datetime.strptime(time, '%Y%j').date()
    fmt = '%Y.%m.%d'
    return dt.strftime(fmt)

if '__main__' == __name__:

    dirout = r'E:\work_hym_2020\西北院项目-中期之后\太阳天顶角'
    # sta_info= {'DT' : (113.4167, 40.0833), 'TY':(112.5833, 37.6167), 'HM':(111.3667, 35.6500),'GZ':(113.23, 23.16)}
    sta_info = {'GE':(94.92,36.42),'EJ':(101.07,41.95)}
    # sta_info = {'DT' : (113.4167, 40.0833), 'TY':(112.5833, 37.6167), 'HM':(111.3667, 35.6500)}
    #sta_info = {'ts': (110.0, 23.5)}
    days = [31,28,31,30,31,30,31,31,30,31,30,31]
    TimeZone = 8.
    year_list = [2019]
    for sta_key,geo_info in sta_info.items():

        time_str = []
        sza_str = []
        for year in year_list :
        # year = 2018
            sta_name = sta_key
            sta_lon = geo_info[0]
            sta_lat = geo_info[1]

            #输出

            if sta_lon >= 0:
                if TimeZone == -13:
                    dLon = sta_lon - (math.floor((sta_lon * 10 - 75) / 150) + 1) * 15.0
                else:
                    dLon = sta_lon - TimeZone * 15.0  # 地球上某一点与其所在时区中心的经度差
            else:
                if TimeZone == -13:
                    dLon = (math.floor((sta_lon * 10 - 75) / 150) + 1) * 15.0 - sta_lon
                else:
                    dLon = TimeZone * 15.0 - sta_lon

            for mm in np.arange(1, 13):
                days_mm = days[mm-1]
                for dd in np.arange(1, days_mm+1):
                    yymmdd_str = str(year)+str(mm).zfill(2)+str(dd).zfill(2)

                    #计算是该年的第几天 day of year
                    DOY =daynum_in_year(yymmdd_str)

                    N0 = 79.6764 + 0.2422*(year-1985) - int((year-1985)/4.0)
                    sitar_rd = 2*math.pi*(DOY-N0)/365.2422 #弧度
                    #sitar = math.radians(sitar_deg)
                    sitar = sitar_rd
                    #ED1是度
                    ED1 = 0.3723 + 23.2567*math.sin(sitar) + 0.1149*math.sin(2*sitar) - 0.1712*math.sin(3*sitar)- 0.758*math.cos(sitar) + 0.3656*math.cos(2*sitar) + 0.0201*math.cos(3*sitar)
                    ED = ED1*math.pi/180           #ED本身有符号
                    #ED = ED1
                    #

                    #时差
                    Et = 0.0028 - 1.9857*math.sin(sitar) + 9.9059*math.sin(2*sitar) - 7.0924*math.cos(sitar)- 0.6882*math.cos(2*sitar)
                    for hh in np.arange(0,24):

                            min = 0
                        # for min in np.arange(0,60):
                            a=1
                            yymmddhhmm_str  = yymmdd_str+str(hh).zfill(2)+str(min).zfill(2)

                            gtdt1 = hh + min/60.0 + 0 + dLon/15        #地方时 ；平太阳时
                            gtdt = gtdt1 + Et/60.0  #真太阳时
                            dTimeAngle1 = 15.0*(gtdt-12)
                            dTimeAngle = dTimeAngle1*math.pi/180 #时角τ
                            #dTimeAngle = dTimeAngle1

                            latitude_rd = sta_lat*math.pi/180
                            #latitudeArc = sta_lat

                            HeightAngleArc = math.asin(math.sin(latitude_rd) * math.sin(ED) + math.cos(latitude_rd) \
                                            * math.cos(ED) * math.cos(dTimeAngle))

                            HeightAngle_deg = math.degrees(HeightAngleArc)
                            SZA = 90.0 - HeightAngle_deg
                            fmt = '%Y%m%d%H%M'
                            dt = datetime.strptime(yymmddhhmm_str, fmt)

                            time_str.append(dt)
                            sza_str.append( HeightAngle_deg)
                            # print('日期：%s ,太阳天顶角(deg)：%8.4f ' % (dt,SZA))

        pathout = sta_name +'.txt'
        with open(pathout, "w") as f:
            for time,sza in zip(time_str,sza_str):
                f.write('%s %8.4f %s'%(time,sza,'\n') )
        # pathout = dirout + '\\' + sta_name + '.xlsx'
        # out_dic = {'time': time_str, 'deg': sza_str}
        # out_df = pd.DataFrame(out_dic)
        # # outpath = os.path.join(dirpath, year + '日比较结果.xlsx')
        # out_df.to_excel(pathout, index=False, header=False)
