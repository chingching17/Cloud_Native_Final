from django.test import TestCase
from django.contrib.auth.models import User
from web_cn.models import require_info
from datetime import datetime
from django.core.files.uploadedfile import SimpleUploadedFile

class RequireInfoModelTest(TestCase):

    def setUp(self):
        # Create two users for submitted_by and completed_by fields
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password123')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='password123')

    def test_create_require_info(self):
        # Create an instance of require_info
        require = require_info.objects.create(
            factory='Fab A',
            priority='High',
            lab='Chemistry',
            current_priority=10,
            status='In Progress',
            is_completed=False,
            is_submitted=True,
            submitted_by=self.user1,
            completed_by=None,
            created_at=datetime.now()
        )

        # Assert that the instance is saved correctly
        self.assertEqual(require.factory, 'Fab A')
        self.assertEqual(require.priority, 'High')
        self.assertEqual(require.lab, 'Chemistry')
        self.assertEqual(require.current_priority, 10)
        self.assertEqual(require.status, 'In Progress')
        self.assertFalse(require.is_completed)
        self.assertTrue(require.is_submitted)
        self.assertEqual(require.submitted_by, self.user1)
        self.assertIsNone(require.completed_by)

    def test_create_require_info_with_attachment(self):
        # Create an instance of require_info with an attachment
        attachment = SimpleUploadedFile("file.txt", b"file_content")
        require = require_info.objects.create(
            factory='Fab B',
            priority='Medium',
            lab='Surface Analysis',
            current_priority=20,
            status='Pending',
            attachment=attachment,
            is_completed=False,
            is_submitted=True,
            submitted_by=self.user2,
            completed_by=self.user1,
            created_at=datetime.now()
        )

        # Assert that the instance is saved correctly
        self.assertEqual(require.factory, 'Fab B')
        self.assertEqual(require.priority, 'Medium')
        self.assertEqual(require.lab, 'Surface Analysis')
        self.assertEqual(require.current_priority, 20)
        self.assertEqual(require.status, 'Pending')
        self.assertFalse(require.is_completed)
        self.assertTrue(require.is_submitted)
        self.assertEqual(require.submitted_by, self.user2)
        self.assertEqual(require.completed_by, self.user1)
        self.assertTrue(require.attachment)

    def test_default_values(self):
        # Create an instance with default values
        require = require_info.objects.create(
            factory='Fab C',
            priority='Low',
            lab='Composition Analysis',
            current_priority=30,
            status='Not Started',
            submitted_by=self.user1,
            created_at=datetime.now()
        )

        # Assert that default values are set correctly
        self.assertFalse(require.is_completed)
        self.assertFalse(require.is_submitted)
        # self.assertIsNone(require.attachment)  # Check that attachment is None
        if require.attachment.name: 
            print ("I have a sound file")
        else:   
            print ("no sound")
        self.assertIsNone(require.completed_by)
