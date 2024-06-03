from django.test import TestCase
from django.contrib.auth.models import User, Group
from web_cn.forms import CustomUserCreationForm

class CustomUserCreationFormTest(TestCase):

    def setUp(self):
        # Ensure groups exist for testing
        self.group_names = [
            '化學實驗室', '表面分析實驗室', '成分分析實驗室', 
            'Fab A', 'Fab B', 'Fab C'
        ]
        for name in self.group_names:
            Group.objects.get_or_create(name=name)

    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'password123ka',
            'password2': 'password123ka',
            'group': 'Fab A',
        }
        form = CustomUserCreationForm(data=form_data)
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('password123ka'))
        self.assertTrue(user.groups.filter(name='Fab A').exists())


    def test_invalid_form_due_to_missing_email(self):
        form_data = {
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'password123',
            'group': 'Fab A',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invalid_form_due_to_password_mismatch(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'differentpassword',
            'group': 'Fab A',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_invalid_group_choice(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password123',
            'group': 'Invalid Group',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('group', form.errors)

    def test_user_added_to_group(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'password123ka',
            'password2': 'password123ka',
            'group': 'Fab B',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.groups.filter(name='Fab B').exists())
