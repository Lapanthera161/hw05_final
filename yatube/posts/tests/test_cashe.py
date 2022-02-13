from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User


INDEX = reverse('posts:index')


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='cache')
        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=cls.test_user,
        )

    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """Кэширование данных на главной странице работает корректно"""
        response = self.guest_client.get(INDEX)
        cached_response_content = response.content
        Post.objects.create(text='Второй пост', author=self.test_user)
        response = self.guest_client.get(INDEX)
        self.assertEqual(cached_response_content, response.content)
        cache.clear()
        response = self.guest_client.get(INDEX)
        self.assertNotEqual(cached_response_content, response.content)