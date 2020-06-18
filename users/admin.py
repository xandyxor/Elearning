from django.contrib import admin
from .models import UserProfile
from django.utils.safestring import mark_safe
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_permission_codename
from django.utils.translation import ngettext
from django.contrib import messages
# admin.site.register(UserProfile)



class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        fields = ('email', 'username')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label=("Password"),
        help_text=("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\'../password/\'>this form</a>."
                    "</br>原始密碼不會存儲，因此無法查看此用戶的密碼，但是您可以使用此<a href=\'../password/\'>按鈕</a>.更改密碼。"
                    ))
    class Meta:
        model = UserProfile
        # fields = ('email', 'password', 'username', 'is_staff', 'is_active')
        fields = ('image','student_ID','username','department', 'grade', 'gender','email','mobile','password')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    
    def activate_account(self, request, queryset):
        updated = queryset.update(is_active='1')
        self.message_user(request, ngettext(
            '%d 帳號已啟用',
            '%d 帳號已啟用.',
            updated,
        ) % updated, messages.SUCCESS)
    activate_account.short_description = "啟用帳號"

    def close_account(self, request, queryset):
        updated = queryset.update(is_active='0')
        self.message_user(request, ngettext(
            '%d 帳號已關閉',
            '%d 帳號已關閉.',
            updated,
        ) % updated, messages.SUCCESS)
    close_account.short_description = "關閉帳號"
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm


    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('student_ID','username','department', 'grade', 'gender','email','is_active')
    # list_filter = ('is_staff',)
    readonly_fields = ("email",)
    actions = [activate_account,close_account]
    fieldsets = (
        (None, {'fields': ('image','student_ID','username','department', 'grade', 'gender','email','mobile',)}),
        ('Change Password', {'fields': ('password',)}),
        ('Permissions', {'fields': ('is_active','groups','user_permissions')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()





# Now register the new UserAdmin...
#admin.site.register(MyUser, UserAdmin)
admin.site.register(UserProfile,UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
# admin.site.register(Group)
# Register your models here.
