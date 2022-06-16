from datetime import timedelta
import dj_database_url
import os
import django_heroku
# from celery import Celery
import redis

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "ro5rd^(wia%&wji)uc@st(6l@e)-^0e$o*wx-3w=v8^!6m=d%e"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

# app = Celery('example')
# app.conf.update(BROKER_URL=os.environ.get('REDIS_URL'),CELERY_RESULT_BACKEND=os.environ.get('REDIS_URL'))

# Application definition

INSTALLED_APPS = [
    # Project Apps
    'homepage.apps.HomepageConfig',
    'billing.apps.BillingConfig',
    'management.apps.ManagementConfig',
    'blog.apps.BlogConfig',
    'dashboard.apps.DashboardConfig',
    'users.apps.UsersConfig',
    'service.apps.ServiceConfig',
    'chat.apps.ChatConfig',
    'channels',
    # 'whitenoise.runserver_nostatic',

    # Django libraries
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Other libs
    'django_celery_beat',
    "verify_email.apps.VerifyEmailConfig",
    'crispy_forms',
    'storages',
    'six'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

]

ROOT_URLCONF = 'webapp.urls'

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

# AUTH_USER_MODEL = 'users.Account'
WSGI_APPLICATION = 'webapp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASE_URL = os.environ['DATABASE_URL']

# conn = psycopg2.connect('django.db.backends.sqlite3', sslmode='require')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        # 'CONN_MAX_AGE': 10
    }
}
db_from_env = dj_database_url.config(ssl_require=False)
DATABASES['default'].update(db_from_env)
django_heroku.settings(locals(), logging=not DEBUG, databases=not DEBUG)

# del DATABASES['default']['OPTIONS']['sslmode']


# DATABASES['default']=dj_database_url.config(
#                             conn_max_age=600, ssl_require=True)


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Media Settings
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

#Email Settings
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = "confirmemailiblinkco@gmail.com"
EMAIL_HOST_PASSWORD = "cziyqvprtpzbvlux"

DEFAULT_FROM_EMAIL = 'noreply<no_reply@domain.com>'
# HTML_MESSAGE_TEMPLATE = "users/activate_email.html"

# Celery 
CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
CELERY_IMPORTS = ("service", "users", "management")
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'


AUTHENTICATION_BACKENDS = (
    # 'django.contrib.auth.backends.ModelBackend',
    'users.backends.EmailBackend',
    # 'django.contrib.auth.backends.ModelBackend',
)

# Channels
ASGI_APPLICATION = 'webapp.routing.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379')],
        },
    },
}

# Redis caches 
CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": os.environ.get('REDIS_URL'),
    }
}

POOL = redis.ConnectionPool(host=os.environ.get('REDIS_URL'), port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

# Defining for production
if os.getcwd() =='/app':
    DEBUG=False


# Stripe
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_CONNECT_CLIENT_ID = os.environ.get('STRIPE_CONNECT_CLIENT_ID')

# AWS E3
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = "iblinkco-django"
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


