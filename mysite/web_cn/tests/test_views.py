from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from web_cn.models import require_info
from django.db import connection
import json
from django.http import JsonResponse
from unittest.mock import patch
from web_cn.views import add_order
from django.template.loader import render_to_string

class TestViews(TestCase):
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
    
    def test_add_order(self):
        client = Client()
        url = reverse('add_order')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add.html')
    
class AddOrderViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_add_order_post(self):
        # Create a POST request with necessary data
        data = {
            'factory': 'ABC',
            'priority': 'High',
            'laboratory': 'Testing Lab',
            # Simulate an attachment file
            'attachment': 'test_file.txt'
        }
        request = self.factory.post(reverse('add_order'), data)
        
        # Attach FILES if any
        request.FILES['attachment'] = 'test_file.txt'

        # Call the view function
        response = add_order(request)

        # Check if a new order was created
        self.assertEqual(require_info.objects.count(), 1)

        # Check if the response redirects to '/add'
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/add')

        

class TestDeleteOrderView(TestCase):
    # 測試成功刪除訂單的情況
    @patch('web_cn.views.require_info.objects.get')
    def test_delete_order(self, mock_get):
        # Create a test client
        client = Client()

        # Define a fake request_id
        request_id = 123

        # Prepare mock object
        mock_instance = mock_get.return_value
        mock_instance.delete.return_value = None

        # Prepare request data
        data = {'request_id': request_id}
        json_data = json.dumps(data)

        # Perform a POST request to the view
        response = client.post(reverse('delete_order'), data=json_data, content_type='application/json')

        # Check if the delete method was called
        mock_get.assert_called_once_with(req_id=request_id)
        mock_instance.delete.assert_called_once()

        # Check if the view redirects to '/manage'
        self.assertRedirects(response, '/manage')

    # 測試試圖刪除不存在的訂單的情況 
    def test_delete_order_non_existing_request(self):
        # Create a test client
        client = Client()

        # Define a fake request_id that does not exist
        request_id = 999

        # Prepare request data
        data = {'request_id': request_id}
        json_data = json.dumps(data)

        # Perform a POST request to the view
        response = client.post(reverse('delete_order'), data=json_data, content_type='application/json')

        # Check if the response status code is 404
        self.assertEqual(response.status_code, 404)

        # Check if the response contains the expected error message
        self.assertEqual(response.json(), {'error': 'Request does not exist'})

    # 測試刪除訂單時出現錯誤的情況
    @patch('web_cn.views.require_info.objects.get')
    def test_delete_order_error(self, mock_get):
        # Create a test client
        client = Client()

        # Define a fake request_id
        request_id = 123

        # Prepare mock object to raise an exception
        mock_instance = mock_get.return_value
        mock_instance.delete.side_effect = Exception('Test error')

        # Prepare request data
        data = {'request_id': request_id}
        json_data = json.dumps(data)

        # Perform a POST request to the view
        response = client.post(reverse('delete_order'), data=json_data, content_type='application/json')

        # Check if the delete method was called
        mock_get.assert_called_once_with(req_id=request_id)
        mock_instance.delete.assert_called_once()

        # Check if the response status code is 500
        self.assertEqual(response.status_code, 500)

        # Check if the response contains the expected error message
        self.assertEqual(response.json(), {'error': 'Error deleting request: Test error'})

class TestCompleteOrderView(TestCase):
    @patch('web_cn.views.require_info.objects.get')
    def test_complete_order(self, mock_get):
        # Create a test client
        client = Client()

        # Define a fake request_id
        request_id = 123

        # Prepare mock object
        mock_instance = mock_get.return_value
        mock_instance.save.return_value = None

        # Prepare request data
        data = {'request_id': request_id}
        json_data = json.dumps(data)

        # Perform a POST request to the view
        response = client.post(reverse('complete_order'), data=json_data, content_type='application/json')

        # Check if the get method was called
        mock_get.assert_called_once_with(req_id=request_id)

        # Check if the status attribute was updated to '完成'
        self.assertEqual(mock_instance.status, '完成')

        # Check if the save method was called
        mock_instance.save.assert_called_once()

        # Check if the view redirects to '/manage'
        self.assertRedirects(response, '/manage')

    def test_complete_order_non_existing_request(self):
        # Create a test client
        client = Client()

        # Define a fake request_id that does not exist
        request_id = 999

        # Prepare request data
        data = {'request_id': request_id}
        json_data = json.dumps(data)

        # Perform a POST request to the view
        response = client.post(reverse('complete_order'), data=json_data, content_type='application/json')

        # Check if the response status code is 404
        self.assertEqual(response.status_code, 404)

        # Check if the response contains the expected error message
        self.assertEqual(response.json(), {'error': 'Request does not exist'})

    @patch('web_cn.views.require_info.objects.get')
    def test_complete_order_error(self, mock_get):
        # Create a test client
        client = Client()

        # Define a fake request_id
        request_id = 123

        # Prepare mock object to raise an exception
        mock_instance = mock_get.return_value
        mock_instance.save.side_effect = Exception('Test error')

        # Prepare request data
        data = {'request_id': request_id}
        json_data = json.dumps(data)

        # Perform a POST request to the view
        response = client.post(reverse('complete_order'), data=json_data, content_type='application/json')

        # Check if the get method was called
        mock_get.assert_called_once_with(req_id=request_id)

        # Check if the save method was called
        mock_instance.save.assert_called_once()

        # Check if the response status code is 500
        self.assertEqual(response.status_code, 500)

        # Check if the response contains the expected error message
        self.assertEqual(response.json(), {'error': 'Error deleting request: Test error'})
