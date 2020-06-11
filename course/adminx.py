# course/adminx.py

import xadmin

from .models import Course, Lesson ,Words
# from organization.models import CourseOrg

class LessonInline(object):
    model = Lesson
    extra = 0


# class CourseResourceInline(object):
#     model = CourseResource
#     extra = 0


# Course的admin管理器
class CourseAdmin(object):
    '''課程'''

    list_display = [ 'name','desc','get_zj_nums','go_to']   #顯示的欄位
    search_fields = ['name', 'desc']             #搜索
    list_filter = [ 'name','desc']    #過濾
    model_icon = 'fa fa-book'            #圖示
    # ordering = ['-click_nums']           #排序
    # readonly_fields = ['click_nums']     #只讀欄位
    exclude = ['fav_nums']               #不顯示的欄位
    # list_editable = ['degree','desc']
    # refresh_times = [3,5]                #自動刷新（裡面是秒數範圍）
    inlines = [LessonInline]    #增加章節和課程資源
    # style_fields = {"detail": "ueditor"}

    def queryset(self):
        # 重載queryset方法，來過濾出我們想要的數據的
        qs = super(CourseAdmin, self).queryset()
        # 只顯示is_banner=True的課程
        # qs = qs.filter(is_banner=False)
        return qs

    def save_models(self):
        # 在保存課程的時候統計課程機構的課程數
        # obj實際是一個course對象
        obj = self.new_obj
        # 如果這裡不保存，新增課程，統計的課程數會少一個
        obj.save()
        # 確定課程的課程機構存在。
        # if obj.course_org is not None:
        #     #找到添加的課程的課程機構
        #     course_org = obj.course_org
        #     #課程機構的課程數量等於添加課程後的數量
        #     course_org.course_nums = Course.objects.filter(course_org=course_org).count()
        #     course_org.save()


# class BannerCourseAdmin(object):
#     '''輪播課程'''

#     list_display = [ 'name','desc']
#     search_fields = ['name', 'desc']
#     list_filter = [ 'name','desc']
#     model_icon = 'fa fa-book'
#     exclude = ['fav_nums']
#     inlines = [LessonInline]

#     def queryset(self):
#         #重載queryset方法，來過濾出我們想要的數據的
#         qs = super(BannerCourseAdmin, self).queryset()
#         #只顯示is_banner=True的課程
#         qs = qs.filter(is_banner=True)
#         return qs

class LessonAdmin(object):
    '''章節'''

    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    #這裡course__name是根據課程名稱過濾
    list_filter = ['course__name', 'name', 'add_time']


# class VideoAdmin(object):
#     '''影片'''

#     list_display = ['lesson', 'name', 'add_time']
#     search_fields = ['lesson', 'name']
#     list_filter = ['lesson', 'name', 'add_time']


# class CourseResourceAdmin(object):
#     '''課程資源'''

#     list_display = ['course', 'name', 'download', 'add_time']
#     search_fields = ['course', 'name', 'download']
#     list_filter = ['course__name', 'name', 'download', 'add_time']


# Words的admin管理器
class WordsAdmin(object):
    '''單字'''

    list_display = [ 'lesson','words','kk','subject','chinese','description','example']   #顯示的欄位
    search_fields = ['words','chinese']             #搜索
    list_filter = [ 'lesson','words','subject']    #過濾
    model_icon = 'fa fa-bold'            #圖示
    # ordering = ['-click_nums']           #排序
    # readonly_fields = ['click_nums']     #只讀欄位
    # exclude = []               #不顯示的欄位
    # list_editable = ['degree','desc']
    # refresh_times = [3,5]                #自動刷新（裡面是秒數範圍）
    # inlines = [LessonInline]    #增加章節和課程資源
    # style_fields = {"detail": "ueditor"}

   

# 將管理器與model進行註冊關聯
xadmin.site.register(Course, CourseAdmin)
# xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)

xadmin.site.register(Words, WordsAdmin)

# xadmin.site.register(Video, VideoAdmin)
# xadmin.site.register(CourseResource, CourseResourceAdmin)