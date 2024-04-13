from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task, User, Plan, Action, Role
from .forms import TaskForm, UserProfileForm, PlanForm, ActionForm
from django.core.paginator import Paginator
from django.db.models import Count


# Отображение страницы с планами сотрудника, которую может видеть только руководитель
@login_required
def employers_plans(request):
    if request.user.is_authenticated and request.user.role.RoleName == "Руководитель":
        managers = User.objects.filter(role__RoleName="Менеджер")
        return render(request, 'main/employers_plans.html', {'managers': managers})
    else:
        return redirect('home')

# Отображение профиля сотрудника с его планами + разграничение доступа к планам
@login_required
def employee_profile(request, user_id):
    employee = get_object_or_404(User, id=user_id)

    if request.user == employee or request.user.role.RoleName == "Руководитель":
        plans = Plan.objects.filter(User=employee)
        actions = Action.objects.filter(plan__User=employee)
    else:
        plans = None
        actions = None

    return render(request, 'main/employee_profile.html', {
        'employee': employee,
        'plans': plans,
        'actions': actions
    })


# Создание плана руководителем для сотрудника
@login_required
def create_plan_for_employee(request, user_id):
    employee = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = PlanForm(request.POST, request=request, user=employee)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.User = employee
            plan.save()
            return redirect('employers_plans')
    else:
        form = PlanForm(request=request, user=employee)
    return render(request, 'main/create_plan.html', {'form': form, 'employee': employee})


# Отображение профиля текущего пользователя
@login_required
def current_user_profile(request):
    return render(request, 'main/profile.html', {'user': request.user})


# Главная страница. Если пользователь залогинился под Администратором - он переадресовывается в админ-панель
@login_required
def index(request):
    if request.user.is_superuser:
        return redirect('/admin')

    roles_with_users = Role.objects.annotate(user_count=Count('user')).filter(user_count__gt=0).exclude(
        RoleName="Суперпользователь")

    tasks = Task.objects.all()
    return render(request, 'main/index.html', {
        'title': 'Главная страница сайта',
        'roles_with_users': roles_with_users,
        'tasks': tasks
    })


# Отображение плана продаж сотрудника
@login_required
def my_plan(request):
    plans = Plan.objects.filter(User=request.user).order_by('-Deadline')
    return render(request, 'main/my_plan.html', {'plans': plans})


# Страница профиля пользователя
@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'main/profile.html', {'form': form})


# Создание объявления руководителем
@login_required
def create(request):
    error = ''
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            error = 'Форма была неверной'

    form = TaskForm()
    context ={
        'form': form,
        'error': error
    }
    return render(request, 'main/create.html', context)


# Заполнение плана сотрудником
@login_required
def add_action(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id)
    plan_year = plan.Deadline.year
    plan_creation_date = plan.created_at.date()

    if request.method == "POST":
        form = ActionForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.plan = plan
            plan.save()
            action.product = plan.Product
            action.save()
            return redirect('view_plan', plan_id=plan.id)
    else:
        form = ActionForm()
    return render(request, 'main/add_action.html', {'form': form, 'plan': plan, 'plan_year': plan_year, 'plan_creation_date': plan_creation_date.strftime('%Y-%m-%d')})


# Просмотр плана и каких либо действий связанных с ним
@login_required
def view_plan(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id)
    actions = Action.objects.filter(plan=plan).order_by('date')

    paginator = Paginator(actions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/view_plan.html', {'plan': plan, 'actions': actions, 'page_obj': page_obj})