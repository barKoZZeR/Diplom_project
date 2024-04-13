from .models import Task, Sale, Plan, Action, Product, User
from django.forms import ModelForm, TextInput, Textarea, DateInput
from django import forms
from .models import User
import datetime
from django.core.exceptions import ValidationError

# Форма для редактирования профиля
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'telegram', 'vk']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram': forms.TextInput(attrs={'class': 'form-control'}),
            'vk': forms.TextInput(attrs={'class': 'form-control'}),
        }


# Форма для создания и редактирования планов продаж
class PlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        super(PlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Plan
        fields = ['Product', 'Quantity', 'Deadline']
        widgets = {
            'Deadline': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'min': datetime.date.today().strftime('%Y-%m-%d')
                }
            ),
        }

    # Проверка существования планов по одному продукту в том же квартале
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("Product")
        deadline = cleaned_data.get("Deadline")
        user = self.user

        if product and deadline and user:
            quarter = (deadline.month - 1) // 3 + 1
            quarter_start_month = (quarter - 1) * 3 + 1
            quarter_end_month = quarter * 3
            year = deadline.year
            start_date = datetime.date(year, quarter_start_month, 1)
            end_date = datetime.date(year, quarter_end_month, {
                1: 31, 2: 30, 3: 30, 4: 31
            }[quarter])

            if Plan.objects.filter(Product=product, Deadline__range=(start_date, end_date), User=user).exists():
                raise ValidationError(f"План на продукт '{product}' уже существует для этого пользователя в данном квартале.")

        return cleaned_data


# Форма для создания
class SaleForm(ModelForm):
    class Meta:
        model = Sale
        fields = ['Product', 'Quantity', 'SaleDate', 'User']
        widgets = {
            'Deadline': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

# Форма для создания объявлений или каких-либо общих задач
class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ["title", "task"]
        widgets = {
            "title": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название'
            }),
            "task": Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите описание'
            })
        }


# Форма для заполнения плана сотрудником
class ActionForm(forms.ModelForm):

    class Meta:
        model = Action
        fields = ['date', 'sales', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sales': forms.NumberInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }