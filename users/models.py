# users/models.py

from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe


import os
from uuid import uuid4

from django.utils.deconstruct import deconstructible

@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(str(instance.pk) + str(uuid4().hex), ext)
        # return the whole path to the file
        return os.path.join(self.path, filename.lower())

path_and_rename = PathAndRename("user_img")

class UserProfile(AbstractUser):
    # 1. 姓名
    # 2. 科系
    # 3. 年級
    # 4. 學號
    # 5. 生日
    # 6. 性別
    # 7. 手機
    # 8. 信箱
    # 9. 頭貼

    gender_choices = (
        ('男','男'),
        ('女','女')
    )
    department_choices= (
        ('應用英語', '應用英語'),
        ('應用日語', '應用日語'),
        ('應用中文', '應用中文'),
        ('資訊工程', '資訊工程'),
        ('資訊管理', '資訊管理'),
        ('護理', '護理'),
    )
    grade_choices=(
        ('一年級','一年級'),
        ('二年級','二年級'),
        ('三年級','三年級'),
        ('四年級','四年級'),
        ('五年級','五年級'),
    )
    
    
    # def path_and_rename(path):
    #     def wrapper(instance, filename):
    #         ext = filename.split('.')[-1]
    #         # get filename
    #         filename = '{}.{}'.format(str(instance.pk) + str(uuid4().hex), ext)
    #         # filename = '{}.{}'.format(uuid4().hex, ext)
    #         # if instance.pk:
    #         #     filename = '{}.{}'.format(instance.pk, ext)
    #         # else:
    #         #     # set filename as random string
    #         #     filename = '{}.{}'.format(str(instance.pk) + str(uuid4().hex), ext)
    #         # # return the whole path to the file
    #         return os.path.join(path, filename.lower())
    #     return wrapper

    department = models.CharField('科系',max_length=10,choices=department_choices,default=1,null=True)
    grade = models.CharField('年級',max_length=10,choices=grade_choices,default=1,null=True)
    student_ID = models.CharField('學號',max_length=11,null=True)
    birthday = models.DateField('生日',null=True,blank=True)
    gender = models.CharField('性別',max_length=10,choices=gender_choices,default='男')
    mobile = models.CharField('手機號碼',max_length=11,null=True,blank=True)
    email = models.EmailField('信箱',max_length=50)
    image = models.ImageField(upload_to=path_and_rename,default='/img/hs.jpg',max_length=100,blank=True,null=True)
    

    # def image_tag(self):
    #     return mark_safe('<img src="/upload%s" width="150" height="150" />' % (self.image))

    # image_tag.short_description = 'Image'

    class Meta:
        verbose_name = '學生名單'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    


# class EmailVerifyRecord(models.Model):
#     send_choices = (
#         ('register','註冊'),
#         ('forget','找回密碼'),
#         ('update_email','修改信箱')
#     )

#     code = models.CharField('驗證碼',max_length=20)
#     email = models.EmailField('信箱',max_length=50)
#     send_type = models.CharField(choices=send_choices,max_length=30)
#     send_time = models.DateTimeField(default=datetime.now)


# class Banner(models.Model):
#     title = models.CharField('標題',max_length=100)
#     image = models.ImageField('輪播圖',upload_to='banner/%Y%m',max_length=100)
#     url = models.URLField('訪問地址',max_length=200)
#     index = models.IntegerField('順序',default=100)
#     add_time = models.DateTimeField('添加時間',default=datetime.now)

#     class Meta:
#         verbose_name = '輪播圖'
#         verbose_name_plural = verbose_name