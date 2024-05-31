from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import connection
from django.contrib import messages

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
import json
import os
import logging
from .models import require_info
from .forms import CustomUserCreationForm
from .tasks import send_notification

logger = logging.getLogger('myapp')

# Create your views here.
@login_required
def user_list(request):
    users = User.objects.all().values('username', 'email', 'groups__name')
    return render(request, 'user_list.html', {'users': users})

@login_required
def group_members(request):
    chemistry_lab = Group.objects.filter(name='化學實驗室').first()
    surface_analysis_lab = Group.objects.filter(name='表面分析實驗室').first()
    composition_analysis_lab = Group.objects.filter(name='成分分析實驗室').first()

    chemistry_lab_users = chemistry_lab.user_set.all() if chemistry_lab else None
    surface_analysis_lab_users = surface_analysis_lab.user_set.all() if surface_analysis_lab else None
    composition_analysis_lab_users = composition_analysis_lab.user_set.all() if composition_analysis_lab else None

    return render(request, 'group_members.html', {
        'chemistry_lab_users': chemistry_lab_users,
        'surface_analysis_lab_users': surface_analysis_lab_users,
        'composition_analysis_lab_users': composition_analysis_lab_users,
    })
    
@csrf_protect
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # username = form.cleaned_data.get('username')
            # raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=raw_password)
            # login(request, user)
            return redirect('login')  # Redirect to index or any other page
    else:
        form = CustomUserCreationForm()
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
                return redirect('manage')  # Redirect to index or any other page
    else:
        form = AuthenticationForm()

    users = User.objects.all().values_list('username', flat=True)
    return render(request, 'login.html', {'form': form, 'users': users})

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

# @login_required
def index(request):
    return render(request, 'index.html', {})

def show_history(request):
	query = 'SELECT * FROM web_cn_require_info ORDER BY req_id'
	with connection.cursor() as cursor:
		cursor.execute(query)
		results = cursor.fetchall()

	paginator = Paginator(results, 10)
	page = request.GET.get('page', 1)

	try:
		paginated_results = paginator.page(page)
	except PageNotAnInteger:
		paginated_results = paginator.page(1)
	except EmptyPage:
		paginated_results = paginator.page(paginator.num_pages)

	context = { 'results': paginated_results,  
                'total_count' : len(results),
                'ongoing_count': sum(1 for row in results if row[5] == '進行中')}

	return render(request, 'history.html', context)

def add(request):
    return render(request, 'add.html', {})

def manage(request):
	query = 'SELECT * FROM web_cn_require_info ORDER BY current_priority'
	with connection.cursor() as cursor:
		cursor.execute(query)
		results = cursor.fetchall()

	paginator = Paginator(results, 10)
	page = request.GET.get('page', 1)

	try:
		paginated_results = paginator.page(page)
	except PageNotAnInteger:
		paginated_results = paginator.page(1)
	except EmptyPage:
		paginated_results = paginator.page(paginator.num_pages)

	context = { 'results': paginated_results, 
                'fab_a_count' : sum(1 for row in results if row[1] == 'Fab A'),
                'fab_b_count' : sum(1 for row in results if row[1] == 'Fab B'),
                'fab_c_count' : sum(1 for row in results if row[1] == 'Fab C'),
                'ongoing_count': sum(1 for row in results if row[5] == '進行中')}

	return render(request, 'manage.html', context)

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
                current_priority='10',
                status='進行中',
                attachment=attachment
            )
            new_order.save()
            logger.info(f"New order created: {new_order.req_id} by user {request.user.username}")
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
        logger.info(f"User {request.user.username} requested to delete order with ID: {request_id}")

        try:
            request_to_delete = require_info.objects.get(req_id=request_id)
            request_to_delete.delete()
            logger.info(f"Order with ID {request_id} deleted successfully by user {request.user.username}")
            
            user_email = request.user.email

            send_notification(
                email=user_email,
                subject='Order Deleted',
                message=f'Order with ID {request_id} has been deleted.'
            )

            response_data = {'redirect_url': '/manage'}
            return JsonResponse(response_data)

        except require_info.DoesNotExist:
            logger.warning(f"Order with ID {request_id} does not exist")
            return JsonResponse({'error': 'Request does not exist'}, status=404)
        except Exception as e:
            logger.error(f"Error deleting order with ID {request_id}: {str(e)}")
            return JsonResponse({'error': 'Error deleting request: ' + str(e)}, status=500)

