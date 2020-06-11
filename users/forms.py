# users/forms.py

from django import forms
from users.models import UserProfile

# 登錄表單驗證
class LoginForm(forms.Form):
    # 使用者名稱密碼不能為空
    username = forms.CharField(required=True)
    password = forms.CharField(required=True,min_length=5)

class RegisterForm(forms.Form):
    '''註冊驗證表單'''    
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True,min_length=5)

    department = forms.CharField(required=False)
    grade = forms.CharField(required=False)
    student_ID = forms.CharField(required=False)
    birthday = forms.DateField(required=False)
    gender = forms.CharField(required=False)
    mobile = forms.CharField(required=False)


    # image = forms.ImageField()
    # department = models.CharField('科系',max_length=10,choices=department_choices,default=1)
    # grade = models.CharField('年級',max_length=10,choices=grade_choices,default=1)
    # student_ID = models.CharField('學號',max_length=11)
    # birthday = models.DateField('生日',null=True,blank=True)
    # gender = models.CharField('性別',max_length=10,choices=gender_choices,default='female')
    # mobile = models.CharField('手機號碼',max_length=11,null=True,blank=True)
    # email = models.EmailField('信箱',max_length=50)
    # image = models.ImageField(upload_to='image/%Y%m',default='image/default.png',max_length=100)


class UserForm(forms.ModelForm):
    gender_choices = (
        ('男','男'),
        ('女','女'),
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
    username = forms.CharField(label='姓名')
    department = forms.CharField(label= '科系',widget=forms.Select(choices=department_choices))
    grade = forms.CharField(label ='年級',widget=forms.Select(choices=grade_choices))
    student_ID = forms.CharField(label = '學號')
    birthday = forms.DateField(label = '生日')
    gender = forms.CharField(label = '性別',widget=forms.Select(choices=gender_choices))
    mobile = forms.CharField(label = '手機號碼')
    email = forms.EmailField(label='信箱')
    # image = forms.ImageField(upload_to='image/%Y%m',default='image/default.png',max_length=100,null=True)

    password = forms.CharField(label='密碼',required=True, widget=forms.PasswordInput())
    password2 = forms.CharField(label='確認密碼',required=True, widget=forms.PasswordInput())

    
    class Meta:
        model = UserProfile
        fields = ['username', "department",'grade','student_ID','birthday','gender','mobile','email', 'password', 'password2']

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password!=password2:
            raise forms.ValidationError('密碼不相符')
        return password2

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.set_password(user.password)
        if commit:
            user.save()
        return user