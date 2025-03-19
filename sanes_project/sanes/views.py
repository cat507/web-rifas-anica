from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.shortcuts import redirect
from .models import San, Order, Ticket  # Asumiendo que tienes modelos para órdenes y tickets
from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login
from .forms import CustomUserCreationForm
import random
from .models import Cupo
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SanForm
from .forms import ConfirmPurchaseForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import CustomLoginForm
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from .forms import CustomLoginForm  # Formulario customizado
from .models import Participacion
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import San, Participacion, Pago, Cupo, Order
from .forms import ConfirmPurchaseForm
from datetime import date
from django.http import HttpResponse
from django.http import HttpResponse
from django.contrib.auth.models import User  # User customizado
from .models import Participacion  # Importa el modelo necesario
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import San
from .serializers import SanSerializer
from .models import Cupo
from .serializers import CupoSerializer

def user_is_not_authenticated(user):
    return not user.is_authenticated

def mis_sanes(request):
    if request.user.is_authenticated:
        participaciones = Participacion.objects.filter(user=request.user)
    else:
        participaciones = None

    return render(request, 'mis_sanes.html', {
        'participaciones': participaciones,
    })

def san_list(request):
    # Obtén todos los sanes
    sanes = San.objects.all()
    san_count = sanes.count()  # Contar el número de sanes
    context = {
        'sanes': sanes,
        'san_count': san_count
    }
    return render(request, 'san_list.html', context)

def home(request):
    return render(request, 'home.html')  # Renderiza el template 'home.html'

class SanDetailView(DetailView):
    model = San
    template_name = 'san_detail.html'
    context_object_name = 'san'

    def get_object(self):
        return get_object_or_404(San, id=self.kwargs['id'])
    
def buy_san(request, san_id):
    san = get_object_or_404(San, id=san_id)

    # Verificar el número de cupos asignados
    cupos_asignados = san.cupos.filter(asignado=True).count()
    total_participantes = san.total_participantes

    # Comprobar si hay cupos disponibles
    if cupos_asignados < total_participantes:
        # Excluir el cupo de la semana 1 (organizador) y seleccionar un cupo aleatorio
        cupos_disponibles = san.cupos.filter(asignado=False).exclude(numero_semana=1)

        if cupos_disponibles.exists():
            cupo_asignado = random.choice(cupos_disponibles)
            cupo_asignado.participante = request.user
            cupo_asignado.asignado = True
            cupo_asignado.save()
            success_message = "Cupo asignado exitosamente."
            messages.success(request, success_message)
            print(success_message)  # Imprime en la consola
            return redirect('confirm_purchase', san_id=san_id)
        else:
            error_message = "No hay cupos disponibles en este momento."
            messages.error(request, error_message)
            print(error_message)  # Imprime en la consola
    else:
        error_message = "No hay cupos disponibles para este SAN."
        messages.error(request, error_message)
        print(error_message)  # Imprime en la consola

    return redirect('san_detail', san_id=san_id)

class CupoAdmin(admin.ModelAdmin):
    list_display = ('san', 'participante', 'numero_semana', 'asignado', 'estado')
    list_filter = ('estado', 'san')
    search_fields = ('participante__username', 'san__nombre')
    actions = ['confirmar_pago', 'rechazar_pago']

    # Acción para confirmar pagos
    @admin.action(description='Confirmar pago seleccionado')
    def confirmar_pago(self, request, queryset):
        queryset.update(estado='confirmado')
        self.message_user(request, "Pago confirmado con éxito.")

    # Acción para rechazar pagos
    @admin.action(description='Rechazar pago seleccionado')
    def rechazar_pago(self, request, queryset):
        queryset.update(estado='rechazado')
        self.message_user(request, "Pago rechazado con éxito.")

@user_passes_test(lambda u: u.is_superuser)  # Solo para administradores
def admin_order_report(request):
    orders = Order.objects.all()
    tickets = Ticket.objects.all()

    context = {
        'orders': orders,
        'tickets': tickets
    }
    return render(request, 'admin_order_report.html', context)

