from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.http import require_POST
from datetime import timedelta
from collections import OrderedDict


def login_view(request):
    if request.session.get('user_id'):
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                if user.is_active:
                    user.last_login = timezone.now()
                    user.save(update_fields=['last_login'])
                    request.session['user_id'] = user.id  # Stocke l'ID de l'utilisateur dans la session
                    return redirect('home')
                else:
                    return render(request, 'auth/login.html', {'error': 'User is inactive'})
            else:
                return render(request, 'auth/login.html', {'error': 'Invalid credentials'})
        except User.DoesNotExist:
            return render(request, 'auth/login.html', {'error': 'User does not exist'})
    return render(request, 'auth/login.html')


def register_view(request):
    if request.session.get('user_id'):
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        date_of_birth = request.POST.get('date_of_birth')
        role = request.POST.get('role', 'user')
        profile_picture = request.FILES.get('profile_picture')

        if not all([username, password, email, first_name, last_name, date_of_birth]):
            return render(request, 'auth/register.html', {'error': 'All fields are required'})

        if User.objects.filter(username=username).exists():
            return render(request, 'auth/register.html', {'error': 'Username already exists'})
        if User.objects.filter(email=email).exists():
            return render(request, 'auth/register.html', {'error': 'Email already exists'})

        hashed_password = make_password(password)
        user = User(
            username=username,
            password=hashed_password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            role=role
        )

        if date_of_birth:
            user.date_of_birth = date_of_birth
        if profile_picture:
            user.profile_picture = profile_picture

        user.save()
        request.session['user_id'] = user.id  # Connecte l'utilisateur nouvellement inscrit
        return redirect('home')
    return render(request, 'auth/register.html')


def get_current_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    return None


def dashboard_view(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    actions = Action.objects.filter(user=user, isDeleted=False).order_by('-timestamp')[:5]
    tasks = Task.objects.filter(assigned_to=user, isDeleted=False).order_by('-created_at')[:5]
    pensees = Pensee_Bete.objects.filter(user=user, isDeleted=False).order_by('-created_at')[:5]
    links = Link.objects.filter(user=user, isDeleted=False).order_by('-created_at')[:5]

    # Préparation des données pour les graphiques (30 derniers jours)
    today = timezone.now().date()
    days = [today - timedelta(days=i) for i in range(29, -1, -1)]
    labels = [d.strftime("%d/%m") for d in days]

    def count_by_day(qs, date_field):
        counts = OrderedDict((d, 0) for d in days)
        for obj in qs:
            date = getattr(obj, date_field).date()
            if date in counts:
                counts[date] += 1
        return list(counts.values())

    actions_qs = Action.objects.filter(user=user, isDeleted=False, timestamp__date__gte=days[0])
    tasks_qs = Task.objects.filter(assigned_to=user, isDeleted=False, created_at__date__gte=days[0])
    pensees_qs = Pensee_Bete.objects.filter(user=user, isDeleted=False, created_at__date__gte=days[0])
    links_qs = Link.objects.filter(user=user, isDeleted=False, created_at__date__gte=days[0])

    actions_data = count_by_day(actions_qs, "timestamp")
    tasks_data = count_by_day(tasks_qs, "created_at")
    pensees_data = count_by_day(pensees_qs, "created_at")
    links_data = count_by_day(links_qs, "created_at")

    # Statut des tâches (pie chart)
    from .models import TaskStatus
    status_labels = [label for _, label in TaskStatus.choices]
    status_keys = [key for key, _ in TaskStatus.choices]
    status_counts = []
    for key in status_keys:
        status_counts.append(Task.objects.filter(assigned_to=user, isDeleted=False, status=key).count())

    return render(request, 'dashboard.html', {
        'user': user,
        'actions': actions,
        'tasks': tasks,
        'pensees': pensees,
        'links': links,
        'chart_labels': labels,
        'actions_data': actions_data,
        'tasks_data': tasks_data,
        'pensees_data': pensees_data,
        'links_data': links_data,
        'tasks_status_labels': status_labels,
        'tasks_status_data': status_counts,
    })


def logout_view(request):
    request.session.flush()
    return redirect('login')

# ACTIONS
def action_list(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    actions = Action.objects.filter(user=user, isDeleted=False).order_by('-timestamp')
    return render(request, 'actions/list.html', {'actions': actions, 'user': user})

def action_create(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    if request.method == 'POST':
        title = request.POST.get('action_title')
        description = request.POST.get('description', '')
        if title:
            Action.objects.create(user=user, action_title=title, description=description)
            return redirect('action_list')
    return render(request, 'actions/create.html', {'user': user})

def action_delete(request, action_id):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    action = Action.objects.filter(id=action_id, user=user).first()
    if action:
        action.isDeleted = True
        action.save()
    return redirect('action_list')

# TASKS
def task_list(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    tasks = Task.objects.filter(assigned_to=user, isDeleted=False).order_by('-created_at')
    return render(request, 'tasks/list.html', {'tasks': tasks, 'user': user})

def task_create(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        status = request.POST.get('status', TaskStatus.PENDING)
        if title:
            Task.objects.create(title=title, description=description, assigned_to=user, status=status)
            return redirect('task_list')
    return render(request, 'tasks/create.html', {'user': user, 'statuses': TaskStatus.choices})

def task_update_status(request, task_id):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    task = Task.objects.filter(id=task_id, assigned_to=user, isDeleted=False).first()
    if request.method == 'POST' and task:
        status = request.POST.get('status')
        if status in dict(TaskStatus.choices):
            task.status = status
            task.save()
    return redirect('task_list')

def task_delete(request, task_id):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    task = Task.objects.filter(id=task_id, assigned_to=user).first()
    if task:
        task.isDeleted = True
        task.save()
    return redirect('task_list')

# PENSEE BETE
def pensee_bete_list(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    pensees = Pensee_Bete.objects.filter(user=user, isDeleted=False).order_by('-created_at')
    return render(request, 'pensees/list.html', {'pensees': pensees, 'user': user})

def pensee_bete_create(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Pensee_Bete.objects.create(user=user, content=content)
            return redirect('pensee_bete_list')
    return render(request, 'pensees/create.html', {'user': user})

def pensee_bete_delete(request, pensee_id):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    pensee = Pensee_Bete.objects.filter(id=pensee_id, user=user).first()
    if pensee:
        pensee.isDeleted = True
        pensee.save()
    return redirect('pensee_bete_list')

# LINKS
def link_list(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    links = Link.objects.filter(user=user, isDeleted=False).order_by('-created_at')
    return render(request, 'links/list.html', {'links': links, 'user': user})

def link_create(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    if request.method == 'POST':
        url = request.POST.get('url')
        description = request.POST.get('description', '')
        if url:
            Link.objects.create(user=user, url=url, description=description)
            return redirect('link_list')
    return render(request, 'links/create.html', {'user': user})

def link_delete(request, link_id):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    link = Link.objects.filter(id=link_id, user=user).first()
    if link:
        link.isDeleted = True
        link.save()
    return redirect('link_list')