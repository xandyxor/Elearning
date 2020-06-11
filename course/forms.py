from django import forms
from course.models import Course
import datetime

class CourseForm(forms.ModelForm):
    name = forms.CharField(label='標題', max_length=128)
    desc = forms.CharField(label='內容', widget=forms.Textarea)
    # image = forms.ImageField(label ="封面圖",upload_to="courses/%Y/%m",max_length=100)
    # is_banner = forms.BooleanField(label ='是否輪播')
    add_time = forms.DateTimeField(label = "添加時間",initial=datetime.datetime.now())

    class Meta:
        model = Course
        # fields = ['name', 'desc','is_banner','add_time']
        fields = ['name', 'desc','add_time']
