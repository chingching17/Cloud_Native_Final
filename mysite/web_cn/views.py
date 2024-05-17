from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from .models import require_info
from django.http import JsonResponse
import json

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout



# Create your views here.
def index(request):
    return render(request, 'index.html', {})

def show_history(request):
	query = f'SELECT  * from web_cn_require_info ORDER BY req_id'
	with connection.cursor() as cursor:
		cursor.execute(query)
		results = cursor.fetchall()
	return render(request, 'history.html', {'results': results})

def add(request):
    return render(request, 'add.html', {})

def manage(request):
	query = f'SELECT  * from web_cn_require_info ORDER BY priority'
	with connection.cursor() as cursor:
		cursor.execute(query)
		results = cursor.fetchall()
	return render(request, 'manage.html', {'results': results})

def add_order(request):
    if request.method == 'POST':

        factory = request.POST.get('factory')
        priority = request.POST.get('priority')
        lab = request.POST.get('laboratory')

        if 'attachment' in request.FILES:
            attachment = request.FILES['attachment']
        else:
            attachment = None

        new_order = require_info(factory=factory, priority=priority, lab=lab, current_priority='1', status='進行中', attachment=attachment)
        new_order.save()
        return redirect('/add')

    return render(request, 'add.html', {})

def delete_order(request):
    if request.method == 'POST':

        json_data = json.loads(request.body)
        request_id = json_data.get('request_id')

        try:
            
            request_to_delete = require_info.objects.get(req_id=request_id)
            request_to_delete.delete()

            return redirect('/manage')

        except require_info.DoesNotExist:
            return JsonResponse({'error': 'Request does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'Error deleting request: ' + str(e)}, status=500)

def complete_order(request):
    if request.method == 'POST':

        json_data = json.loads(request.body)
        request_id = json_data.get('request_id')

        try:
            
            request_to_complete = require_info.objects.get(req_id=request_id)
            request_to_complete.status = '完成'
            request_to_complete.save()

            return redirect('/manage')

        except require_info.DoesNotExist:
            return JsonResponse({'error': 'Request does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'Error deleting request: ' + str(e)}, status=500)

# feat/2approval
# login page and register page
@csrf_protect
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/register')  
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/login')  # 導向首頁或其他頁面
    else:
        form = AuthenticationForm()

    # 查詢所有使用者
    users = User.objects.all().values_list('username', flat=True)
    return render(request, 'login.html', {'form': form, 'users': users})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def index(request):
    return render(request, 'index.html', {'current_user': request.user})