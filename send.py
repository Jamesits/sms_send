# -*- coding=utf-8 -*-

##########设置项###################
adb_path = r"adb.exe"            # adb.exe 可执行文件路径
msg = ur"短信内容"                # 短信内容
file_encode = "utf8"             # 文件编码（建议使用 UTF-8）
filename = "contant1.txt"       # 文件路径
#################################

regex = r"(1\d{2}[ -]?\d{4}[ -]?\d{4})," # 匹配用的正则表达式。末尾的逗号是为 CSV 文件优化的，不需要的话可以删掉。
debug = 1       #调试开关
do_not_really_send = 0 #调试：不要真的发送

do_not_install_apk = 1 #调试：不要安装 apk

do_not_uninstall_apk = 1 #调试：不要卸载 apk
sleep_time = 1  #两次发送延时


import os
import re
import time

num_list = []

class SmsError(Exception): pass #通用错误类
class SmsValueError(SmsError): pass #参数错误
class SmsBringToFrontError(SmsError): pass #无法运行，通常是由于屏幕锁定/关闭造成的
class SmsApkNotInstalledError(SmsError): pass #手机客户端未安装

def if_string_in(strRead, strRule):
    '''
检查字符串包含关系
'''
    if len(strRead and strRule)>0:
        return 1
    else:
        return 0

def exec_adb(cmd):
    '''
运行 adb 命令
'''
    st = os.popen(adb_path + " " + cmd).read()
    if debug == 1:
        print "[adb command]" + adb_path + " " + cmd
        print "[adb result]" + st
    return st

def solve_offline():
    '''
    尝试修复 device offline 问题
    '''
    exec_adb("kill-server")
    exec_adb("start-server")
    exec_adb("remount")
    
def if_online(): 
    '''
    检查设备是否为离线状态
    '''
    dstatus = exec_adb("devices")
    if re.search('(.*)\toffline', dstatus):
        return 0
    else:
        return 1

def check_online():
    if if_online()==0:
        print "手机处于离线状态，尝试重启服务……",
        solve_offline()
        while if_online()==0:
            print "失败\n设备仍然处于离线状态。请断开 USB 连接，重新连接手机，然后按下回车键。"
            raw_input()

def send(num, msg):
    '''
    发送短信
    '''
    r = exec_adb('shell am start -n com.llinteger.adb_sms/com.llinteger.adb_sms.MainActivity -e target_num ' + num.encode("utf-8") + ' -e msg_body "' + msg.encode("utf-8") + '\n"')
    if if_string_in(r, r"Warning: Activity not started, its current task has been brought to the front") == 1:
        raise SmsBringToFrontError,r
    elif if_string_in(r, r"Error type 3") == 1:
        raise SmsApkNotInstalledError,r
    elif if_string_in(r, r"Error: Activity not started, unable to resolve Intent") == 1:
        raise SmsValueError,r
    elif if_string_in(r, r'Starting: Intent { cmp=com.llinteger.adb_sms/.MainActivity (has extras) }') == 1:
        return r
    else:
        raise SmsError,r
    

def send_sure(num, msg):
    '''
    包装好的安装手机客户端及发送函数
    '''
    check_online()
    if do_not_uninstall_apk == 0:
        exec_adb("uninstall com.llinteger.adb_sms")
    if do_not_install_apk == 0:
        exec_adb("install sms.apk")
    print "Sending... | Number:" + num +" | Context:" + msg
    try:
        send(num, msg)
    except SmsValueError:
        print "手机号码错误"
    except SmsBringToFrontError:
        print "请解锁手机，在开发者设置中勾选“保持唤醒状态”，然后按 Home 键直到主屏幕显示在手机屏幕上，然后按下回车键。"
        raw_input()
    except SmsApkNotInstalledError:
        print "apk 未安装:"
    except SmsError:
        print "发生未知错误:"
    finally:
        time.sleep(sleep_time)

if __name__ == "__main__":
    print "============= 短信发送脚本 =============="
    print '''
请连接好你的手机，确认开发选项中勾选了“USB 调试”和“保持唤醒状态”两项，确保驱动安装成功。然后请按回车键。
请不要插入多台手机。双卡手机默认使用卡 1 发送。
'''
    raw_input()
    check_online()

    print "读取文件……",
    for line in open(filename):
        l = line.decode(file_encode)
        result = re.findall(regex, l)
        for num in result:
            num_list.append(num.replace(" ","").replace("-",""))

    print "完成\n=======发送列表========"
    for i in num_list:
        print i
    print "总计 " + str(len(num_list)) + " 项。"
    print "按回车键开始发送。"
    raw_input()

    if do_not_really_send == 0:
        for i in num_list:
            send_sure(i, msg)
        if do_not_uninstall_apk == 0:
            exec_adb("uninstall com.llinteger.adb_sms")
    else:
        print "调试模式，发送已取消。"
