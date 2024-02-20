from venv import logger
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import CustomUser
from backend_rocinante import settings
import json
import datetime
import jwt
import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class AuthView(View):

    def register(self, request):
        data = json.loads(request.body.decode('utf-8'))

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return JsonResponse({'error': 'Dados incompletos.'}, safe=False, status=400)

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Este email já está em uso.'}, safe=False, status=400)

        try:
            user = CustomUser.objects.create_user(
                username=username, email=email, password=password)
            login(request, user)
            return JsonResponse({'message': 'Registrado com sucesso.'}, safe=False, status=201)
        except Exception as e:
            logger.error(f'Erro ao registrar usuário: {e}', exc_info=True)
            return JsonResponse({str(e)}, status=400, safe=False)

    def login(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')

            user = authenticate(username=username, password=password)

            if user is not None:

                payload = {
                    'user_id': user.id,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                    'iat': datetime.datetime.utcnow()
                }
                token = jwt.encode(
                    payload, settings.SECRET_KEY, algorithm='HS256')
                if isinstance(token, bytes):
                    token = token.decode('utf-8')

                response_data = {
                    'message': 'Logado com sucesso.',
                    'token': token
                }
                return JsonResponse(response_data, status=200, safe=False)
            else:
                return JsonResponse({'error': 'Usuário ou senha inválidos.'}, status=400, safe=False)
        except Exception as e:
            logger.critical(f'Erro ao logar usuário: {e}', exc_info=True)
            return JsonResponse({str(e)}, status=500, safe=False)

    def logout(self, request):
        logout(request)
        return JsonResponse({'message': 'Deslogado com sucesso.'}, status=200)

    def post(self, request, action):
        if action == "register":
            return self.register(request)
        elif action == "login":
            return self.login(request)
        elif action == "logout":
            return self.logout(request)
        else:
            return JsonResponse({'error': 'Ação inválida.'}, status=400, safe=False)


def index(request):
    try:
        return render(request, 'index.html')
    except Exception as e:
        logger.critical(f'Erro na rota de index: {e}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500, safe=False)
