"""
Django settings for sanes_project project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-7fqao6yfgprx14hmu8)m!ky49it#(w09upt14ysj9&kwub3%0&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '192.168.1.106',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sanes',
    'corsheaders',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'sanes_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sanes_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'anica_db',
        'USER': 'admin',
        'PASSWORD': 'admin',
        'HOST': 'localhost',  # O la dirección de tu servidor MySQL
        'PORT': '3306',  # Puerto de MySQL (3306 es el puerto por defecto)
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Directorio donde se almacenan los archivos estáticos durante el desarrollo
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Directorio estático en la raíz del proyecto
]

# Directorio donde se almacenan los archivos estáticos después de ejecutar collectstatic
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Directorio para almacenar archivos cargados por el usuario (imágenes, archivos)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuración de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Cambia esto por el servidor SMTP que utilices
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mr.alejandrocs@gmail.com'  # Correo desde el cual se enviarán los emails
EMAIL_HOST_PASSWORD = 'qesa vzke xaks eurr'  # La contraseña de tu correo electrónico

# También puedes configurar un email de no-reply si es necesario:
DEFAULT_FROM_EMAIL = 'noreply@tu_dominio.com'

# Internationalization
LANGUAGE_CODE = 'es-ve'  # Cambia a español de Venezuela, por ejemplo

TIME_ZONE = 'America/Caracas'  # Zona horaria de Venezuela

USE_I18N = True
USE_L10N = True
USE_TZ = True  # O False si no vas a usar zonas horarias con soporte UTC

LOGIN_REDIRECT_URL = 'san_list'  # O cualquier otra vista que desees

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Deja el backend por defecto
    'sanes.authentication_backends.EmailBackend',  # Reemplaza con la ruta real
)

CORS_ALLOW_ALL_ORIGINS = True