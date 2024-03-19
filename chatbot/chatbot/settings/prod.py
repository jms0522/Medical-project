from .base import *

DEBUG = False

ALLOWED_HOSTS = ['43.201.236.125']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

RABBITMQ_USER = os.getenv('RABBITMQ_USER')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json_formatter': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'interaction': {
            'level': 'INFO',
            'filters': ['require_debug_false'], # 운영 시 변경 필요
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/drrc.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'error': {
            'level': 'INFO',
            'filters': ['require_debug_false'], # 운영 시 변경 필요
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/error.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'logstash': {
            'level': 'INFO',
            'class': 'logstash.TCPLogstashHandler',
            'host': 'logstash',  # Logstash 서버 주소
            'port': 5959,  # Logstash 설정에서 정의한 포트
            'version': 1,
            'message_type': 'django',  # 사용할 메시지 타입
            'fqdn': False,  # FQDN 사용 여부
            'tags': ['django'],  # 태그 리스트
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins', 'error', 'logstash'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server', 'logstash'],
            'level': 'INFO',
            'propagate': False,
        },
        'drrc': {
            'handlers': ['console', 'interaction', 'logstash'],
            'level': 'INFO',
        },
        'error': {
            'handlers': ['console', 'error', 'logstash'],
            'level': 'INFO',
        },
    }
}