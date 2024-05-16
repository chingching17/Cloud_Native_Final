from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from .models import require_info
from django.http import JsonResponse

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

def add_order(request):
    if request.method == 'POST':

        factory = request.POST.get('factory')
        priority = request.POST.get('priority')
        lab = request.POST.get('laboratory')
       
        new_order = require_info(factory=factory, priority=priority, lab=lab)
        new_order.save()
        return redirect('/add')

    return render(request, 'add.html', {})