@user_passes_test(user_is_not_authenticated)
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Guarda el usuario y crea el perfil
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # Loguea al usuario automáticamente
            return redirect('home')  # Redirige después de registrarse
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def order_confirmation(request, order_id):
    # Obtener la orden usando el ID proporcionado
    order = get_object_or_404(Order, id=order_id)

    # Obtener el objeto SAN relacionado con la orden
    san = order.san

    # No necesitas crear una nueva orden aquí, solo mostrar los detalles de la ya existente

    # Puedes también obtener el ticket asociado a esta orden, si es necesario
    ticket = Ticket.objects.filter(order=order).first()

    # Renderiza la página de confirmación con la información de la orden y el ticket
    return render(request, 'order_confirmation.html', {
        'order': order,
        'san': san,
        'ticket': ticket  # Pasamos el ticket si es necesario mostrarlo
    })

def san_detail(request, id):
    san = get_object_or_404(San, id=id)
    
    # Supongamos que tienes un modelo de cupos o eventos relacionados con el 'San'
    cupos_disponibles = san.cupos.all()  # O ajusta según tu modelo
    
    # Convertir los cupos a un formato compatible con FullCalendar
    eventos = []
    for cupo in cupos_disponibles:
        eventos.append({
            'title': 'Cupo disponible',
            'start': cupo.fecha.isoformat(),  # Asegúrate de que la fecha esté en formato ISO 8601
        })
    
    return render(request, 'san_detail.html', {'san': san, 'eventos': eventos})

def asignar_cupo_aleatorio(san_id, usuario):
    san = get_object_or_404(San, pk=san_id)
    cupos_disponibles = san.cupos.filter(asignado=False).exclude(numero_semana=1)
    
    if cupos_disponibles.exists():
        cupo_asignado = random.choice(cupos_disponibles)
        cupo_asignado.participante = usuario
        cupo_asignado.asignado = True
        cupo_asignado.save()
    else:
        # Lógica en caso de que no haya cupos disponibles
        pass

def confirmar_compra(request, san_id):
    san = get_object_or_404(San, pk=san_id)
    
    tasa_bs = 90  # 1 Bs = 90 Pesos
    tasa_usd = 36  # 1 USD = 36 Bs = 3700 Pesos
    
    # Supongamos que el monto del san es en bolívares
    monto_bs = san.monto
    monto_pesos = monto_bs * tasa_bs
    monto_usd = monto_bs / tasa_usd
    
    if request.method == "POST":
        metodo_pago = request.POST.get('metodo_pago')
        # Guardar los datos y proceder al pago
        # ...
    
    context = {
        'san': san,
        'monto_bs': monto_bs,
        'monto_pesos': monto_pesos,
        'monto_usd': monto_usd,
    }
    return render(request, 'confirmar_compra.html', context)

def mis_sanes(request):
    if request.user.is_authenticated:
        participaciones = Participacion.objects.filter(user=request.user)
    else:
        participaciones = None

    return render(request, 'mis_sanes.html', {
        'participaciones': participaciones,
    })

@login_required
def detail_san(request, san_id):
    san = get_object_or_404(San, pk=san_id)
    cupos = Cupo.objects.filter(san=san)  # Filtrar los cupos asociados a ese san
    fechas_de_cobro = calculate_payment_dates(san)  # Función que calcula las fechas de cobro según el tipo de SAN

    context = {
        'san': san,
        'cupos': cupos,
        'fechas_de_cobro': fechas_de_cobro,
        'user_has_cupo': check_user_cupo(request.user, san)  # Lógica para verificar si el usuario tiene un cupo asignado
    }

    return render(request, 'detail_san.html', context)

