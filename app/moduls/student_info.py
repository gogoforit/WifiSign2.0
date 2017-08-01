from mongoengine import *


class StudentInfo(Document):
    _id = StringField()
    name = StringField(required=True)
    student_id = StringField(required=True)
    class_id = StringField(required=True)
    address_mac = StringField(required=True)
    connect_time = StringField(required=True)
    break_time = StringField(required=True)
    status = StringField(required=True)
    date = StringField(required=True)
    remarks = StringField(required=True)
    meta = {'db_alias': 'local_db', 'collection': 'student_info_remote'}