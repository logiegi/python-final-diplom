import os
from celery import Celery

# Определяем переменную окружения с настройками Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orders.settings")

# Создаём экземпляр Celery
celery_app = Celery("orders")

# Загружаем настройки из Django settings, которые начинаются с "CELERY_"
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находит все задачи (tasks) в приложениях Django
celery_app.autodiscover_tasks()
