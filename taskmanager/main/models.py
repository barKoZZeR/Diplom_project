from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings
from django.db import IntegrityError
from django.core.exceptions import ValidationError


# Модель для создания пользователей
class MyUserManager(BaseUserManager):
    # Создание обычного пользователя
    # Проверяется, есть ли у пользователя имя, если нет, то появляется ошибка
    def create_user(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    # Создание суперпользователя
    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)

        # Автоматически, суперпользователю присваивается роль "Суперпользователь"
        role, created = Role.objects.get_or_create(RoleName='Суперпользователь')
        extra_fields.setdefault('role', role)
        return self.create_user(username, password, **extra_fields)


# Модель для хранения ролей
class Role(models.Model):
    RoleName = models.CharField(max_length=255, unique=True, verbose_name="Название роли")

    def __str__(self):
        return self.RoleName

    def save(self, *args, **kwargs):
        try:
            super(Role, self).save(*args, **kwargs)
        except IntegrityError:
            raise ValidationError('Роль с таким названием уже существует.')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'


# Модель для хранения данных пользователя
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, verbose_name="Имя пользователя")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="Роль")
    last_login = models.DateTimeField(verbose_name='последний вход', null=True, blank=True) #default=timezone.now)
    first_name = models.CharField(max_length=30, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=150, blank=True, verbose_name="Отчество")
    email = models.EmailField(verbose_name="Адрес электронной почты", blank=True, null=True)
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона", blank=True, null=True)
    telegram = models.CharField(max_length=255, verbose_name="Telegram", blank=True, null=True)
    vk = models.CharField(max_length=255, verbose_name="VK", blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)


    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    # Определение статуса пользователя
    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True


# Профиль пользователя
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username


# Модель для создания объявлений или каких-либо общих задач
class Task(models.Model):
    title = models.CharField('Название', max_length=50)
    task = models.TextField('Описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'


# Модель продукта, который будет использоваться для создания планов
class Product(models.Model):
    ProductName = models.CharField(max_length=255, unique=True, verbose_name="Название продукта")

    def __str__(self):
        return self.ProductName

    def save(self, *args, **kwargs):
        try:
            super(Product, self).save(*args, **kwargs)
        except IntegrityError:
            raise ValidationError('Продукт с таким названием уже существует.')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


# Модель для плана продаж
class Plan(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    Quantity = models.IntegerField(verbose_name="Количество")
    Deadline = models.DateField(default=timezone.now, verbose_name="Крайний срок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="plan_creator", verbose_name="Создано пользователем")

    def get_total_sales(self):
        return sum(action.sales for action in self.actions.all())

    def __str__(self):
        return f"План для {self.User.username} на продукт {self.Product.ProductName}"


# Модель для записи сотрудником продаж
class Sale(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    Quantity = models.IntegerField(verbose_name="Количество проданного")
    SaleDate = models.DateField(verbose_name="Дата продажи")

    def __str__(self):
        return f"Продажа {self.Product.ProductName} пользователем {self.User.Username}"


# Действия сотрудника по заполнения плана
class Action(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='actions')
    date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    sales = models.IntegerField(verbose_name="Количество продаж")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    def __str__(self):
        return f"Действие от {self.date} для продукта {self.product}"
