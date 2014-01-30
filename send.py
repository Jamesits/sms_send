# -*- coding=utf-8 -*-

import os
import re
import time

adb_path = r"C:\Users\zhj\Desktop\adb\adb.exe"
num = "+8613165917133"
msg = u"测试一下 "
file_encode = "utf8"
filename = "contant2.txt"
num_list = []

def solve_offline():
    os.popen(adb_path + " kill-server")
    os.popen(adb_path + " start-server")
    os.popen(adb_path + " remount")

def if_online():
    
    dstatus = os.popen(adb_path + " devices").read()
#p = re.compile('(.*)\toffline')
    if re.search('(.*)\toffline', dstatus):
        return 0
    else:
        return 1


def send(num, msg):

    str1 = adb_path + ' shell am start -n com.llinteger.adb_sms/com.llinteger.adb_sms.MainActivity -e target_num ' + num + ' -e msg_body "' + msg.encode("utf-8") + '\n"'
    print os.popen(str1).read()
    #time.sleep(1)
    #print os.popen(str2).read()

def send_sure(num, msg):
    if if_online()==0:
        print "Device offline. Trying to reconnect..."
        solve_offline()
        while if_online()==0:
            print "Device offline. Please unplug the device and plug it again, then press enter."
            raw_input()
    #print "Send(fake)"
    send(num, msg)
    print "Message sent | Number:" + num +" | Context:" + msg
    time.sleep(1)

if __name__ == "__main__":
    print "============= Message Sender =============="
    print "Plug in your device, unlock it and press enter to continue."
    raw_input()
    if if_online()==0:
        print "Device offline. Trying to reconnect..."
        solve_offline()
        while if_online()==0:
            print "Device offline. Please unplug the device and plug it again, then press enter. If the problem occurs frequently, change a USB Port."
            raw_input()

    print "Now sending..."

    for line in open(filename):
        l = line.decode(file_encode)
        result = re.findall(r"(1\d{10}),", l)
        for num in result:
            num_list.append(num)

    for i in num_list:
        print i
        
    send_sure("13165917133", u"朱焕杰祝您新年快乐！")


#adb shell "su kill $(ps | busybox grep com.llinteger.adb_sms | busybox tr -s ' ' | busybox cut -d ' ' -f2)"
