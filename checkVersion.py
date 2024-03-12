import winreg  # 和注册表交互
import re  # 正则模块
import os
import subprocess  # 用于执行cmd命令
import sys
import urllib.request  	# 发送http请求
import urllib.parse  	# 拼接url
import zipfile  		# 操作.zip文件
import requests,json
import shutil

version_re = re.compile(r'^[1-9]\d*\.\d*.\d*')  # 匹配前3位版本号的正则表达式
current_directory = os.getcwd()
chrome_driver_path = os.path.join(current_directory, 'chromedriver.exe')

def getChromeVersion():
    try:
    # 从注册表中获得版本号
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')

        _v, type = winreg.QueryValueEx(key, 'version')

        print('Current Chrome Version: {}'.format(_v)) # 这步打印会在命令行窗口显示

        return version_re.findall(_v)[0]  # 返回前3位版本号

    except WindowsError as e:
        print('check Chrome failed:{}'.format(e))

def getDriverVersion(absPath):
   """
   @param absPath: chromedriver.exe的绝对路径
   """
   cmd = r'{} --version'.format(absPath)  # 拼接成cmd命令
   
   try:
       # 执行cmd命令并接收命令回显
       out, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
       out = out.decode('utf-8')
       	
       _v = out.split(' ')[1] # 拆分回显字符串，获取版本号
       print('Current chromedriver Version:{}'.format(_v))

       return version_re.findall(_v)[0]
   except IndexError as e:
       print('check chromedriver failed:{}'.format(e))
       return 0

def progressFunc(blocknum, blocksize, totalsize):
    '''作回调函数用
    @blocknum: 已经下载的数据块
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
    '''
    percent = 100.0 * blocknum * blocksize / totalsize

    if percent > 100:
        percent = 100
    downsize = blocknum * blocksize

    if downsize >= totalsize:
        downsize = totalsize

    s = "%.2f%%" % (percent) + "====>" + "%.2f" % (downsize / 1024 / 1024) + "M/" + "%.2f" % (totalsize / 1024 / 1024) + "M \r"
    sys.stdout.write(s)
    sys.stdout.flush()

    if percent == 100:
        print('')

def downLoadDriver(save_d,c_v,os_v='win',vlistURL='https://registry.npmmirror.com/-/binary/chromedriver/'):
    highURL={
        '116':"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/win64/chromedriver-win64.zip",
        '117':"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.62/win64/chromedriver-win64.zip",
        '118':"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.3/win64/chromedriver-win64.zip",
        '119':"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/win64/chromedriver-win64.zip",
        '120':"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.28/win64/chromedriver-win64.zip",
        '121':"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6129.0/win64/chromedriver-win64.zip",
        '122':"https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.111/win64/chromedriver-win64.zip"
    }
    os_version={
        'win':"chromedriver_win32.zip",
        'mac':"chromedriver_mac64.zip",
        'mac_ml':"chromedriver_mac64_m1.zip"
    }
    try:
        if int(c_v.split('.')[0])>122:
            print("对于版本大于122.*.*的chrome浏览器：")
            print("请手动前往https://storage.googleapis.com/chrome-for-testing-public/ 下载对应的chromedriver版本")
            keyIN=input()
        elif int(c_v.split('.')[0])>114:
            # print("大于114的版本")
            os_v="chromedriver-win64.zip"
            downUrl=highURL[c_v.split('.')[0]]
        else:
            os_v=os_version[os_v]
            downBaseURL=''
            vlist=requests.get(vlistURL).text
            vlist=json.loads(vlist)
            for i in vlist:
                d_v=i['name'].split('.')
                d_v=d_v[:-1]
                d_v='.'.join(d_v)
                if d_v==c_v:
                    downBaseURL=i['url']
                    break
            downUrl = urllib.parse.urljoin(downBaseURL, os_v) # 拼接出下载路径
    except:
        print("对齐版本失败")
        keyIN=input()

        
    file = os.path.join(save_d, os.path.basename(downUrl))
    print('will saved in {}'.format(file))
    # 开始下载，并显示下载进度(progressFunc)
    urllib.request.urlretrieve(downUrl, file, progressFunc)

    # 下载完成后解压
    zFile = zipfile.ZipFile(file, 'r')
    for fileM in zFile.namelist():
        zFile.extract(fileM, os.path.dirname(file))
    zFile.close()

    if int(c_v.split('.')[0])>114:
        target_dir = 'chromedriver-win64'
        target_path = save_d
            # 移动目录中的文件到与子目录同级
        files_in_subdirectory = os.listdir(os.path.join(target_path, target_dir))
        for file_in_subdirectory in files_in_subdirectory:
            src_path = os.path.join(target_path, target_dir, file_in_subdirectory)
            dest_path = os.path.join(target_path, file_in_subdirectory)
            shutil.move(src_path, dest_path)
        os.rmdir(os.path.join(target_path, target_dir))
    os.remove(file)

def checkV(absPath):
    d_v=getDriverVersion(absPath)
    c_v=getChromeVersion()
    # c_v='104.0.5112'
    if c_v == d_v:
        # 若匹配，在命令行窗口提示下面的信息
        # input('Chrome and chromedriver are matched. Press Enter to exit.')
        print('Chrome and chromedriver 版本一致。')
    else:
        print('Chrome and chromedriver 版本不一致。')
        # 若不匹配，走下面的流程去下载chromedriver
        _v = c_v
        save_d = os.path.dirname(absPath) # 下载文件的保存路径，与chromedriver同级
        downLoadDriver(save_d,_v)

# checkV(chrome_driver_path)