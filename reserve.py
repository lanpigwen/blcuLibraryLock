from checkVersion import checkV


import smtplib
from email.mime.text import MIMEText

import logging
import traceback


def sendEmail(receiver, content):
    mail_host = 'smtp.163.com'
    mail_user = 'blcu_access_system'
    mail_pass = 'NYVBABPKROUMRMMO'
    sender = 'blcu_access_system@163.com'

    message = MIMEText(content, 'plain', 'utf-8')
    message['Subject'] = '系统通知'
    message['From'] = sender
    message['To'] = receiver

    try:
        smtpObj = smtplib.SMTP(mail_host)
        # 如果需要，使用STARTTLS
        # smtpObj.starttls()
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receiver, message.as_string())
        smtpObj.quit()
        return 'success'
    except smtplib.SMTPException as e:
        return 'error', e

import atexit

def sendEmalibeforeExit(to_who,content):
    # 保存数据的逻辑
    sendEmail(to_who,content)
    # print("正在保存数据...")



from datetime import datetime, timedelta,time
import time as Time
import sys

def timeOffset(hour=1,minute=0):
    """
    预约 hour小时+minute分钟后的座位
    """
    minute=minute+(5 - minute % 5) % 5
    # print(minute)

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


def resvTime(hour=1,minute=0):
    """
    预约 hour小时+minute分钟后的座位
    """
    adjusted_time=timeOffset(hour,minute)
    return adjusted_time.strftime('%Y-%m-%d %H:%M:%S')

def endTime(hour=1,minute=0,h=22,m=0,s=0):
    """
    始终为当天的h:m:s
    """
    adjusted_time=timeOffset(hour,minute)
    return adjusted_time.replace(hour=h, minute=m, second=s).strftime('%Y-%m-%d %H:%M:%S')


def first_end_date():
    current_date = datetime.now().date()

    # 获取本月第一天
    first_day = datetime(current_date.year, current_date.month, 1)

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


import requests
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import json
import os

from selenium.webdriver.chrome.service import Service

current_directory = os.getcwd()
chrome_driver_path = os.path.join(current_directory, 'chromedriver.exe')

#使用selenium获得cookie,token,返回可供post和get操作的session对象  session.post.....session.get.....
def loginReturnSession(my_username,my_password):
    options = webdriver.ChromeOptions()
    s= Service(chrome_driver_path)
    options.add_argument('headless')#不跳出来
    options.add_argument("--disable-gpu")  # 关闭硬件加速，不然会闪屏
    driver = webdriver.Edge(options=options,service=s)
    driver.get("http://libkjyy.blcu.edu.cn/mobile.html#/login")

    WAIT = WebDriverWait(driver, 5)
    username = WAIT.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/div/div[2]/div[1]/div/div[1]/div[2]/input')))
    password = WAIT.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/div/div[2]/div[1]/div/div[2]/div[2]/input')))
    submit = WAIT.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div/div/div/div[2]/div[1]/button')))

    username.send_keys(my_username)
    password.send_keys(my_password)
    submit.click()

    # 获取cookies
    cookies = driver.get_cookies()
    time.sleep(1)
    token = driver.execute_script('return sessionStorage.getItem("vuex");')
    useInfo=json.loads(token)['userInfo']
    #获取登录者信息
    token=useInfo['token']
    accNo=useInfo['accNo']
    # uuid=useInfo['uuid']#用户的uuid


    # 把cookie信息加到session中
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # 设置请求头，包含token
    headers = {
        'Authorization': f'Bearer {token}',  # 这里根据实际情况设置Authorization头
        "Content-Type":"application/json",
    }

    # 将headers添加到Session中
    session.headers.update(headers)

    return session,cookies,token,accNo

def printInfo(response):
    resvInfo=response
    resvBegin=''
    resvEnd=''
    resvName=''
    resvDevInfoList=[]
    data=resvInfo['data']
    if data!=None:
        resvName=data['resvName']
        resvDevInfoList=data['resvDevInfoList'][0]
        resvBegin=str(data['resvBeginTime'])[:10]
        resvBegin=s2date(int(resvBegin))
        resvEnd=str(data['resvEndTime'])[:10]
        resvEnd=s2date(int(resvEnd))
    try:
        print(resvDevInfoList['roomName'],resvDevInfoList['devName'],resvBegin,resvEnd,resvName,"",sep='  ') 
        logging.info("%s %s %s %s %s",resvDevInfoList['roomName'],resvDevInfoList['devName'],resvBegin,resvEnd,resvName)
    except:pass

