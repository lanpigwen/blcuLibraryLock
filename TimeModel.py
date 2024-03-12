from datetime import datetime, timedelta
import time as Time


def timeOffset(hour,minute):
    """
    预约 hour小时+minute分钟后的座位
    """
    minute=minute+(5 - minute % 5) % 5

    # 获取当前时间
    current_time = datetime.now()

    # 计算分钟的偏移，使其成为5的倍数
    minutes_offset = (5 - current_time.minute % 5) % 5+minute

    # 计算秒数的偏移，使其为0
    seconds_offset = -current_time.second

    # 计算小时的偏移，使其加1
    hours_offset = hour

    # 使用 timedelta 进行时间偏移
    offset = timedelta(minutes=minutes_offset, seconds=seconds_offset, hours=hours_offset)
    adjusted_time = current_time + offset

    return adjusted_time

def resvTime(hour,minute):
    """
    预约 hour小时+minute分钟后的座位
    """
    adjusted_time=timeOffset(hour,minute)
    #判断是否在7-21
    if adjusted_time.hour<7:
        return adjusted_time.replace(hour=7, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
    elif adjusted_time.hour>=21:
        return adjusted_time.replace(hour=21, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
    return adjusted_time.strftime('%Y-%m-%d %H:%M:%S')

def endTime(hour,minute,h=22,m=0,s=0):
    """
    始终为当天的h:m:s
    """
    adjusted_time=timeOffset(hour,minute)
    return adjusted_time.replace(hour=h, minute=m, second=s).strftime('%Y-%m-%d %H:%M:%S')

def first_end_date():
    current_date = datetime.now().date()

    # 获取本月第一天
    first_day = datetime(current_date.year, current_date.month, 1)
    if current_date.month==12:
        last_day = datetime(current_date.year + 1, 1, 1) - timedelta(days=1)
    else:
    # print((current_date.month + 1)%13)
    # 计算下个月的第一天，然后减去一天得到本月最后一天
        last_day = datetime(current_date.year, current_date.month + 1, 1) - timedelta(days=1)

    # 将日期格式化为字符串
    formatted_first_day = first_day.strftime('%Y-%m-%d')
    formatted_last_day = last_day.strftime('%Y-%m-%d')
    return formatted_first_day,formatted_last_day

def over1h(time_str1,time_str2):


    # 将字符串转换为 datetime 对象
    time1 = datetime.strptime(time_str1, '%Y-%m-%d %H:%M:%S')
    time2 = datetime.strptime(time_str2, '%Y-%m-%d %H:%M:%S')

    # 计算时间差
    time_difference = time2 - time1

    # 比较时间差是否大于1小时
    if time1<time2 and time_difference > timedelta(hours=1) and time1.hour>=7:
        # print("时间差大于1小时")
        return 1
    else:
        return 0
    
def s2date(time_stamp):
    time_struct = Time.localtime(time_stamp)    # 首先把时间戳转换为结构化时间
    time_format = Time.strftime("%Y-%m-%d %H-%M-%S",time_struct)
    return time_format

