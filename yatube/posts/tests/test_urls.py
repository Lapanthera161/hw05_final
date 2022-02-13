from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus
from posts.models import Group, Post

User = get_user_model()

INDEX = reverse('posts:index')
GR_TEST = reverse('posts:group_list', args=['test-slug'])
GR_FAKE = reverse('posts:group_list', args=['fake_slug'])
NEW = reverse('posts:post_create')
PROFILE = reverse('posts:profile', args=['post_author'])
P_DETAIL = reverse('posts:post_detail', args='1')
P_EDIT = reverse('posts:post_edit', args='1')


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',
        )

        cls.user = User.objects.create_user(
            username='post_author'
        )

        cls.user_2 = User.objects.create_user(
            username='another_user'
        )

        cls.post = Post.objects.create(
            text='Просто тестовый текст',
            author=StaticURLTests.user,
            group=StaticURLTests.group,
        )

    def setUp(self):
        self.guest_client = Client()

        self.post_author = Client()
        self.post_author.force_login(self.user)

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_2)

    def test_guest_client_urls_status_code(self):
        """Проверяем доступность страниц для любого пользователя."""
        field_response_urls_code = {
            INDEX: HTTPStatus.OK,
            GR_TEST: HTTPStatus.OK,
            GR_FAKE: HTTPStatus.NOT_FOUND,
            NEW: HTTPStatus.FOUND,
            PROFILE: HTTPStatus.OK,
            P_DETAIL: HTTPStatus.OK,
            P_EDIT: HTTPStatus.FOUND,
        }
        for url, response_code in field_response_urls_code.items():
            with self.subTest(url=url):
                status_code = self.guest_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_authorized_client_urls_status_code(self):
        """Проверяем доступность страниц для авторизованного пользователя"""
        field_response_urls_code = {
            INDEX: HTTPStatus.OK,
            GR_TEST: HTTPStatus.OK,
            GR_FAKE: HTTPStatus.NOT_FOUND,
            NEW: HTTPStatus.OK,
            PROFILE: HTTPStatus.OK,
            P_DETAIL: HTTPStatus.OK,
            P_EDIT: HTTPStatus.FOUND,
        }
        for url, response_code in field_response_urls_code.items():
            with self.subTest(url=url):
                status_code = self.authorized_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_author_post_edit_status_code(self):
        """Доступносить редактирования автору поста"""
        response = self.post_author.get(P_EDIT).status_code
        self.assertEqual(response, HTTPStatus.OK)

    def test_guest_client_redirect(self):
        """Проверяем редиректы для неавторизованного пользователя"""
        redirect_response = {
            NEW: '/auth/login/?next=/create/',
            P_EDIT: '/auth/login/?next=/posts/1/edit/',
        }
        for url, redirect in redirect_response.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, redirect)

    def test_authorized_client_redirect(self):
        """Проверяем редиректы не для автора"""
        response = self.authorized_client.get(P_EDIT)
        self.assertRedirects(response, P_DETAIL)

    def test_urls_uses_correct_template(self):
        """Проверка вызываемых HTML-шаблонов"""
        templates_url_names = {
            'posts/index.html': INDEX,
            'posts/group_list.html': GR_TEST,
            'posts/post_create.html': NEW,
            'posts/profile.html': PROFILE,
            'posts/post_detail.html': P_DETAIL,
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.post_author.get(address)
                self.assertTemplateUsed(response, template)


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
