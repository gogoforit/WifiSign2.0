import datetime
import time
import os
from mongoengine import *
from mongoengine.context_managers import switch_db
from app.moduls.student import Student
from app.moduls.student_info import StudentInfo


local_username = os.environ['LOCAL_USERNAME']
local_password = os.environ['LOCAL_PASSWORD']
local_host = os.environ['LOCAL_HOST']
local_db = os.environ['LOCAL_DB']
remote_username = os.environ['REMOTE_USERNAME']
remote_password = os.environ['REMOTE_PASSWORD']
remote_host = os.environ['REMOTE_HOST']
remote_db = os.environ['REMOTE_DB']
class_id = os.environ['CLASS_ID']


connect(db=local_db,
        host=local_host,
        username=local_username,
        password=local_password,
        alias='local_db')
connect(db=remote_db,
        host=remote_host,
        username=remote_username,
        password=remote_password,
        alias='remote_db')


def get_macs():
    pid = get_pid()  # 获取ap热点的pid
    mycommand = "create_ap --list-clients " + pid  # 构造查询这个ap热点的命令
    info = os.popen(mycommand)
    info = info.read()
    info = info.split('\n')
    macs = []
    for each in info:
        theinfo = each.split(' ')
        for each2 in theinfo:
            if ':' in each2:
                each2 = each2.replace(':', '-')
                mac = each2
                macs.append(mac)
    return macs

def get_pid():
    k = os.popen("create_ap  --list-running")
    k = k.read()
    k = k.split('\n')
    k = k[2].split(' ')
    pid = k[0]
    return pid

def get_date():
    today_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    return today_date

def get_now_datetime():
    now_hour = time.strftime('%H')
    now_min = time.strftime('%M')
    now_sec = time.strftime('%S')
    now_time = datetime.time(int(now_hour), int(now_min), int(now_sec))
    return now_time

def get_now_time():
    now_time = time.strftime('%H:%M:%S')
    return now_time

def get_class_num():
    now_time = get_now_datetime()
    info = {}
    class_time_start_1 = datetime.time(8, 0, 0)
    class_time_end_1 = datetime.time(10, 0, 0)
    class_time_start_2 = datetime.time(10, 5, 0)
    class_time_end_2 = datetime.time(12, 0, 0)
    class_time_start_3 = datetime.time(14, 30, 0)
    class_time_end_3 = datetime.time(16, 0, 0)
    class_time_start_4 = datetime.time(16, 0, 0)
    class_time_end_4 = datetime.time(18, 0, 0)
    if now_time > class_time_start_1 and now_time < class_time_end_1:
        info['start_time'] = '8'
        info['class_num'] = '1'
    elif now_time > class_time_start_2 and now_time < class_time_end_2:
        info['start_time'] = '10'
        info['class_num'] = '2'
    elif now_time > class_time_start_3 and now_time < class_time_end_3:
        info['start_time'] = '14'
        info['class_num'] = '3'
    elif now_time > class_time_start_4 and now_time < class_time_end_4:
        info['start_time'] = '16'
        info['class_num'] = '4'
    else:
        info['start_time'] = time.strftime('%H')
        info['class_num'] = '5'
    return info

if __name__ == '__main__':
    while True:
        students_connect_info = {}  # 所有学生的签到信息

        with switch_db(Student, 'local_db') as Student:
            students = Student.objects(class_id=class_id)
            for student in students:
                student_connect_info = {}  # 单个学生签到信息
                student_address_mac = student['address_mac']
                student_name = student['name']
                student_id = student['student_id']
                student_connect_info['student_id'] = student_id
                student_connect_info['name'] = student_name
                student_connect_info['class_id'] = class_id
                student_connect_info['address_mac'] = student_address_mac
                student_connect_info['status'] = '0'
                students_connect_info[student_address_mac] = student_connect_info

        macs = get_macs()
        class_num_and_start_time = get_class_num()
        class_num = class_num_and_start_time['class_num']
        start_time = class_num_and_start_time['start_time']
        today_date = get_date()
        now_time = get_now_time()
        _id = ''.join([today_date, '/', class_num])

        with switch_db(StudentInfo, 'remote_db') as StudentInfo:
            for mac in macs:
                if mac in students_connect_info:
                    __id = ''.join([_id, '/', mac])
                    students_connect_info[mac]['status'] = '1'
                    if StudentInfo.objects(_id=__id):
                        student = StudentInfo.objects(_id=__id).first()
                        student.break_time = now_time
                        student.status = '1'
                        student.save()
                    else:
                        student_info_remote = StudentInfo(name=students_connect_info[mac]['name'],
                                                          student_id=students_connect_info[mac]['student_id'],
                                                          class_id=students_connect_info[mac]['class_id'],
                                                          address_mac=students_connect_info[mac]['address_mac'],
                                                          connect_time=now_time,
                                                          break_time=now_time,
                                                          status='1',
                                                          date=today_date,
                                                          class_num=class_num,
                                                          remarks='hello',
                                                          _id=__id)
                        student_info_remote.save()

            for key in students_connect_info.keys():
                __id = ''.join([today_date, '/', class_num])
                __id = ''.join([_id, '/', key])
                if students_connect_info[key]['status'] == '0':
                    if not StudentInfo.objects(_id=__id):
                        student_info_remote = StudentInfo(name=students_connect_info[key]['name'],
                                                          student_id=students_connect_info[key]['student_id'],
                                                          class_id=students_connect_info[key]['class_id'],
                                                          address_mac=students_connect_info[key]['address_mac'],
                                                          connect_time=now_time,
                                                          break_time=now_time,
                                                          status='0',
                                                          date=today_date,
                                                          class_num=class_num,
                                                          remarks='hello',
                                                          _id=__id)
                        student_info_remote.save()
                    else:
                        student = StudentInfo.objects(_id=__id).first()
                        student.status = '0'
                        student.save()









