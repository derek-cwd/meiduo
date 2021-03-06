from django.contrib.auth.backends import ModelBackend
import re

from users.models import User


def get_user_by_account(account):
    '''判断account到底是usernam还是mobile'''
    try:
        if re.match(r'^1[3-9\d{9}$]', account):
            #mobile
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except Exception as e:
        return None
    else:
        return user

class usernameMobileAuthentication(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        '''重写认证函数: 使其具有手机号功能'''

        #自定义一个函数,用来区分username保存的类型: username/mobile
        user = get_user_by_account(username)

        if user and user.check_password(password):

            return user