""" def buy_san(request, san_id):
    san = get_object_or_404(San, pk=san_id)

    # Verificar el número de cupos asignados
    cupos_asignados = san.cupos.filter(asignado=True).count()
    total_participantes = san.total_participantes

    if cupos_asignados < total_participantes:
        cupos_disponibles = san.cupos.filter(asignado=False).exclude(numero_semana=1)

        if cupos_disponibles.exists():
            cupo_asignado = random.choice(cupos_disponibles)
            cupo_asignado.participante = request.user
            cupo_asignado.asignado = True
            cupo_asignado.save()

            messages.success(request, "Cupo asignado exitosamente.")
            return redirect('confirm_purchase', san_id=san_id)
        else:
            messages.error(request, "No hay cupos disponibles.")
            print("No hay cupos disponibles.")
    else:
        messages.error(request, "Todos los cupos ya han sido asignados.")
    
    return redirect('san_detail', san_id=san_id) """

class SanDetailView(DetailView):
    model = San
    template_name = 'san_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        san = self.get_object()
        
        # Verificar si el usuario tiene un cupo en este SAN
        user_has_cupo = False
        if self.request.user.is_authenticated:
            user_has_cupo = Cupo.objects.filter(participante=self.request.user, san=san).exists()
        
        context['user_has_cupo'] = user_has_cupo
        return context
    
    def get_object(self):
        san_id = self.kwargs.get('san_id')
        return get_object_or_404(San, pk=san_id)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import San, Order, Cupo
from .forms import ConfirmPurchaseForm
from django.utils.crypto import get_random_string
from .models import San, Participacion, Pago, Order, Ticket

def confirm_purchase(request, san_id):
    san = get_object_or_404(San, pk=san_id)
    cupo_asignado = san.cupos.filter(participante=request.user).first()

    # Si no tiene un cupo asignado, mostrar mensaje de error
    if not cupo_asignado:
        messages.error(request, "No tienes cupos asignados para este SAN.")
        return redirect('san_list')

    # Tasas de conversión
    usd_to_bs = 36
    usd_to_pesos = 3700

    # Monto total en dólares del SAN
    monto_usd_total = san.total_price
    cuota_monto = monto_usd_total / san.num_cuotas  # Calcula el monto de la cuota
    monto_bs = cuota_monto * usd_to_bs
    monto_pesos = cuota_monto * usd_to_pesos

    if request.method == 'POST':
        form = ConfirmPurchaseForm(request.POST, request.FILES)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            payment_receipt = form.cleaned_data.get('payment_receipt')

            # Guardar detalles del método de pago en el cupo asignado
            cupo_asignado.metodo_pago = payment_method
            if payment_method == 'bank_transfer' and payment_receipt:
                cupo_asignado.comprobante_pago = payment_receipt

            # Actualizar el estado del cupo a "pendiente_confirmacion"
            cupo_asignado.estado = 'pendiente_confirmacion'
            cupo_asignado.save()

            # Crear la orden
            order = Order.objects.create(
                san=san,
                user=request.user,
                total_price=cuota_monto
            )

            # Crear el registro de pago
            pago = Pago.objects.create(
                cupo=cupo_asignado,
                usuario=request.user,
                fecha_pago=date.today(),
                monto_pagado=cuota_monto,
                metodo_pago=payment_method,
                comprobante_pago=payment_receipt,
                order=order  # Asociar el pago a la orden creada
            )

            # Crear un ticket asociado a la orden
            ticket_number = get_random_string(length=10)  # Generar un número de ticket aleatorio
            ticket = Ticket.objects.create(
                order=order,  # Asocia el ticket con la orden
                ticket_number=ticket_number,
                amount_paid=cuota_monto
            )

            # Crear o actualizar la participación del usuario en este SAN
            participacion, created = Participacion.objects.get_or_create(
                user=request.user,
                san=san,
                defaults={
                    'fecha_ultima_cuota': date.today(),  # Fecha de la primera cuota
                    'cuotas_pagadas': 1  # Se asume que ya ha pagado la primera cuota
                }
            )

            if not created:
                # Si ya existe la participación, actualiza los datos de las cuotas
                participacion.cuotas_pagadas += 1
                participacion.fecha_ultima_cuota = date.today()
                participacion.save()

            # Mostrar mensaje de éxito con el número de ticket
            messages.success(request, f"Tu pago ha sido registrado exitosamente. Tu número de ticket es: {ticket.ticket_number}.")
            return redirect('order_confirmation', order_id=order.id)

    else:
        form = ConfirmPurchaseForm()

    context = {
        'san': san,
        'cuota_monto': cuota_monto,  # Monto de la cuota inicial en USD
        'monto_bs': monto_bs,  # Monto de la cuota inicial en BS
        'monto_pesos': monto_pesos,  # Monto de la cuota inicial en COP
        'form': form,  # Formulario de confirmación
    }

    return render(request, 'confirm_purchase.html', context)

