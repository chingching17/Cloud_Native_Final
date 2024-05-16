from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from .models import require_info
from django.http import JsonResponse
import json

# Create your views here.
def index(request):
    return render(request, 'index.html', {})

def show_history(request):
	query = f'SELECT  * from web_cn_require_info'
	with connection.cursor() as cursor:
		cursor.execute(query)
		results = cursor.fetchall()
	return render(request, 'history.html', {'results': results})

def add(request):
    return render(request, 'add.html', {})

def manage(request):
	query = f'SELECT  * from web_cn_require_info'
	with connection.cursor() as cursor:
		cursor.execute(query)
		results = cursor.fetchall()
	return render(request, 'manage.html', {'results': results})

def add_order(request):
    if request.method == 'POST':

        factory = request.POST.get('factory')
        priority = request.POST.get('priority')
        lab = request.POST.get('laboratory')
       
        new_order = require_info(factory=factory, priority=priority, lab=lab)
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