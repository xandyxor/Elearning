# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login

from django.contrib.auth.backends import ModelBackend
from .models import UserProfile
from django.db.models import Q
from django.views.generic.base import View
from .forms import LoginForm,RegisterForm
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect

from six.moves import urllib
from django.urls import reverse


class Student_IDBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        # if not (username is None):
        #     try:
        #         user = UserProfile.objects.get(username=username)
        #     except UserProfile.DoesNotExist:  # 可以捕获除与程序退出sys.exit()相关之外的所有异常
        #         return None
        #     if user.check_password(password):
        #         return user
        if email is None:
            student_ID = kwargs.get('student_ID')
            if student_ID is None:
                return None
            else:
                try:
                    user = UserProfile.objects.get(student_ID=student_ID)
                except UserProfile.DoesNotExist:
                    return None
        else:
            try:
                user = UserProfile.objects.get(email=email)
            except UserProfile.DoesNotExist:  # 可以捕获除与程序退出sys.exit()相关之外的所有异常
                return None

        if user.check_password(password):
            return user
            
    def get_user(self, user_id):
        try:
            return UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return None

#信箱和使用者名稱都可以登錄
# 基礎ModelBackend類，因為它有authenticate方法

# class CustomBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             # 不希望用戶存在兩個，get只能有一個。兩個是get失敗的一種原因 Q為使用聯集查詢
#             user = UserProfile.objects.get(Q(student_ID=username)|Q(email=username))

#             # django的後台中密碼加密：所以不能password==password
#             # UserProfile繼承的AbstractUser中有def check_password(self, raw_password):
#             if user.check_password(password):
#                 return user
#         except Exception as e:
#             return None


class LoginView(View):
    def get(self,request):
        # return render(request, 'login.html')
        return HttpResponseRedirect('/#login')


    def post(self,request):
        # 實例化
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # 獲取用戶提交的使用者名稱和密碼
            student_ID = request.POST.get('student_ID', None)
            pass_word = request.POST.get('password', None)
            # 成功返回user對象,失敗None
            # user = authenticate(username=user_id_email, password=pass_word)
            user = authenticate(student_ID=student_ID, password=pass_word)

            # 如果不是null說明驗證成功
            if user is not None:
                # 登錄
                login(request, user)
                return render(request, 'index.html')
            # 只有當使用者名稱或密碼不存在時，才返回錯誤訊息到前端
            else:
                return render(request, 'login.html', {'msg': '使用者信箱/學號或密碼錯誤','login_form':login_form})

        # form.is_valid（）已經判斷不合法了，所以這裡不需要再返回錯誤訊息到前端了
        else:
            return render(request,'login.html',{'login_form':login_form})

class RegisterView(View):
    '''用戶註冊'''
    def get(self,request):
        # register_form = RegisterForm()
        # return render(request,'course/index.html',{'register_form':register_form})
        return HttpResponseRedirect('/#register')


    def post(self,request):
        print("RegisterView")

        register_form = RegisterForm(request.POST)
        print(register_form)
        if register_form.is_valid():
            print("register_form.is_valid()")
            user_email = request.POST.get('email', None)
            # 如果用戶已存在，則提示錯誤訊息
            if UserProfile.objects.filter(email = user_email):
                print("如果用戶已存在，則提示錯誤訊息")

                return render(request, 'course/index.html', {'register_form':register_form,'msg': '用戶已存在'})
                return redirect('/#register', {'register_form':register_form,'msg': '用戶已存在'})


            pass_word = request.POST.get('password', None)
            department = request.POST.get('department', None)
            grade = request.POST.get('grade', None)
            student_ID = request.POST.get('student_ID', None)
            birthday = request.POST.get('birthday', None)
            gender = request.POST.get('gender', None)
            mobile = request.POST.get('mobile', None)

            # 如果學號已存在，則提示錯誤訊息
            if UserProfile.objects.filter(student_ID = student_ID):
                print("學號已存在，提示錯誤訊息")
                return render(request, 'course/index.html', {'register_form':register_form,'msg': '學號已存在'})
                return redirect('/#register', {'register_form':register_form,'msg': '學號已存在'})
                
            name = request.POST.get('name', None)

            # 實例化一個user_profile對象
            user_profile = UserProfile()
            user_profile.username = name
            user_profile.email = user_email
            user_profile.department = department
            user_profile.grade = grade
            user_profile.student_ID = student_ID
            user_profile.birthday = birthday
            user_profile.gender = gender
            user_profile.mobile = mobile

            user_profile.is_active = False
            # 對保存到資料庫的密碼加密
            user_profile.password = make_password(pass_word)
            user_profile.save()
            print("user_profile.save()")
            # return render(request,'course/index.html')
            return redirect('/#register')

        else:
            # return render(request,'course/index.html',{'register_form':register_form})
            return redirect('/#register')



from django.contrib import messages

from users.forms import UserForm


def register(request):
    '''
    Register a new user
    '''
    print("register")
    template = 'users/register.html'
    if request.method == 'GET':
        # return render(request, template, {'userForm':UserForm()})
        return redirect('/#register')


    # POST
    userForm = UserForm(request.POST)
    if not userForm.is_valid():
        # return render(request, template, {'userForm':userForm})
        print(userForm)
        return redirect('/#register')


    userForm.save()
    messages.success(request, '歡迎註冊')
    return redirect('/')


# from django.contrib.auth import authenticate
# from django.contrib.auth import login as auth_login


def userlogin(request):
    '''
    Login an existing user
    '''
    template = 'course/index.html'
    if request.method == 'GET':
        print('get')
        # return render(request,template)
        return redirect('/#login')


    # POST
    email = request.POST.get('email')
    password = request.POST.get('password')
    print(email,password)
    if not email or not password:    # Server-side validation
        messages.error(request, '請填資料')
        print('請填資料')
        # return render(request,template)
        # return HttpResponseRedirect('/#login')
        return redirect('/#login')

        

    user = authenticate(email=email, password=password)
    if not user:    # authentication fails
        messages.error(request, '登入失敗')
        print('登入失敗')
        # return render(request,template)
        # return HttpResponseRedirect('/#login')
        return redirect('/#login')

        

    # login success
    login(request, user)
    messages.success(request, '登入成功')
    print('登入成功')
    return redirect('/')
    # return HttpResponseRedirect('/#login')



from django.contrib.auth import logout

def userlogout(request):
    '''
    Logout the user
    '''
    logout(request)
    messages.success(request, '歡迎再度光臨')
    return redirect('/')