def create_san(request):
    if request.method == 'POST':
        form = SanForm(request.POST, request.FILES)
        if form.is_valid():
            san = form.save()  # Guarda el SAN y luego crea los cupos
            # Crear los cupos asociados al nuevo SAN
            for i in range(1, san.total_participantes + 1):
                Cupo.objects.create(san=san, numero_semana=i, asignado=False)
            messages.success(request, 'El SAN fue creado exitosamente con sus cupos.')
            return redirect('san_list')  # Redirigir a una vista de lista de SANs
    else:
        form = SanForm()

    return render(request, 'create_san.html', {'form': form})

@user_passes_test(user_is_not_authenticated)
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Intenta autenticar usando el email o nombre de usuario
            try:
                user = User.objects.get(email=username_or_email)
                username = user.username  # Obtener el nombre de usuario desde el email
            except User.DoesNotExist:
                username = username_or_email  # Asumir que es el nombre de usuario

            # Intentar autenticar al usuario
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('san_list')  # Redirigir después de iniciar sesión
            else:
                form.add_error(None, "Credenciales incorrectas")
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})


def user_is_not_authenticated(user):
    return not user.is_authenticated  # True si el usuario NO está autenticado

def logout_view(request):
    logout(request)  # Cierra la sesión del usuario
    return redirect('san_list')  # Redirige a la página de inicio

def notify_user(self):
    # Preparar el asunto y mensaje según el estado
    if self.estado == 'confirmado':
        subject = "Confirmación de Pago"
        message = f"Hola {self.participante.username}, tu pago ha sido confirmado para el SAN {self.san.name}."
    elif self.estado == 'rechazado':
        subject = "Pago Rechazado"
        message = f"Hola {self.participante.username}, tu pago ha sido rechazado para el SAN {self.san.name}. Por favor, contáctanos para más información."

    # Enviar correo electrónico
    send_mail(
        subject,
        message,
        'mr.alejandrocs@gmail.com',  # Correo del remitente
        [self.participante.email],  # Correo del destinatario
        fail_silently=False,
    )

from datetime import timedelta, date
from django.utils import timezone

def cuotas_san(request, san_id):
    san = get_object_or_404(San, pk=san_id)
    participacion = Participacion.objects.filter(user=request.user, san=san).first()

    if not participacion:
        messages.error(request, "No estás inscrito en este SAN.")
        return redirect('mis_sanes')

    total_cuotas = san.num_cuotas
    cuotas_pagadas = participacion.cuotas_pagadas
    cuota_monto = san.total_price / total_cuotas  # Monto de cada cuota

    # Lista para almacenar las cuotas y sus estados
    cuotas_info = []
    for i in range(total_cuotas):
        cuota_fecha = participacion.fecha_ultima_cuota.replace(day=1) + timedelta(days=15 * i)  # Suponiendo cuotas quincenales
        
        # Lógica para determinar el estado de la cuota
        if i < cuotas_pagadas:
            estado = "Usuario ya ha cancelado esta cuota"
        elif cuota_fecha > timezone.now().date():
            estado = "El usuario todavía no puede cancelar esta cuota"
        else:
            estado = "Registrar pago"  # Botón para registrar pago

        cuotas_info.append({
            'cuota_fecha': cuota_fecha,
            'estado': estado,
            'cuota_numero': i + 1,  # Agregar número de cuota
            'cuota_monto': cuota_monto,  # Monto de la cuota
        })

    context = {
        'san': san,
        'cuotas_info': cuotas_info,
    }
    
    return render(request, 'cuotas_san.html', context)

