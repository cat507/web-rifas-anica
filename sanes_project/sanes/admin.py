from django.contrib import admin
from .models import Cupo, Order, Ticket

class CupoAdmin(admin.ModelAdmin):
    list_display = ('san', 'participante', 'numero_semana', 'asignado', 'estado')
    list_filter = ('estado', 'san')
    search_fields = ('participante__username', 'san__nombre')
    actions = ['confirmar_pago', 'rechazar_pago']

    @admin.action(description='Confirmar pago seleccionado')
    def confirmar_pago(self, request, queryset):
        queryset.update(estado='confirmado')
        self.message_user(request, "Pago confirmado con éxito.")

    @admin.action(description='Rechazar pago seleccionado')
    def rechazar_pago(self, request, queryset):
        queryset.update(estado='rechazado')
        self.message_user(request, "Pago rechazado con éxito.")

admin.site.register(Cupo, CupoAdmin)

# Registra Order solo si no está registrado
try:
    admin.site.register(Order)
except AlreadyRegistered:
    print("Order ya está registrado")

# Registra Ticket solo si no está registrado
try:
    admin.site.register(Ticket)
except AlreadyRegistered:
    print("Ticket ya está registrado")

from .models import Pago

class PagoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cupo', 'monto_pagado', 'fecha_pago', 'estado')
    list_filter = ('estado', 'usuario')
    search_fields = ('usuario__username',)

admin.site.register(Pago, PagoAdmin)