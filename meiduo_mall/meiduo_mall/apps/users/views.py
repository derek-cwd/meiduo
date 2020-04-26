from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render


# Create your views here.
from django.views import View

from users.models import User
import json, re
from django_redis import get_redis_connection




class UsernameCountView(View):

    def get(self, request, username):


        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            return JsonResponse({'code':400,
                                 'errmsg': '访问数据库失败'})

        return JsonResponse({'code': 0,
                             'errmsg': 'ok',
                             'count': count})


class MobileCountView(View):

    def get(self, request, mobile):

        #1.查询mobile在mysql中的个数
        try:
            count = User.object.filter(mobile=mobile).count()
        except Exception as e:
            return JsonResponse({'code':400,
                                 'errmsg': '查询数据库出错'})
        #2. 返回结果(json)
        return JsonResponse({'code': 0,
                             'errmsg': 'ok',
                             'count': count})


class RegisterView(View):

    def post(self, request):
        '''实现注册接口'''

        #1. 接收json参数,获取每一个
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        password2 = dict.get('password2')
        mobile = dict.get('mobile')
        allow = dict.get('allow')
        sms_code_client = dict.get('sms_code')

        #2. 整体检验,查看是否有空值
        if not all([username, password, password2, mobile, sms_code_client]):
            return JsonResponse({'code':400,
                                 'errmsg':'缺少必传参数'})
        #3. 单个检验,username是否为5-20位
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return JsonResponse({'code': 400,
                                 'errmsg': 'username不满足格式要求'})
        #4. password是否为8-20位
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return JsonResponse({'code': 400,
                                 'errmsg': 'pssword不满足格式要求'})
        #5. 判断两个密码是否一致
        if password != password2:
            return JsonResponse({'code': 400,
                                 'errmsg': '两次输入不对'})
        #6. mobile是否为手机格式
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code':400,
                                 'errmsg': '手机号不满足格式要求'})
        #7. allow是否为true
        if allow != True:
            return JsonResponse({'code':400,
                                 'errmsg': 'allow不满足格式要求'})
        #8. 链接redis,获取redis连接对象
        redis_conn = get_redis_connection('verify_code')
        #9. 从redis中,获取保存的短信验证码
        sms_code_server = redis_conn.get('sms_%s' % mobile)

        if not sms_code_server:
            return JsonResponse({'code':400,
                                 'errmsg':'短信验证码过期'})
        #10. 把前后端的短信验证码进行比对
        if sms_code_client != sms_code_server.decode():
            return JsonResponse({'code':400,
                                 'errmsg': '输入的短信验证码不对'})

        #11. 把前端传入的mobile, username, password保存到User
        try:
            user = User.objects.create_user(username=username,
                                     password=password,
                                     mobile=mobile)
        except Exception as e:
            return JsonResponse({'code':400,
                                 'errmsg':'数据库保存失败'})

        #补充:实现状态保持:
        login(request, user)

        #12. 返回结果(json)
        return JsonResponse({'code': 0,
                             'errmsg': 'ok'})