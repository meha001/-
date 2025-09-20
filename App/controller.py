__author__ = 'meha001'

from flask_restful import Resource, reqparse  # Исправленный импорт
from flask_security import auth_token_required, roles_required, login_user  # Исправленный импорт
from flask import current_app
from .models import User


class Protected(Resource):
    @auth_token_required
    def get(self):
        return {"msg": "这是需要Token的GET方法"}, 200

    @auth_token_required
    @roles_required('admin')  # 不满足则跳转至SECURITY_UNAUTHORIZED_VIEW
    def post(self):
        return {"msg": "这是需要Token和admin权限的POST方法"}, 201


class Login(Resource):  # 自定义登录函数
    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('username', type=str, location='json', required=True, help="用户名不能为空") \
            .add_argument("password", type=str, location='json', required=True, help="密码不能为空") \
            .parse_args()
        
        user = User.authenticate(args['username'], args['password'])
        if user:
            login_user(user)  # Упрощенный вызов
            return {
                "message": "登录成功", 
                "token": user.get_auth_token(),
                "user_id": user.id,
                "username": user.username
            }, 200
        else:
            return {"message": "用户名或密码错误"}, 401