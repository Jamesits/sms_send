# -*- coding=utf-8 -*-

##########设置项###################
adb_path = r"adb.exe"            # adb.exe 可执行文件路径
msg = ur"短信内容"                # 短信内容
file_encode = "utf8"             # 文件编码（建议使用 UTF-8）
filename = "contant2.txt"       # 文件路径
#################################

regex = r"(1\d{2}[ -]?\d{4}[ -]?\d{4})," # 匹配用的正则表达式。末尾的逗号是为 CSV 文件优化的，不需要的话可以删掉。
debug = 0       #调试开关
do_not_really_send = 0 #调试：不要真的发送
sleep_time = 1  #两次发送延时


import os
import re
import time

num_list = []

def exec_adb(cmd):
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
    exec_adb('shell am start -n com.llinteger.adb_sms/com.llinteger.adb_sms.MainActivity -e target_num ' + num.encode("utf-8") + ' -e msg_body "' + msg.encode("utf-8") + '\n"')

def send_sure(num, msg):
    '''
    包装好的安装手机客户端及发送函数
    '''
    check_online()
    exec_adb( "uninstall com.llinteger.adb_sms")
    exec_adb( "install sms.apk")
    print "Sending... | Number:" + num +" | Context:" + msg
    send(num, msg)
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
        os.popen(adb_path + "uninstall com.llinteger.adb_sms")
    else:
        print "调试模式，禁止发送。"
