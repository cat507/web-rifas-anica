from django.urls import path
from . import views  # Asegúrate de que este archivo 'views.py' exista
from .views import SanDetailView
from .views import register
from django.contrib.auth import views as auth_views
from .views import admin_order_report
from django.conf import settings
from django.conf.urls.static import static
from .views import logout_view
from .views import login_view
from .views import mis_sanes, cuotas_san, confirm_purchase

urlpatterns = [
    path('sanes/', views.san_list, name='san_list'),
    path('san/<int:san_id>/', views.SanDetailView.as_view(), name='san_detail'),  # Cambiar 'id' por 'san_id'
    path('san/<int:san_id>/buy/', views.buy_san, name='buy_san'),  # Usar 'san_id'
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),  # Cambia a donde quieras redirigir
    path('register/', register, name='register'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('san/<int:san_id>/confirm/', views.confirm_purchase, name='confirm_purchase'),
    path('admin/order_report/', views.admin_order_report, name='admin_order_report'),
    path('create/', views.create_san, name='create_san'),
    path('mis-sanes/', views.mis_sanes, name='mis_sanes'),
    path('cuotas_san/<int:san_id>/', cuotas_san, name='cuotas_san'),  # Nueva URL para cuotas_san
    path('enviar-recordatorio/<int:usuario_id>/', views.enviar_recordatorio_view, name='enviar_recordatorio'),
    path('', views.home, name='home'),  # Ruta vacía, apunta a la vista 'home'
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)