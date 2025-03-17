from django.db import models
from django.contrib.auth.models import User
from datetime import date  # Para usar la fecha actual
from django.core.mail import send_mail

class San(models.Model):
    PAYMENT_FREQUENCIES = [
        ('mensual', 'Mensual'),
        ('quincenal', 'Quincenal'),
    ]

    # Nombre del SAN o del producto
    name = models.CharField(max_length=255)
    
    # Organizador del SAN
    organizador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sanes_organizados', null=True, blank=True)  # Permite temporalmente nulo
    
    # Fecha de inicio del SAN
    fecha_inicio = models.DateField(default=date.today)  # Define la fecha actual como predeterminada

    # Precio total del sane o producto
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Número de cuotas en las que se va a dividir el pago
    num_cuotas = models.PositiveIntegerField()

    # Frecuencia de pago
    payment_frequency = models.CharField(max_length=10, choices=PAYMENT_FREQUENCIES, default='mensual')

    # Tipo de SAN (Ahorro o Producto)
    type_of_san = models.CharField(max_length=255, choices=[('ahorro', 'Ahorro'), ('producto', 'Producto')])

    # Imagen representativa del SAN
    image = models.ImageField(upload_to='products/')

    # Total de participantes del SAN
    total_participantes = models.PositiveIntegerField(default=1)

    # Cuota por participante (se calcula automáticamente)
    cuota = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.cuota:
            if self.payment_frequency == 'mensual':
                self.cuota = self.total_price / self.num_cuotas
            elif self.payment_frequency == 'quincenal':
                self.cuota = self.total_price / (self.num_cuotas * 2)
        super(San, self).save(*args, **kwargs)

    def cupos_disponibles(self):
        """Calcula la cantidad de cupos disponibles."""
        return self.total_participantes - self.cupos.filter(asignado=True).count()


class Cupo(models.Model):
    ESTADO_CHOICES = [
        ('pendiente_confirmacion', 'Pendiente de Confirmación'),
        ('confirmado', 'Confirmado'),
        ('rechazado', 'Rechazado'),
    ]

    participante = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    san = models.ForeignKey('San', related_name='cupos', on_delete=models.CASCADE)
    numero_semana = models.PositiveIntegerField()
    asignado = models.BooleanField(default=False)
    metodo_pago = models.CharField(max_length=20, blank=True, null=True)
    comprobante_pago = models.ImageField(upload_to='comprobantes/', blank=True, null=True)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='pendiente_confirmacion')

    def save(self, *args, **kwargs):
        # Verificar la disponibilidad de cupos antes de guardar
        if not self.asignado and self.san.cupos_disponibles() <= 0:
            raise ValueError("No hay cupos disponibles para este SAN.")

        # Verificar si el estado ha cambiado
        if self.pk is not None:  # Verificar que el objeto no sea nuevo
            old_cupo = Cupo.objects.get(pk=self.pk)
            if old_cupo.estado != self.estado:  # Si el estado ha cambiado
                self.notify_user()  # Notificar al usuario

        # Guardar el objeto normalmente
        super(Cupo, self).save(*args, **kwargs)

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
            [self.participante.email],  # Correo del destinatario (el usuario que compró el cupo)
            fail_silently=False,
        )

    def __str__(self):
        return f'Cupo {self.numero_semana} para el SAN {self.san.name}'

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    san = models.ForeignKey(San, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    ticket_number = models.CharField(max_length=100)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    issued_at = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=20)
    oficio = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)

class Participacion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    san = models.ForeignKey(San, on_delete=models.CASCADE)
    fecha_ultima_cuota = models.DateField(null=True, blank=True)
    cuotas_pagadas = models.IntegerField(default=0)

    def fecha_proxima_cuota(self):
        from datetime import date
        hoy = date.today()
        proxima_fecha = None
        
        # Verificamos si la frecuencia de pago es mensual o quincenal
        if self.san.payment_frequency == 'mensual':
            if hoy.day < 15:
                proxima_fecha = date(hoy.year, hoy.month, 15)
            else:
                # Mover a la próxima mensualidad
                if hoy.month == 12:
                    proxima_fecha = date(hoy.year + 1, 1, 15)
                else:
                    proxima_fecha = date(hoy.year, hoy.month + 1, 15)
        
        elif self.san.payment_frequency == 'quincenal':
            if hoy.day < 15:
                proxima_fecha = date(hoy.year, hoy.month, 15)
            elif hoy.day == 15:
                proxima_fecha = date(hoy.year, hoy.month, 30)  # Si hoy es 15, la próxima es el 30
            else:
                # Mover a la próxima quincena
                if hoy.month == 12:
                    proxima_fecha = date(hoy.year + 1, 1, 15)  # Cambiar de mes
                else:
                    proxima_fecha = date(hoy.year, hoy.month + 1, 15)  # Cambiar a mes siguiente

        # Asegúrate de manejar la lógica de fin de año y el cambio de meses adecuadamente
        return proxima_fecha
    
    def cuota_a_pagar(self):
        # Calcula el monto de la próxima cuota
        return self.san.total_price / self.san.num_cuotas
    
from django.db import models
from django.contrib.auth.models import User

class Pago(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('rechazado', 'Rechazado'),
    ]
    
    cupo = models.ForeignKey('Cupo', on_delete=models.CASCADE)  # Referencia al cupo
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_pago = models.DateField(auto_now_add=True)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)  # Monto pagado
    metodo_pago = models.CharField(max_length=20, blank=True, null=True)  # Método de pago
    comprobante_pago = models.ImageField(upload_to='comprobantes/', blank=True, null=True)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='pendiente')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)  # Agregar esta línea

    def __str__(self):
        return f"Pago de {self.usuario.username} por {self.monto_pagado} en {self.fecha_pago}"
