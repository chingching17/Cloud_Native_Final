from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from web_cn.models import require_info
from web_cn.views import complete_order, delete_order, increase_priority, decrease_priority, show_history, add, manage, add_order
import json

class TestCompleteOrderView(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='ComplexPassword123!')
        self.other_user = User.objects.create_user(username='otheruser', password='ComplexPassword123!')
        self.require_info = require_info.objects.create(
            req_id=1,
            lab='Lab1',
            current_priority=3,
            status='Pending',
            is_submitted=True,
            completed_by=None
        )

    def test_complete_order(self):
        self.client.login(username='testuser', password='ComplexPassword123!')
        data = json.dumps({'request_id': 1})
        request = self.factory.post(reverse('complete_order'), data, content_type='application/json')
        request.user = self.user
        response = complete_order(request)
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, 200)
        self.require_info.refresh_from_db()
        self.assertTrue(self.require_info.is_completed)

    def test_complete_order_already_completed(self):
        self.require_info.completed_by = self.other_user
        self.require_info.save()
        self.client.login(username='testuser', password='ComplexPassword123!')
        data = json.dumps({'request_id': 1})
        request = self.factory.post(reverse('complete_order'), data, content_type='application/json')
        request.user = self.user
        response = complete_order(request)
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, 403)

    def test_complete_order_not_submitted(self):
        self.require_info.is_submitted = False
        self.require_info.save()
        self.client.login(username='testuser', password='ComplexPassword123!')
        data = json.dumps({'request_id': 1})
        request = self.factory.post(reverse('complete_order'), data, content_type='application/json')
        request.user = self.user
        response = complete_order(request)
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, 403)

    def test_complete_order_by_submitting_user(self):
        self.require_info.submitted_by = self.user
        self.require_info.save()
        self.client.login(username='testuser', password='ComplexPassword123!')
        data = json.dumps({'request_id': 1})
        request = self.factory.post(reverse('complete_order'), data, content_type='application/json')
        request.user = self.user
        response = complete_order(request)
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, 403)

    def test_complete_order_error(self):
        self.client.login(username='testuser', password='ComplexPassword123!')
        data = json.dumps({'request_id': 999})
        request = self.factory.post(reverse('complete_order'), data, content_type='application/json')
        request.user = self.user
        response = complete_order(request)
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, 500)

class TestDeleteOrderView(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='ComplexPassword123!')
        self.require_info = require_info.objects.create(
            req_id=1,
            lab='Lab1',
            current_priority=3,
            status='Pending'
        )

    def test_delete_order(self):
        self.client.login(username='testuser', password='ComplexPassword123!')
        data = json.dumps({'request_id': 1})
        request = self.factory.post(reverse('delete_order'), data, content_type='application/json')
        request.user = self.user
        response = delete_order(request)
        print(f"Response content: {response.content}")
        self.assertFalse(require_info.objects.filter(req_id=1).exists())

    def test_delete_order_nonexistent(self):
        self.client.login(username='testuser', password='ComplexPassword123!')
        data = json.dumps({'request_id': 999})
        request = self.factory.post(reverse('delete_order'), data, content_type='application/json')
        request.user = self.user
        response = delete_order(request)
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, 404)

class TestPriorityAdjustmentView(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='ComplexPassword123!')
        self.require_info = require_info.objects.create(
            req_id=1,
            lab='Lab1',
            current_priority=3,
            status='Pending'
        )

    def test_increase_priority(self):
        self.client.login(username='testuser', password='ComplexPassword123!')
        data = json.dumps({'request_id': 1})
        request = self.factory.post(reverse('increase_priority'), data, content_type='application/json')
        request.user = self.user
        response = increase_priority(request)
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, 200)
        self.require_info.refresh_from_db()
        self.assertEqual(self.require_info.current_priority, '2')

    def test_decrease_priority(self):
        self.client.login(username='testuser', password='ComplexPassword123!')
        data = json.dumps({'request_id': 1})
        request = self.factory.post(reverse('decrease_priority'), data, content_type='application/json')
        request.user = self.user
        response = decrease_priority(request)
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, 200)
        self.require_info.refresh_from_db()
        self.assertEqual(self.require_info.current_priority, '4')

    def test_increase_priority_nonexistent(self):
        self.client.login(username='testuser', password='ComplexPassword123!')
        data = json.dumps({'request_id': 999})
        request = self.factory.post(reverse('increase_priority'), data, content_type='application/json')
        request.user = self.user
        response = increase_priority(request)
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, 200)

    def test_decrease_priority_nonexistent(self):
        self.client.login(username='testuser', password='ComplexPassword123!')
        data = json.dumps({'request_id': 999})
        request = self.factory.post(reverse('decrease_priority'), data, content_type='application/json')
        request.user = self.user
        response = decrease_priority(request)
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, 200)

class TestOrderViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='ComplexPassword123!')
        self.require_info = require_info.objects.create(
            req_id=1,
            lab='Lab1',
            current_priority=3,
            status='Pending'
        )

    def test_show_history(self):
        self.client.login(username='testuser', password='ComplexPassword123!')
        response = self.client.get(reverse('show_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'history.html')
        self.assertContains(response, 'Lab1')

    def test_add(self):
        self.client.login(username='testuser', password='ComplexPassword123!')
        response = self.client.get(reverse('add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add.html')

    def test_manage(self):
        self.client.login(username='testuser', password='ComplexPassword123!')
        response = self.client.get(reverse('manage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage.html')

    def test_add_order(self):
        self.client.login(username='testuser', password='ComplexPassword123!')
        response = self.client.get(reverse('add_order'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add.html')

    def test_add_order_post(self):
        self.client.login(username='testuser', password='ComplexPassword123!')
        response = self.client.post(reverse('add_order'), {
            'factory': 'Factory1',
            'priority': 'High',
            'laboratory': 'Lab2'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(require_info.objects.filter(lab='Lab2').exists())