#获取预约信息
def getResvInfo(session):

    #获取预约信息 看是否有预约
    rInfoUrl = 'http://libkjyy.blcu.edu.cn/ic-web/reserve/resvInfo'

    firstD,endD=first_end_date()

    resvInfoPayload = {
        'needStatus': '8454',
        'unneedStatus': '128',
        'beginDate': firstD,
        'endDate': endD
    }

    response = session.get(rInfoUrl, params=resvInfoPayload)
    resvInfo=json.loads(response.text)
    resvId=''
    resvStatus=''
    resvBegin=''
    resvEnd=''
    resvName=''
    uuid=''
    resvDevInfoList=[]
    if resvInfo['count']==1:
        data=resvInfo['data'][0]
        uuid=data['uuid']#预约的uuid
        resvName=data['resvName']
        resvDevInfoList=data['resvDevInfoList'][0]
        resvId=data['resvId']
        resvStatus=data['resvStatus']
        resvBegin=str(data['resvBeginTime'])[:10]
        resvBegin=s2date(int(resvBegin))
        resvEnd=str(data['resvEndTime'])[:10]
        resvEnd=s2date(int(resvEnd))
    else:
        resvStatus=0

    return uuid,resvId,resvStatus,resvBegin,resvEnd,resvName,resvDevInfoList
    

#暂离
def templateLeave(session,resvId):
    turl='http://libkjyy.blcu.edu.cn/ic-web/seatOperation/tempLeave'

    tlPayload = {
    "resvId":resvId
    }

    response = session.post(turl,json=tlPayload)#必须用json传，因为请求头的content-type  是 application/json

    print(response.text)
    logging.info(response.text)


#取消预约
def cancelResv(session,uuid):
    durl='http://libkjyy.blcu.edu.cn/ic-web/reserve/delete'
    dlPayload = {
    "uuid":uuid
    }
    response = session.post(durl,json=dlPayload)#必须用json传，因为请求头的content-type  是 application/json
    response=json.loads(response.text)
    return response


#获取座位号
def findDeskNum(session,floorId=100455435,deskId='1C044'):
    roomurl='http://libkjyy.blcu.edu.cn/ic-web/reserve'

    resvDates=datetime.now().date().strftime('%Y%m%d')
    roomPayload = {
    "roomIds": floorId,#一楼C区
    "resvDates": resvDates,
    "sysKind": 8,
    }

    response = session.get(roomurl, params=roomPayload)
    seatData=json.loads(response.text)['data']
    resvDev=''
    for i in seatData:
        if i['devName']==deskId:
            resvDev=i['devId']
            break
    return resvDev


#预约
def resvDesk(session,accNo,resvDev,hour=1,minute=0):
    resvBeginTime=resvTime(hour,minute)
    resvEndTime=endTime(hour,minute)

    if over1h(resvBeginTime,resvEndTime)==0:
        #时间差不足1小时 或 开始时间早于7:00
        # print("时间差不足1小时 或 开始时间早于7:00")
        #可以预约明天的了7:00:00
        resvBeginTime=endTime(8,0,h=7,m=0,s=0)
        resvEndTime=endTime(8,0,h=22,m=0,s=0)
    # print(resvBeginTime,resvEndTime)

    
    rurl='http://libkjyy.blcu.edu.cn/ic-web/reserve'

    resvPayload={
        "appAccNo": accNo,#登录时的usr
        "memberKind":1,
        "resvBeginTime":resvBeginTime,
        "resvDev":[resvDev],  
        "resvEndTime":resvEndTime,
        "resvMember":[accNo],
        "resvProperty":0,
        "sysKind":8,
        "testName":""
    }

    # print(resvPayload)
    response=session.post(rurl,json=resvPayload)
    response=json.loads(response.text)

    return response


#提前离开
def endAhead(session,uuid):
    endAheahUrl='http://libkjyy.blcu.edu.cn/ic-web/reserve/endAhaed'
    endAheahPayload={
        "uuid":uuid
    }
    response = session.post(endAheahUrl,json=endAheahPayload)
    response=json.loads(response.text)

    return response



