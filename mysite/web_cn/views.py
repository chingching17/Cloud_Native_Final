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
from django.http import JsonResponse

logger = logging.getLogger('myapp')

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
            logger.info("Attachment found in request.")
        else:
            attachment = None
            logger.info("No attachment found in request.")

        try:
            new_order = require_info(
                factory=factory,
                priority=priority,
                lab=lab,
                current_priority='1',
                status='進行中',
                attachment=attachment
            )
            new_order.save()
            logger.info(f"New order created: {new_order}")
            return redirect('/add')
        except Exception as e:
            logger.error(f"Error creating new order: {str(e)}")
            return render(request, 'add.html', {'error': 'Error creating new order.'})

    return render(request, 'add.html', {})

def delete_order(request):

    logger.debug("delete_order function called")
    if request.method == 'POST':
        json_data = json.loads(request.body)
        request_id = json_data.get('request_id')
        logger.info(f"Request to delete order with ID: {request_id}")

        try:
            
            request_to_delete = require_info.objects.get(req_id=request_id)
            request_to_delete.delete()
            logger.info(f"Order with ID {request_id} deleted successfully")

            return redirect('/manage')

        except require_info.DoesNotExist:
            logger.warning(f"Order with ID {request_id} does not exist")
            return JsonResponse({'error': 'Request does not exist'}, status=404)
        except Exception as e:
            logger.error(f"Error deleting order with ID {request_id}: {str(e)}")
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
            logger.info(f"Notification sent for order ID {request_id}")

            return redirect('/manage')

        except require_info.DoesNotExist:
            logger.warning(f"Order with ID {request_id} does not exist")
            return JsonResponse({'error': 'Request does not exist'}, status=404)
        except Exception as e:
            logger.error(f"Error completing order with ID {request_id}: {str(e)}")
            return JsonResponse({'error': 'Error deleting request: ' + str(e)}, status=500)
        
def send_notification(email, subject, message):
    logger.info(f"Sending email to {email} with subject '{subject}'")
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")

def view_logs(request):
    log_file_path = os.path.join(settings.BASE_DIR, 'logs/debug.log')
    with open(log_file_path, 'r') as file:
        log_content = file.readlines()
    
    search_query = request.GET.get('search', '')
    reverse_order = request.GET.get('reverse', 'false') == 'true'
    
    if search_query:
        log_content = [line for line in log_content if search_query in line]
    
    if reverse_order:
        log_content = log_content[::-1]
    
    log_entries = []
    for log in log_content:
        parts = log.split(' ', 3)  # Assuming log format: <LEVEL> <TIME> <MODULE> <MESSAGE>
        if len(parts) == 4:
            log_entries.append({
                'level': parts[0],
                'time': parts[1] + ' ' + parts[2],
                'module': parts[3].split()[0],
                'message': ' '.join(parts[3].split()[1:])
            })
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(log_entries, safe=False)
    
    return render(request, 'view_logs.html', {
        'log_content': log_entries,
        'search_query': search_query,
        'reverse_order': reverse_order,
    })