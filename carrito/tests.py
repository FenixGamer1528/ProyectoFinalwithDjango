from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Producto


User = get_user_model()


class WishlistTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass1234')
        self.producto = Producto.objects.create(nombre='Prueba', precio=10.0)

    def test_toggle_favorito_requires_login(self):
        url = reverse('toggle_favorito', args=[self.producto.id])
        resp = self.client.post(url)
        # Should redirect to login because view is login_required
        self.assertIn(resp.status_code, (302,))

    def test_toggle_favorito_adds_and_removes(self):
        self.client.login(username='tester', password='pass1234')
        url = reverse('toggle_favorito', args=[self.producto.id])

        # Add
        resp = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('ok'))
        self.assertTrue(data.get('added'))
        self.user.refresh_from_db()
        self.assertIn(self.producto, self.user.favoritos.all())

        # Remove
        resp = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('ok'))
        self.assertFalse(data.get('added'))
        self.user.refresh_from_db()
        self.assertNotIn(self.producto, self.user.favoritos.all())

    def test_mis_deseos_view_shows_products(self):
        # add favorite
        self.user.favoritos.add(self.producto)
        self.client.login(username='tester', password='pass1234')
        url = reverse('mis_deseos')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # template should contain product name
        self.assertContains(resp, 'Prueba')
from django.test import TestCase

# Create your tests here.
