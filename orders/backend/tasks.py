import requests
import yaml 
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.db import IntegrityError


from backend.models import Shop, Category, Product, Parameter, ProductParameter, ProductInfo
from orders.celery import celery_app


@celery_app.task()
def send_email(title, message, email, *args, **kwargs):
    email_list = list()
    email_list.append(email)
    try:
        msg = EmailMultiAlternatives(subject=title, body=message, from_email=settings.EMAIL_HOST_USER, to=email_list)
        msg.send()
        return f'{title}: {msg.subject}, Message:{msg.body}'
    except Exception as e:
        raise e


import requests
import yaml
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from django.db.utils import IntegrityError
from celery import shared_task

@shared_task
def get_import(partner, url):
    if not url:
        return {'Status': False, 'Error': 'Url is empty'}

    stream = None

    # Проверяем, это локальный файл или URL
    if url.startswith("file://"):
        # Убираем "file://" и читаем файл локально
        file_path = url.replace("file://", "")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                stream = f.read()
        except FileNotFoundError:
            return {'Status': False, 'Error': 'Файл не найден'}
        except Exception as e:
            return {'Status': False, 'Error': f'Ошибка при чтении файла: {str(e)}'}
    else:
        # Проверяем, что URL валиден
        validate_url = URLValidator()
        try:
            validate_url(url)
            response = requests.get(url)
            if response.status_code != 200:
                return {'Status': False, 'Error': f'Ошибка HTTP {response.status_code}'}
            stream = response.text
        except ValidationError:
            return {'Status': False, 'Error': 'Неверный URL'}
        except requests.RequestException as e:
            return {'Status': False, 'Error': f'Ошибка запроса: {str(e)}'}

    # Загружаем YAML
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        return {'Status': False, 'Error': f'Ошибка в YAML: {str(e)}'}

    # Обрабатываем магазин
    try:
        shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=partner)
    except IntegrityError as e:
        return {'Status': False, 'Error': str(e)}

# Загружаем категории
    for category in data.get('categories', []):
        category_object = Category.objects.filter(id=category['id']).first()

        if category_object:
            print(f"⚠️ Категория {category_object.name} (ID: {category['id']}) уже существует, пропускаем создание")
        else:
            category_object = Category.objects.create(id=category['id'], name=category['name'])
            print(f"✅ Создана новая категория: {category_object.name} (ID: {category_object.id})")

    category_object.shops.add(shop.id)
    category_object.save()

    # Удаляем старые товары и загружаем новые
    ProductInfo.objects.filter(shop_id=shop.id).delete()
    for item in data.get('goods', []):
        product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
        product_info = ProductInfo.objects.create(
            product_id=product.id, external_id=item['id'],
            model=item['model'], price=item['price'],
            price_rrc=item['price_rrc'], quantity=item['quantity'],
            shop_id=shop.id
        )
        for name, value in item.get('parameters', {}).items():
            parameter_object, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.create(
                product_info_id=product_info.id, parameter_id=parameter_object.id, value=value
            )

    return {'Status': True}

