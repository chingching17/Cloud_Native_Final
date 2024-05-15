from django.shortcuts import render
from django.db import connection
from django.contrib import messages

# Create your views here.
def index(request):
    return render(request, 'index.html', {})

def show_history(request):
	query = f'SELECT  * from web_cn_require_info'
	with connection.cursor() as cursor:
		cursor.execute(query)
		results = cursor.fetchall()
	return render(request, 'history.html', {'results': results})