from django.contrib import admin
from course.models import Course, Lesson ,Words
# Register your models here.
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Words)