def decrease_priority(request):
    if request.method == 'POST':

        try:

            json_data = json.loads(request.body)
            request_id = json_data.get('request_id')
            logger.info(f"User {request.user.username} requested to decrease priority for ID: {request_id}")

            if not connection:
                logger.error("Database connection not available")
                return HttpResponseBadRequest("Database connection not available")

            query = "UPDATE web_cn_require_info SET current_priority = current_priority + 1 WHERE req_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(query, (request_id,))
                logger.info(f"User {request.user.username} successfully increased priority for ID: {request_id}")

            response_data = {'redirect_url': '/manage'}
            return JsonResponse(response_data)
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON from request")
            return HttpResponseBadRequest("Invalid JSON")
        except Exception as e:
            logger.error(f"Error processing decrease priority request: {str(e)}")
            return HttpResponseBadRequest(f"Error: {str(e)}")
        
    else:
        logger.warning("Invalid request method")
        return HttpResponseBadRequest("Invalid request method")
    
def increase_priority(request):
    if request.method == 'POST':

        try:

            json_data = json.loads(request.body)
            request_id = json_data.get('request_id')
            logger.info(f"User {request.user.username} requested to increase priority for ID: {request_id}")

            if not connection:
                logger.error("Database connection not available")
                return HttpResponseBadRequest("Database connection not available")

            query = "UPDATE web_cn_require_info SET current_priority = current_priority - 1 WHERE req_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(query, (request_id,))
                logger.info(f"User {request.user.username} successfully increase priority for ID: {request_id}")

            response_data = {'redirect_url': '/manage'}
            return JsonResponse(response_data)
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON from request")
            return HttpResponseBadRequest("Invalid JSON")
        except Exception as e:
            logger.error(f"Error processing decrease priority request: {str(e)}")
            return HttpResponseBadRequest(f"Error: {str(e)}")
        
    else:
        logger.warning("Invalid request method")
        return HttpResponseBadRequest("Invalid request method")

@csrf_exempt
@login_required
def complete_order(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        request_id = json_data.get('request_id')

        try:
            task = get_object_or_404(require_info, req_id=request_id)

            if task.lab not in [group.name for group in request.user.groups.all()]:
                return JsonResponse({'error': 'You are not authorized to complete this order.'}, status=403)

            if task.is_submitted and task.completed_by is None:
                if task.submitted_by == request.user:
                    return JsonResponse({'error': 'You cannot complete this task because you have already submitted it.'}, status=403)
                task.is_completed = True
                task.completed_by = request.user
                task.status = '完成'
                task.save()

                logger.info(f"Order with ID {request_id} is completed. (Approved by user {request.user.username})")
                
                user_email = request.user.email

                send_notification(
                    email=user_email,
                    subject='Order Completed',
                    message=f'Order with ID {request_id} has been completed.'
                )

                return JsonResponse({'is_completed': task.is_completed, 'status': task.status})
            else:
                return JsonResponse({'error': 'This task cannot be completed yet.'}, status=403)

        except require_info.DoesNotExist:
            logger.warning(f"Order with ID {request_id} does not exist")
            return JsonResponse({'error': 'Request does not exist'}, status=404)
        except Exception as e:
            logger.error(f"Error completing order with ID {request_id}: {str(e)}")
            return JsonResponse({'error': 'Error deleting request: ' + str(e)}, status=500)


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

# # feat/2approval
# def approve_task(request, task_id):
#     task = get_object_or_404(Task, id=task_id)
#     if task.approval > 0:
#         task.approval -= 1
#         if task.approval == 0:
#             task.is_completed = True
#         task.save()
#     return JsonResponse({'approval': task.approval, 'is_completed': task.is_completed})

@csrf_exempt
@login_required
def submit_order(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        request_id = json_data.get('request_id')

        try:
            task = get_object_or_404(require_info, req_id=request_id)

            if task.lab not in [group.name for group in request.user.groups.all()]:
                return JsonResponse({'error': 'You are not authorized to submit this order.'}, status=403)

            if task.submitted_by is None:
                # if task.completed_by == request.user:
                #     return JsonResponse({'error': 'You cannot submit this task because you have already completed it.'}, status=403)
                task.is_submitted = True
                task.submitted_by = request.user
                task.save()

                logger.info(f"Order with ID {request_id} submitted by user {request.user.username}")

                user_email = request.user.email

                send_notification(
                    email=user_email,
                    subject='Order Submitted',
                    message=f'Order with ID {request_id} has been submitted.'
                )

                return JsonResponse({'is_submitted': task.is_submitted})
            else:
                return JsonResponse({'error': 'This task has already been submitted.'}, status=403)

        except require_info.DoesNotExist:
            return JsonResponse({'error': 'Request does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'Error submitting request: ' + str(e)}, status=500)
