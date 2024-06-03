from django.test import TestCase, override_settings
from django.core.mail import send_mail
from unittest.mock import patch
from web_cn.tasks import send_notification
from celery import current_app
import logging
import io

class SendNotificationTaskTest(TestCase):

    def setUp(self):
        # Configure Celery to run tasks synchronously for testing
        self.celery_always_eager = current_app.conf.task_always_eager
        current_app.conf.task_always_eager = True

        # Set up logger to capture log messages
        self.log_stream = io.StringIO()
        self.log_handler = logging.StreamHandler(self.log_stream)
        self.logger = logging.getLogger('myapp')
        self.logger.addHandler(self.log_handler)

    def tearDown(self):
        # Restore Celery configuration
        current_app.conf.task_always_eager = self.celery_always_eager

        # Remove the log handler
        self.logger.removeHandler(self.log_handler)

    @override_settings(EMAIL_HOST_USER='your-email@example.com')
    @patch('web_cn.tasks.send_mail')
    def test_send_notification_success(self, mock_send_mail):
        # Arrange
        mock_send_mail.return_value = 1  # Simulate successful email send
        email = 'test@example.com'
        subject = 'Test Subject'
        message = 'Test Message'

        # Act
        send_notification(email, subject, message)

        # Assert
        mock_send_mail.assert_called_once_with(
            subject,
            message,
            'your-email@example.com',  # This should match the override setting
            [email],
            fail_silently=False,
        )
        self.log_handler.flush()
        log_output = self.log_stream.getvalue()
        self.assertIn(f"Email sent successfully to {email}", log_output)

    @override_settings(EMAIL_HOST_USER='your-email@example.com')
    @patch('web_cn.tasks.send_mail')
    def test_send_notification_failure(self, mock_send_mail):
        # Arrange
        mock_send_mail.side_effect = Exception('SMTP Error')  # Simulate email send failure
        email = 'test@example.com'
        subject = 'Test Subject'
        message = 'Test Message'

        # Act
        send_notification(email, subject, message)

        # Assert
        mock_send_mail.assert_called_once_with(
            subject,
            message,
            'your-email@example.com',  # This should match the override setting
            [email],
            fail_silently=False,
        )
        self.log_handler.flush()
        log_output = self.log_stream.getvalue()
        self.assertIn(f"Error sending email to {email}: SMTP Error", log_output)
