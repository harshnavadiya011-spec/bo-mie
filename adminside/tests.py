from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Admin, Role


class AdminSideListSerializerTests(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(
            role="Admin",
            permission=["manage_roles", "manage_staff"],
            is_admin=True,
        )
        
    def test_role_list_excludes_timestamps(self):
        url = reverse("roles-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

        role_item = response.data[0]
        self.assertNotIn("created_at", role_item)
        self.assertNotIn("updated_at", role_item)
        self.assertNotIn("deleted_at", role_item)

    def test_role_detail_includes_timestamps(self):
        url = reverse("roles-detail", kwargs={"pk": self.role.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)
        self.assertIn("deleted_at", response.data)

    def test_admin_list_excludes_timestamps(self):
        url = reverse("admins-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

        admin_item = response.data[0]
        self.assertNotIn("created_at", admin_item)
        self.assertNotIn("updated_at", admin_item)
        self.assertNotIn("deleted_at", admin_item)

    def test_admin_detail_includes_timestamps(self):
        url = reverse("admins-detail", kwargs={"pk": self.admin.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)
        self.assertIn("deleted_at", response.data)