def AutoLockDesk(userConfig):
    """
    逻辑为：先查看有无预约信息，若有预约信息且还不能签到，则查看预约的开始时间，sleep直到状态变为1029 可签到，
    若没有预约信息，则新建预约
    若使用中/暂离中，则删除该次使用
    回到while第一句
    """
    while(1):
        session,cookies,token,accNo=loginReturnSession(userConfig['username'],userConfig['password'])
        uuid,resvId,resvStatus,resvBegin,resvEnd,resvName,resvDevInfoList=getResvInfo(session)
        resvDev=findDeskNum(session,floorId=userConfig['floorId'],deskId=userConfig['deskId'])
        cancelOffTime=userConfig['cancelOffTime']
        cancelOffset = timedelta(minutes=cancelOffTime)
        transStatus={
            '1093':"正在使用中",
            '3141':"正在暂离中",
            '1027':"预约中(未到签到时间)",
            '1029':"预约中(可签到)",
            '0':"没有预约信息"
        }
        resvStatus=str(resvStatus)
        print("【预约状态】: ",transStatus[resvStatus],end='  ')
        logging.info("【预约状态】: %s",transStatus[resvStatus])

        afterSleep=False
        if resvStatus=='1027':
            uuid,resvId,resvStatus,resvBegin,resvEnd,resvName,resvDevInfoList=getResvInfo(session)
            print()
            print("【预约信息】:",resvDevInfoList['roomName'],resvDevInfoList['devName'],resvBegin,resvEnd,resvName,"",sep='  ')
            logging.info("【预约信息】: %s %s %s %s %s",resvDevInfoList['roomName'],resvDevInfoList['devName'],resvBegin,resvEnd,resvName)

            time1 = datetime.now()
            time2 = datetime.strptime(resvBegin, '%Y-%m-%d %H-%M-%S')
            # print(time2)
            cancelTime=time2+cancelOffset
            #早上只能预约7点以后的
            if cancelTime<cancelTime.replace(hour=7, minute=0, second=0):
                cancelTime=cancelTime.replace(hour=7, minute=0, second=0)
            # print("取消时间应为 ",cancelTime)
            time_difference=cancelTime-time1
            timeLength=int(time_difference.total_seconds())
            #应对系统更新，闸机会自动签到
            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 将于 {cancelTime} 重新预约...请勿关闭窗口(结束运行请按 Ctrl + c)...')
            logging.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 将于 {cancelTime} 重新预约...请勿关闭窗口(结束运行请按 Ctrl + c)...')
            try:
                time.sleep(timeLength)
                afterSleep=True
                # print("sleep了",timeLength/60,"分钟")
            except KeyboardInterrupt:
                print(' 是否需要取消已有预约？是(y) 否(n)')
                deleteResv=input()
                logging.info(' 是否需要取消已有预约？是(y) 否(n)---%s',deleteResv)
                if deleteResv=='y':
                    endAhead(session,uuid)
                    responese=cancelResv(session,uuid)
                    print(responese['message'])
                    logging.info(responese['message'])
                return
                # pass
        if resvStatus=='0':
            response=resvDesk(session,accNo,resvDev,userConfig['h'],userConfig['m'])
            print(response['message'])
            print("【新的预约】: ",end='')
            printInfo(response)
            logging.info(response['message'])
            logging.info("【新的预约】: ")
            logging.info(response)

        elif afterSleep or resvStatus=='1093' or resvStatus=='3141' or resvStatus=='1029':
            endAhead(session,uuid)
            time.sleep(1)
            cancelResv(session,uuid)
            time.sleep(1)





room={
    "1A":100455319,
    "1B":100455433,
    "1C":100455435,
    "2A":100455437,
    "2B":100455439,
    "2C":100455441,
    "2D":100455443,
    "3A":100455445,
    "3B":100455447,
    "4A":100455449,
    "4B":100455451,
    "4C":100455453,
    "4D":100455455,
    "5A":100455457,
    "5B":100455459,
    "5C":100455461,
    "5D":100455463
}

import ctypes

def main():

    # 定义常量
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    # 阻止电脑休眠
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
    #如果电脑休眠，就会导致时间不对
    print("""
————————————————————————————————————————————————————————————————————————————————————————————
    username        学号 
    password        数字北语账号的密码 
    floorId         几层几区(例如: 1A) 
    deskId          座位号(例如: 1A001) 
    h               预约当前时间几个小时后开始 
    m               或者多少分钟后开始 
    mail            输入邮箱号 用于提醒意外退出
————————————————————————————————————————————————————————————————————————————————————————————
【注意事项】:电脑下载Chrome浏览器，且保持版本和reserve.exe同目录下的chromedriver.exe版本一致
【注意事项】:https://registry.npmmirror.com/binary.html?path=chromedriver/ 可获取相应版本的chromedriver.exe    
【注意事项】:请连接校园网使用！！！      
""")
    # print(len(sys.argv))
    # 将命令行参数转为字典

    checkV(chrome_driver_path)
    if len(sys.argv)<7:
        userConfig = {
        'username': input("输入学号: "),
        'password': input("输入密码: "),
        'floorId': room[input("输入楼层区号(如1A): ")],
        'deskId': input("输入座位号(如1A001): "),
        'h': int(input("输入小时偏移量: ")),
        'm': int(input("输入分钟偏移量: ")),
        'mail':input("输入邮箱(也可以不输入)"),
        'cancelOffTime':-12
        }        
    else:
        # print(sys.argv)
        userConfig = {
            'username': sys.argv[1],
            'password': sys.argv[2],
            'floorId': room[sys.argv[3]],
            'deskId': sys.argv[4],
            'h': int(sys.argv[5]),
            'm': int(sys.argv[6]),
            'mail':sys.argv[7] if len(sys.argv)>7 else "xx@x.com",
            'cancelOffTime' : int(sys.argv[8]) if len(sys.argv)>8 else -12,
        }
    logging.basicConfig(format='%(asctime)s -  %(message)s',
                    level=logging.INFO,
                    filename=userConfig['username']+'.log',
                    filemode='a')
    atexit.register(sendEmalibeforeExit,userConfig['mail'],'你已经退出系统，请注意不要违约！')#退出时发送邮件提醒
    try:
        logging.info('————————————————————————————————————————————————————————————————————————————————————————')
        AutoLockDesk(userConfig)
    except:
        logging.error(str(traceback.format_exc()))

if __name__ == "__main__":
    main()


#C:\Users\78381\Desktop\图书馆预约\newblcuLib\app.ico
#pyinstaller -i C:\Users\78381\Desktop\图书馆预约\newblcuLib\app.ico -F -D reserve.py
