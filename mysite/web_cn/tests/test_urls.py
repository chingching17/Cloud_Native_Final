from django.test import SimpleTestCase
from django.urls import reverse, resolve
from web_cn.views import index, show_history, add, manage, add_order, delete_order, complete_order

class TestUrls(SimpleTestCase):

    def test_index_url_is_resolved(self):
        url = reverse('index')
        self.assertEqual(resolve(url).func, index)

    def test_show_history_url_is_resolved(self):
        url = reverse('show_history')
        self.assertEqual(resolve(url).func, show_history)

    def test_add_url_is_resolved(self):
        url = reverse('add')
        self.assertEqual(resolve(url).func, add)

    def test_manage_url_is_resolved(self):
        url = reverse('manage')
        self.assertEqual(resolve(url).func, manage)

    def test_add_order_url_is_resolved(self):
        url = reverse('add_order')
        self.assertEqual(resolve(url).func, add_order)

    def test_delete_order_url_is_resolved(self):
        url = reverse('delete_order')
        self.assertEqual(resolve(url).func, delete_order)
    
    def test_complete_order_url_is_resolved(self):
        url = reverse('complete_order')
        self.assertEqual(resolve(url).func, complete_order)