from twilio.rest import Client

def enviar_recordatorio(usuario):
    account_sid = 'AC86656496b25c6c61594341718cd7267e'
    auth_token = '393e069823047f979532387d440047dd'
    client = Client(account_sid, auth_token)

    mensaje = f"Hola {usuario.username}, recuerda que tu próximo pago es el {fecha_pago}."
    client.messages.create(
        body=mensaje,
        from_='+1234567890',  # Tu número de Twilio
        to=usuario.telefono
    )

from datetime import timedelta, datetime

import datetime

def calculate_payment_dates(san):
    fechas = []
    fecha_inicio = san.fecha_inicio

    if san.payment_frequency == 'quincenal':
        # Agregar los días 15 y 30 de cada mes desde la fecha de inicio
        for i in range(6):  # Ejemplo: los próximos 6 meses
            day_15 = fecha_inicio.replace(day=15) + datetime.timedelta(days=30*i)
            day_30 = fecha_inicio.replace(day=30) + datetime.timedelta(days=30*i)
            fechas.extend([day_15, day_30])
    elif san.payment_frequency == 'mensual':
        # Agregar el día 15 de cada mes
        for i in range(6):  # Ejemplo: los próximos 6 meses
            day_15 = fecha_inicio.replace(day=15) + datetime.timedelta(days=30*i)
            fechas.append(day_15)
    
    return [fecha.strftime('%Y-%m-%d') for fecha in fechas]  # Asegúrate de devolver las fechas en el formato correcto

def calendario_view(request, san_id):
    san = get_object_or_404(San, id=san_id)
    cupos = Cupo.objects.filter(san=san)
    fechas_cobro = calcular_fechas_de_cobro(san)

    context = {
        'san': san,
        'cupos': cupos,
        'fechas_de_cobro': fechas_cobro
    }
    return render(request, 'calendario.html', context)

from twilio.rest import Client
from django.http import HttpResponse
from twilio.rest import Client
from django.contrib.auth.models import User
from .models import San, Participacion, UserProfile

def enviar_recordatorio(usuario):
    account_sid = 'AC86656496b25c6c61594341718cd7267e'
    auth_token = '393e069823047f979532387d440047dd'
    client = Client(account_sid, auth_token)

    # Número de teléfono específico al que enviar el mensaje
    telefono_destinatario = '+584247300736'  # Asegúrate de que este número esté verificado en tu cuenta de Twilio

    try:
        mensaje = f"Hola {usuario.username}, este es un recordatorio de que tienes un pago pendiente."
        client.messages.create(
            body=mensaje,
            from_='+18123083515',  # Tu número de Twilio
            to=telefono_destinatario
        )
        print(f"Mensaje real enviado a {telefono_destinatario}.")
    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")

def enviar_recordatorio_view(request, usuario_id):
    # Obtener el usuario desde la base de datos
    usuario = get_object_or_404(User, id=usuario_id)  # Cambia Usuario por User
    
    # Llamar a la función que envía el mensaje
    enviar_recordatorio(usuario)  # Asegúrate de que esta función esté definida
    
    # Devolver una respuesta
    return HttpResponse(f"Recordatorio enviado a {telefono_destinatario} con éxito.")

def enviar_recordatorio_view(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    
    # Llamar a la función que envía el mensaje
    enviar_recordatorio(usuario)
    
    # Devolver una respuesta
    return HttpResponse(f"Recordatorio enviado a {usuario.username} con éxito a {usuario.userprofile.telefono}.")

def api_home(request):
    return JsonResponse({"message": "Bienvenido a la API de Django"}, safe=False)

class SanList(APIView):
    def get(self, request):
        san_list = San.objects.all()
        serializer = SanSerializer(san_list, many=True)
        return Response(serializer.data)
    
class CupoList(APIView):
    def get(self, request):
        cupo_list = Cupo.objects.all()
        serializer = CupoSerializer(cupo_list, many=True)
        return Response(serializer.data)