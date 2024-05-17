from django.test import TestCase
from web_cn.models import require_info

class RequireInfoModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        require_info.objects.create(
            factory='ABC',
            priority='High',
            lab='Testing Lab',
            current_priority='High',
            status='Pending'
        )

    def test_factory_max_length(self):
        require = require_info.objects.get(req_id=1)
        max_length = require._meta.get_field('factory').max_length
        self.assertEqual(max_length, 5)

    def test_priority_max_length(self):
        require = require_info.objects.get(req_id=1)
        max_length = require._meta.get_field('priority').max_length
        self.assertEqual(max_length, 15)

    def test_lab_max_length(self):
        require = require_info.objects.get(req_id=1)
        max_length = require._meta.get_field('lab').max_length
        self.assertEqual(max_length, 20)

    def test_current_priority_max_length(self):
        require = require_info.objects.get(req_id=1)
        max_length = require._meta.get_field('current_priority').max_length
        self.assertEqual(max_length, 15)

    def test_status_max_length(self):
        require = require_info.objects.get(req_id=1)
        max_length = require._meta.get_field('status').max_length
        self.assertEqual(max_length, 20)

    def test_attachment_upload_to(self):
        require = require_info.objects.get(req_id=1)
        upload_to = require._meta.get_field('attachment').upload_to
        self.assertEqual(upload_to, 'attachments/')
