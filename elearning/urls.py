"""elearning URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.conf.urls import include, url
# from xadmin.plugins import xversion
# import xadmin

from django.views.generic import TemplateView
from users import views
from users.views import LoginView,RegisterView

from course.views import indexView
from course.views import dashboardView
from course.views import courseRead_new,Sentence,lessonRead,WordRead
from course.views import GeneratedSentences
import course 


from django.conf import settings  
from django.conf.urls.static import static  
#version模組自動註冊需要版本控制的 Model
# xversion.register_models()

# xadmin.autodiscover()

admin.autodiscover()


urlpatterns = [
    # url('xadmin/', xadmin.site.urls),
    path('admin/', admin.site.urls),

    # path('', TemplateView.as_view(template_name='index.1.html'),name='index1'),
    # path('index.html', TemplateView.as_view(template_name='index.html'),name='index'),
    path('', indexView.as_view(),name='index'),
    path('index', indexView.as_view(),name='index'),
    path('index.html', indexView.as_view(),name='index'),


    url(r'^ajax_index/$', course.views.ajax_index, name='ajax_index'),


    path('login/',LoginView.as_view(),name = 'login'),
    path('login.html/',LoginView.as_view(),name = 'login'),

    path('register/',RegisterView.as_view(),name = 'register'),
    path('register.html/',RegisterView.as_view(),name = 'register'),

    # path('dashboard', TemplateView.as_view(template_name='dashboard.html'),name='dashboard'),
    # path('dashboard.html', TemplateView.as_view(template_name='dashboard.html'),name='dashboard'),

    path('dashboard', dashboardView,name='dashboard'),
    path('dashboard/courseRead_new/<int:courseId>/', courseRead_new,name='courseRead_new'),
    # path('dashboard/Sentence/<int:courseId>/', Sentence,name='Sentence'),
    path('dashboard/Sentence/<int:lessonId>/', Sentence,name='Sentence'),
    path('dashboard/WordRead/<int:WordsId>/', WordRead,name='WordRead'),

    path('dashboard/lessonRead/<int:lessonId>/', lessonRead,name='lessonRead'),

    
    path('dashboard/GeneratedSentences', GeneratedSentences, name='GeneratedSentences'),



    path('course/', include('course.urls', namespace='course')),
    path('users/', include('users.urls', namespace='users')),

    path('starter', TemplateView.as_view(template_name='starter.html'),name='starter'),
    path('sbadmin2', TemplateView.as_view(template_name='sbadmin2.html'),name='sbadmin2'),

    
    


]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# path('admin/', admin.site.urls),

admin.site.site_title = 'NUTC ELEARNING'
admin.site.site_header = 'NUTC ELEARNING'
admin.site.index_title = 'NUTC ELEARNING'
