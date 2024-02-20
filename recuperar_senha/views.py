from math import log
from django.views import View
from django.http import JsonResponse
from auth_class.models import CustomUser
from .models import PasswordResetToken
from email_service.views import EmailSender
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import random
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# REVIEW - Verificar link de recuperação de senha


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetView(View):
    def post(self, request, action):
        if action == "request_reset":
            return self.request_reset(request)
        elif action == "reset":
            return self.reset_password(request)
        else:
            return JsonResponse({'error': 'Ação inválida.'}, status=400)

    def request_reset(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')

            try:
                user = CustomUser.objects.get(email=email)
                verification_code = random.randint(100000, 999999)
                # REVIEW - Verificar se está funcionando
                PasswordResetToken.objects.create(
                    user=user, token=verification_code)

                reset_link = "http://nossodominio.com/resetar-senha/"
                EmailSender.send_email(
                    user.email,
                    "Redefinição de Senha",
                    f"Clique no link para redefinir sua senha: {reset_link}. Seu código de verificação é: {verification_code}",
                    'parceirodocontador.suporte@gmail.com',
                    os.getenv('SECRETKEY_EMAIL')
                )
                return JsonResponse({'message': 'E-mail de redefinição de senha enviado.'}, status=200)
            except CustomUser.DoesNotExist:
                logger.error(f'Erro ao enviar email: {e}', exc_info=True)
                return JsonResponse({'message': 'E-mail não encontrado.'}, status=404)
        except Exception as e:
            logger.error(
                f'Erro ao enviar email de recuperação de senha: {e}', exc_info=True)
            return JsonResponse({'message': 'Erro ao enviar e-mail de recuperação de senha.'}, status=500)

    def reset_password(self, request):
        try:
            data = json.loads(request.body)
            verification_code = data.get('verification_code')
            new_password = data.get('new_password')

            try:
                reset_token = PasswordResetToken.objects.get(
                    token=verification_code, used=False)
                if reset_token.is_valid():
                    user = reset_token.user
                    user.set_password(new_password)
                    user.save()
                    reset_token.used = True
                    reset_token.save()
                    return JsonResponse({'message': 'Senha redefinida com sucesso.'}, status=200)
                else:
                    return JsonResponse({'message': 'Código de verificação inválido ou expirado.'}, status=400)
            except PasswordResetToken.DoesNotExist:
                logger.error(
                    f'Erro ao redefinir senha: {e}', exc_info=True)
                return JsonResponse({'message': 'Código de verificação inválido.'}, status=400)
        except Exception as e:
            logger.error(
                f'Erro ao redefinir senha: {e}', exc_info=True)
            return JsonResponse({'message': 'Erro ao redefinir senha.'}, status=500)
