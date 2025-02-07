from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from backend.models import User, Shop, Product, Category, ProductParameter, ProductInfo, Parameter, OrderItem, Order, Contact, ConfirmEmailToken

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = (
        (None, {'fields': ('email', 'password', 'type', 'avatar')}),  # Добавили avatar
        ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'position')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (  # Позволяет добавлять пользователя с аватаром сразу
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'type', 'avatar'),
        }),
    )

    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff', 'get_avatar_thumbnail')
    search_fields = ('first_name', 'last_name')
    list_filter = ('last_name', 'is_staff')

    def get_avatar_thumbnail(self, obj):
        """ Отображает миниатюру аватара в списке пользователей """
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:50%;" />',
                obj.avatar.crop['100x100'].url
            )
        return "Нет аватара"

    get_avatar_thumbnail.short_description = "Аватар"


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    model = Shop
    fieldsets = (
        (None, {'fields': ('name', 'state')}),
        ('Additional Info', {'fields': ('url', 'user')}),
    )
    list_display = ('id','name', 'state', 'url')
    search_fields = ('name',)
    list_filter = ('state',)
    list_editable = ('state',)

class ProductInline(admin.TabularInline):
    model = Product
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category
    inlines = [ProductInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    model = Product
    fieldsets = (
        (None, {'fields': ('name', 'category', 'image')}),
    )
    list_display = ('id', 'name', 'category', 'get_thumbnail')
    search_fields = ('name', 'category')

    def get_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "Нет изображения"

    get_thumbnail.short_description = "Миниатюра"
    get_thumbnail.allow_tags = True

class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 1


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    model = ProductInfo
    fieldsets = (
        (None, {'fields': ('product', 'model', 'external_id', 'quantity', 'shop')}),
        ('Цены', {'fields': ('price', 'price_rrc')}),
    )
    list_display = ('id','product','external_id', 'price', 'price_rrc', 'quantity', 'shop')
    list_filter = ('model',)
    inlines = [ProductParameterInline]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    pass


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    model = Order
    fields = ('user', 'state', 'contact', 'date')
    list_display = ('id', 'user', 'date', 'state')
    inlines = [OrderItemInline,]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'phone')
    search_fields = ('city',)

@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at',)
    search_fields = ('user',)
    list_filter = ('created_at',)
