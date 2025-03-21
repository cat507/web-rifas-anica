# Generated by Django 5.1.1 on 2024-09-28 21:25

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sanes', '0002_order_ticket'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='san',
            name='fecha_inicio',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='san',
            name='organizador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sanes_organizados', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='san',
            name='total_participantes',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.CreateModel(
            name='Cupo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_semana', models.PositiveIntegerField()),
                ('asignado', models.BooleanField(default=False)),
                ('participante', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('san', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cupos', to='sanes.san')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cedula', models.CharField(max_length=20)),
                ('oficio', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=15)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
