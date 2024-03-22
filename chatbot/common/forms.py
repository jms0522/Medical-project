from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # 명시적으로 email 필드 추가

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',)  # email 필드만 사용

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError(_("유효한 이메일 주소를 입력해주세요."))
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("이미 사용 중인 이메일 주소입니다."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # username 필드에 email 값을 할당
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    pass
