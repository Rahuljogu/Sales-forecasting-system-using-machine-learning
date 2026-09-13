from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ModelTrainingViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='admin',
            password='secret123',
        )
        self.client.force_login(self.user)

    def test_model_training_requires_existing_uploaded_dataset(self):
        session = self.client.session
        session['dataset_path'] = '/tmp/non-existent.csv'
        session.save()

        response = self.client.post(reverse('model_training'), {'action': 'load'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertIn('Please upload a dataset first', response.context['error'])
