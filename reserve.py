from checkVersion import checkV
from MailModel import sendEmalibeforeExit
from TimeModel import resvTime,endTime,first_end_date,s2date
import atexit
import logging
import traceback
import sys
import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
from datetime import datetime, timedelta
import json
import os
import ctypes
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
        print("【新的预约】: ",resvDevInfoList['roomName'],resvDevInfoList['devName'],resvBegin,resvEnd,resvName,"",sep='  ') 
        logging.info("%s %s %s %s %s %s","【新的预约】: ",resvDevInfoList['roomName'],resvDevInfoList['devName'],resvBegin,resvEnd,resvName)
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

    # print(response.text)
    response=json.loads(response.text)
    logging.info('---暂离操作: '+response['message'])
    return response

#取消预约
def cancelResv(session,uuid):
    durl='http://libkjyy.blcu.edu.cn/ic-web/reserve/delete'
    dlPayload = {
    "uuid":uuid
    }
    response = session.post(durl,json=dlPayload)#必须用json传，因为请求头的content-type  是 application/json
    response=json.loads(response.text)
    logging.info('---取消预约操作: '+response['message'])
    return response

#获取座位号
def findDeskNum(session,floorId,deskId):
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
def resvDesk(session,accNo,resvDev,hour,minute):

    resvBeginTime=resvTime(hour,minute)
    resvEndTime=endTime(hour,minute)

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

    response=session.post(rurl,json=resvPayload)
    response=json.loads(response.text)

    logging.info('---预约操作: '+response['message'])
    return response

#提前离开
def endAhead(session,uuid):
    endAheahUrl='http://libkjyy.blcu.edu.cn/ic-web/reserve/endAhaed'
    endAheahPayload={
        "uuid":uuid
    }
    response = session.post(endAheahUrl,json=endAheahPayload)
    response=json.loads(response.text)
    logging.info('---提前离开操作: '+response['message'])
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

        resvStatus=str(resvStatus)
        print("【预约状态】: ",transStatus[resvStatus])
        logging.info("【预约状态】: %s",transStatus[resvStatus])

        afterSleep=False
        if resvStatus=='1027':
            uuid,resvId,resvStatus,resvBegin,resvEnd,resvName,resvDevInfoList=getResvInfo(session)
            print("【预约信息】:",resvDevInfoList['roomName'],resvDevInfoList['devName'],resvBegin,resvEnd,resvName,"",sep='  ')
            logging.info("【预约信息】: %s %s %s %s %s",resvDevInfoList['roomName'],resvDevInfoList['devName'],resvBegin,resvEnd,resvName)

            time1 = datetime.now()
            time2 = datetime.strptime(resvBegin, '%Y-%m-%d %H-%M-%S')
            cancelTime=time2+cancelOffset
            #添加一个如果约的是21点，则offset=0
            if time2.hour==21 or time2.hour==7:
                cancelTime=time2
            #早上只能预约7点以后的
            if cancelTime<cancelTime.replace(hour=7, minute=0, second=0):
                cancelTime=cancelTime.replace(hour=7, minute=0, second=0)
            time_difference=cancelTime-time1
            timeLength=int(time_difference.total_seconds())
            #应对系统更新，闸机会自动签到
            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 将于 {cancelTime} 重新预约...\n请勿关闭窗口(结束运行请按 Ctrl + c)...')
            logging.info(f' 将于 {cancelTime} 重新预约...请勿关闭窗口(结束运行请按 Ctrl + c)...')
            try:
                if timeLength>0:
                    # ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
                    ES_CONTINUOUS = 0x80000000
                    ES_SYSTEM_REQUIRED = 0x00000001
                    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
                    time.sleep(timeLength)
                afterSleep=True
            except KeyboardInterrupt:
                print(' 是否需要取消已有预约？是(y) 否(n)')
                deleteResv=input()
                logging.info(' 是否需要取消已有预约？是(y) 否(n)---%s',deleteResv)
                if deleteResv=='y':
                    endAhead(session,uuid)
                    responese=cancelResv(session,uuid)
                    print(responese['message'])
                return True

        if resvStatus=='0':
            if datetime.now().hour==21:
                input("已经超过21点 无法再预约！！！ Enter退出")
                return
            else:
                response=resvDesk(session,accNo,resvDev,userConfig['h'],userConfig['m'])
                printInfo(response)
        if afterSleep or resvStatus=='1093' or resvStatus=='3141' or resvStatus=='1029':
            endAhead(session,uuid)
            time.sleep(1)
            cancelResv(session,uuid)
            time.sleep(1)

    return False


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

transStatus={
    '1093':"正在使用中",
    '3141':"正在暂离中",
    '1027':"预约中(未到签到时间)",
    '1029':"预约中(可签到)",
    '0':"没有预约信息"
}

def main():

    # 定义常量
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    quitTry=False
    tryTime=1
    # 阻止电脑休眠
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
    # ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)这种会有效的阻止休眠 但是关不了屏幕
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
    while quitTry==False and tryTime<=5:
        try:
            tryTime+=1
            logging.info('————————————————————————————————————————————————————————————————————————————————————————')
            quitTry=AutoLockDesk(userConfig)
            atexit.register(sendEmalibeforeExit,userConfig['mail'],userConfig['username']+'已经退出系统，请注意不要违约！')#退出时发送邮件提醒
        except KeyboardInterrupt:
            quitTry=True
        except:
            logging.error(str(traceback.format_exc()))
            if tryTime==5:
                atexit.register(sendEmalibeforeExit,userConfig['mail'],userConfig['username']+f' 第{tryTime}次错误退出！请及时查看！'+str(traceback.format_exc()))#退出时发送邮件提醒
 

if __name__ == "__main__":
    main()


#C:\Users\78381\Desktop\图书馆预约\newblcuLib\app.ico
#pyinstaller -i C:\Users\78381\Desktop\图书馆预约\newblcuLib\app.ico -F -D reserve.py
