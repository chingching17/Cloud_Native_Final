from django.test import SimpleTestCase
from django.urls import reverse, resolve
from web_cn.views import index, show_history, add, manage, add_order, delete_order, complete_order

# test urls match views
class TestUrls(SimpleTestCase):

    def test_index_url_is_resolved(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func, index)

    def test_show_history_url_is_resolved(self):
        url = reverse('show_history')
        self.assertEquals(resolve(url).func, show_history)

    def test_add_url_is_resolved(self):
        url = reverse('add')
        self.assertEquals(resolve(url).func, add)

    def test_manage_url_is_resolved(self):
        url = reverse('manage')
        self.assertEquals(resolve(url).func, manage)

    def test_add_order_url_is_resolved(self):
        url = reverse('add_order')
        self.assertEquals(resolve(url).func, add_order)

    def test_delete_order_url_is_resolved(self):
        url = reverse('delete_order')
        self.assertEquals(resolve(url).func, delete_order)
    
    def test_complete_order_url_is_resolved(self):
        url = reverse('complete_order') 
        self.assertEquals(resolve(url).func, complete_order)