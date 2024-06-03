from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from web_cn.models import require_info
import json
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.paginator import Page, Paginator
from django.http import HttpRequest
from django.db import connection
from web_cn.views import show_history, manage, add_order
from unittest.mock import Mock, patch, MagicMock
from django.http import JsonResponse, HttpResponseBadRequest
import os

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.client.login(username='testuser', password='password123')

    def test_user_list_view(self):
        response = self.client.get(reverse('user_list'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_group_members_view(self):
        response = self.client.get(reverse('group_members'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_members.html')

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertEquals(response.status_code, 302)  # Redirects to index page

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    # Add more tests for other views as needed

    def test_show_history(self):
        client = Client()
        url = reverse('show_history')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'history.html')

    def test_add(self):
        client = Client()
        url = reverse('add')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add.html')

    def test_manage(self):
        client = Client()
        url = reverse('manage')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage.html')

    def test_pagination(self):
        client = Client()
        url = reverse('manage')
        
        # Send a GET request for page 2
        response = client.get(url, {'page': 2})
        
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Check if the correct template is being used
        self.assertTemplateUsed(response, 'manage.html')
        
        # Check if the context data contains a 'results' attribute and it is an instance of Page
        self.assertIn('results', response.context)
        self.assertIsInstance(response.context['results'], Page)



class AddOrderViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a user belonging to 'Fab A' group
        self.user_fab_a = User.objects.create_user(username='user_fab_a', password='password')
        fab_a_group = Group.objects.create(name='Fab A')
        self.user_fab_a.groups.add(fab_a_group)
        # Create a user not belonging to any allowed group
        self.user_unauthorized = User.objects.create_user(username='user_unauthorized', password='password')

    def test_get_request(self):
        # Send a GET request, should render 'add.html'
        response = self.client.get(reverse('add_order'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add.html')

    def test_unauthorized_post_request(self):
        # Send a POST request as an unauthorized user
        self.client.force_login(self.user_unauthorized)
        response = self.client.post(reverse('add_order'))
        # Should return a JSON response with status code 403 (Forbidden)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'error': 'You are not authorized to add an order.'})

# class AddOrderTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user_fab_a = User.objects.create_user(username='user_fab_a', password='password')
#         self.user_fab_a.groups.create(name='Fab A')

#     def test_authorized_post_request(self):
#         # Send a POST request as an authorized user (user belonging to 'Fab A' group)
#         self.client.force_login(self.user_fab_a)
#         data = {
#             'factory': 'Factory A',
#             'priority': '特急單',
#             'laboratory': 'Lab A',
#         }
#         response = self.client.post(reverse('add_order'), data=data)
#         # Should return a JSON response with status code 201 (Created)
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.json(), {'success': True})



class TestDeleteOrderView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.order = require_info.objects.create(factory='TestF', priority='Test Priority', lab='Test Lab', current_priority=1, status='Test Status')

    @patch('web_cn.views.send_notification')
    def test_delete_order(self, mock_send_notification):
        # Log in as the user
        self.client.force_login(self.user)
        
        # Send a POST request to delete the order
        url = reverse('delete_order')
        data = {'request_id': self.order.req_id}
        response = self.client.post(url, data=data, content_type='application/json')
        
        # Check if the order is deleted
        self.assertEqual(response.status_code, 200)
        self.assertFalse(require_info.objects.filter(req_id=self.order.req_id).exists())
        
        # Check if notification is sent
        mock_send_notification.assert_called_once_with(email=self.user.email, subject='Order Deleted', message=f'Order with ID {self.order.req_id} has been deleted.')

class TestDecreasePriorityView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_valid_post_request(self):
        # Simulate a valid POST request with proper JSON data
        request_data = {'request_id': 123}
        response = self.client.post(reverse('decrease_priority'), data=request_data, content_type='application/json')

        # Check that the response is a JSON response with a redirect URL
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf-8'), {'redirect_url': '/manage'})

    def test_invalid_post_request_invalid_json(self):
        # Simulate a POST request with invalid JSON data
        response = self.client.post(reverse('decrease_priority'), data='Invalid JSON', content_type='application/json')

        # Check that the response is a bad request response
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.status_code, 400)

    def test_invalid_request_method(self):
        # Simulate a GET request instead of POST
        response = self.client.get(reverse('decrease_priority'))

        # Check that the response is a bad request response
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.status_code, 400)

class TestIncreasePriorityView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_valid_post_request(self):
        # Simulate a valid POST request with proper JSON data
        request_data = {'request_id': 123}
        response = self.client.post(reverse('increase_priority'), data=request_data, content_type='application/json')

        # Check that the response is a JSON response with a redirect URL
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf-8'), {'redirect_url': '/manage'})

    def test_invalid_post_request_invalid_json(self):
        # Simulate a POST request with invalid JSON data
        response = self.client.post(reverse('increase_priority'), data='Invalid JSON', content_type='application/json')

        # Check that the response is a bad request response
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.status_code, 400)

    def test_invalid_request_method(self):
        # Simulate a GET request instead of POST
        response = self.client.get(reverse('increase_priority'))

        # Check that the response is a bad request response
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.status_code, 400)

