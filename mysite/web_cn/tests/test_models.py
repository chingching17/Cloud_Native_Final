from django.test import TestCase
from web_cn.models import require_info

class RequireInfoModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.require = require_info.objects.create(
            req_id=1,
            lab='Lab1',
            current_priority=3,  # Assuming priority is stored as an integer
            status='Pending',
            attachment='attachments/test.txt'
        )
    
    def test_lab_max_length(self):
        max_length = self.require._meta.get_field('lab').max_length
        self.assertEqual(max_length, 20)
    
    def test_current_priority_value(self):
        self.assertEqual(self.require.current_priority, 3)
    
    def test_status_max_length(self):
        max_length = self.require._meta.get_field('status').max_length
        self.assertEqual(max_length, 20)
    
    def test_attachment_upload_to(self):
        upload_to = self.require._meta.get_field('attachment').upload_to
        self.assertEqual(upload_to, 'attachments/')
