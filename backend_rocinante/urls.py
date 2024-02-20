from django.contrib import admin
from django.urls import path
from auth_class.views import AuthView, index
from vendas_class import views
from recuperar_senha.views import PasswordResetView
from log import views as log_views
from django.urls import path, re_path
from django.views.generic import TemplateView
from csrf_app.views import csrf_token


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/<str:action>/', AuthView.as_view(), name='auth_action'),
    path('reset/<str:action>/', PasswordResetView.as_view(), name='reset_action'),
    path('omie_vendas/get_vendas/', views.get_vendas_view, name='get_vendas'),
    path('omie_vendas/alterar_pedido/',
         views.alterar_pedido_view, name='alterar_pedido'),
    path('omie_vendas/set_adiantamentos/',
         views.set_adiantamentos_view, name='set_adiantamentos'),
    path('log/', log_views.log_from_frontend, name='log_from_frontend'),
    path('webhook-omie/', views.webhook_omie, name='webhook_omie'),
    path('', index, name='index'),
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
    path('get-csrf-token/', csrf_token)
]