class TestCompleteOrderView(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a user
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')

        # Create a group and add the user to it
        self.group = Group.objects.create(name='Fab A')
        self.user.groups.add(self.group)

        # Create a require_info instance
        self.task = require_info.objects.create(
            factory='Fab A',
            priority='High',
            lab='Test Lab',
            current_priority=1,
            status='In Progress',
            is_submitted=True,
            submitted_by=self.user
        )

    # def test_complete_order_valid(self):
    #     # Test completing a task as an authorized user
    #     self.client.force_login(self.user)
    #     request_data = {'request_id': self.task.req_id}
    #     response = self.client.post(reverse('complete_order'), data=json.dumps(request_data), content_type='application/json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(response.json()['is_completed'])
    #     self.assertEqual(response.json()['status'], '完成')

    def test_complete_order_unauthorized(self):
        # Test completing a task by a user not authorized for that group
        unauthorized_user = User.objects.create_user(username='unauthorized', email='unauthorized@example.com', password='password')
        self.client.force_login(unauthorized_user)
        request_data = {'request_id': self.task.req_id}
        response = self.client.post(reverse('complete_order'), data=json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    # def test_complete_order_already_submitted(self):
    #     # Test completing a task that is already submitted
    #     self.task.is_completed = False
    #     self.task.completed_by = None
    #     self.task.save()
    #     request_data = {'request_id': self.task.req_id}
    #     response = self.client.post(reverse('complete_order'), data=json.dumps(request_data), content_type='application/json')
    #     self.assertEqual(response.status_code, 403)

    # def test_complete_order_nonexistent_task(self):
    #     # Test completing a nonexistent task
    #     nonexistent_id = self.task.req_id + 1
    #     request_data = {'request_id': nonexistent_id}
    #     response = self.client.post(reverse('complete_order'), data=json.dumps(request_data), content_type='application/json')
    #     self.assertEqual(response.status_code, 404)

class TestViewLogs(TestCase):
    def setUp(self):
        self.client = Client()

    def test_view_logs_regular_request(self):
        # Test when the request is made via regular HTTP
        response = self.client.get(reverse('view_logs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_logs.html')

    @patch('web_cn.views.open', create=True)
    def test_view_logs_ajax_request(self, mock_open):
        # Test when the request is made via AJAX (XMLHttpRequest)
        mock_file_content = [
            "INFO 2024-06-10 15:30:45 views.py This is a log message",
            "ERROR 2024-06-10 15:32:20 models.py Another log message"
        ]
        mock_open.return_value.__enter__.return_value.readlines.return_value = mock_file_content

        response = self.client.get(reverse('view_logs'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)

        log_entries = response.json()
        self.assertEqual(len(log_entries), 2)
        self.assertEqual(log_entries[0]['level'], 'INFO')
        self.assertEqual(log_entries[0]['time'], '2024-06-10 15:30:45')
        self.assertEqual(log_entries[0]['module'], 'views.py')
        self.assertEqual(log_entries[0]['message'], 'This is a log message')

        self.assertEqual(log_entries[1]['level'], 'ERROR')
        self.assertEqual(log_entries[1]['time'], '2024-06-10 15:32:20')
        self.assertEqual(log_entries[1]['module'], 'models.py')
        self.assertEqual(log_entries[1]['message'], 'Another log message')

# class TestSubmitOrderView(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#         self.user.groups.create(name='Lab A')
#         self.task = require_info.objects.create(factory='Fab A', priority='Priority A', lab='Lab A')

#     def test_submit_order_success(self):
#         # Test when the order submission is successful
#         self.client.force_login(self.user)
#         data = {'request_id': self.task.req_id}
#         response = self.client.post(reverse('submit_order'), data=json.dumps(data), content_type='application/json')
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(response.json()['is_submitted'])
#         # Check if the task object is updated
#         self.task.refresh_from_db()
#         self.assertTrue(self.task.is_submitted)
#         self.assertEqual(self.task.submitted_by, self.user)

#     def test_submit_order_already_submitted(self):
#         # Test when the order has already been submitted
#         self.task.submitted_by = self.user
#         self.task.save()
#         self.client.force_login(self.user)
#         data = {'request_id': self.task.req_id}
#         response = self.client.post(reverse('submit_order'), data=json.dumps(data), content_type='application/json')
#         self.assertEqual(response.status_code, 403)
#         self.assertEqual(response.json()['error'], 'This task has already been submitted.')
#         # Check if the task object remains unchanged
#         self.task.refresh_from_db()
#         self.assertTrue(self.task.is_submitted)
#         self.assertEqual(self.task.submitted_by, self.user)

#     def test_submit_order_unauthorized(self):
#         # Test when the user is not authorized to submit the order
#         unauthorized_user = User.objects.create_user(username='unauthorized', password='testpassword')
#         self.client.force_login(unauthorized_user)
#         data = {'request_id': self.task.req_id}
#         response = self.client.post(reverse('submit_order'), data=json.dumps(data), content_type='application/json')
#         self.assertEqual(response.status_code, 403)
#         self.assertEqual(response.json()['error'], 'You are not authorized to submit this order.')
#         # Check if the task object remains unchanged
#         self.task.refresh_from_db()
#         self.assertFalse(self.task.is_submitted)
#         self.assertIsNone(self.task.submitted_by)

#     def test_submit_order_invalid_request(self):
#         # Test when the request data is invalid
#         self.client.force_login(self.user)
#         response = self.client.post(reverse('submit_order'), data={}, content_type='application/json')
#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(response.json()['error'], 'Request does not exist')

class SubmitOrderViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', email='test@example.com', password='test_password')
        self.group = Group.objects.create(name='test_group')
        self.user.groups.add(self.group)
        self.task = require_info.objects.create(req_id='123', lab='test_lab')

    # def test_submit_order_success(self):
    #     self.client.login(username='test_user', password='test_password')
    #     data = {'request_id': '123'}
    #     response = self.client.post('/submit_order/', json.dumps(data), content_type='application/json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(json.loads(response.content)['is_submitted'])
    #     self.task.refresh_from_db()
    #     self.assertTrue(self.task.is_submitted)
    #     self.assertEqual(self.task.submitted_by, self.user)

    def test_submit_order_unauthorized(self):
        self.client.login(username='test_user', password='test_password')
        self.user.groups.remove(self.group)  # removing user from the required group
        data = {'request_id': '123'}
        response = self.client.post('/submit_order/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content), {'error': 'You are not authorized to submit this order.'})
        self.task.refresh_from_db()
        self.assertFalse(self.task.is_submitted)
        self.assertIsNone(self.task.submitted_by)

    # def test_submit_order_already_submitted(self):
    #     self.client.login(username='test_user', password='test_password')
    #     self.task.is_submitted = True
    #     self.task.save()
    #     data = {'request_id': '123'}
    #     response = self.client.post('/submit_order/', json.dumps(data), content_type='application/json')
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(json.loads(response.content), {'error': 'This task has already been submitted.'})

    # def test_submit_order_request_not_exist(self):
    #     self.client.login(username='test_user', password='test_password')
    #     data = {'request_id': '456'}  # request_id that does not exist
    #     response = self.client.post('/submit_order/', json.dumps(data), content_type='application/json')
    #     self.assertEqual(response.status_code, 404)
    #     self.assertEqual(json.loads(response.content), {'error': 'Request does not exist'})

    def test_submit_order_error(self):
        # mocking an exception to simulate an error during submission
        with self.assertRaises(Exception):
            self.client.login(username='test_user', password='test_password')
            data = {'request_id': '123'}
            with patch('your_app.views.send_notification') as mocked_send_notification:
                mocked_send_notification.side_effect = Exception('Error sending notification')
                response = self.client.post('/submit_order/', json.dumps(data), content_type='application/json')