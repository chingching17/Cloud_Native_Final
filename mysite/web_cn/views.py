from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from .models import require_info
from django.http import JsonResponse
import json
from django.core.mail import send_mail
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

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

            send_notification(
                email='youremail@example.com',
                subject='Order Completed',
                message=f'Order with ID {request_id} has been completed.'
            )

            return redirect('/manage')

        except require_info.DoesNotExist:
            return JsonResponse({'error': 'Request does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'Error deleting request: ' + str(e)}, status=500)
        
def send_notification(email, subject, message):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

def view_logs(request):
    log_file_path = os.path.join(settings.BASE_DIR, 'logs/debug.log')
    with open(log_file_path, 'r') as file:
        log_content = file.readlines()

    search_query = request.GET.get('search', '')
    if search_query:
        log_content = [line for line in log_content if search_query in line]
    
    parsed_logs = []
    for line in log_content:
        parts = line.split(' ', 3)
        if len(parts) == 4:
            level, date, time, rest = parts
            module, message = rest.split(' ', 1)
            parsed_logs.append({
                'level': level,
                'time': f"{date} {time}",
                'module': module,
                'message': message,
            })

    return render(request, 'view_logs.html', {
        'log_content': parsed_logs,
        'search_query': search_query,
    })