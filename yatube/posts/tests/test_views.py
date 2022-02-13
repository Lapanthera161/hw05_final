from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from posts.views import COUNTP
from posts.models import Group, Post


User = get_user_model()
POST_TEST = 13
SECOND_P = 3
ANOTHER_SLUG = 'other-test-group'
ANOTHER_URL = reverse('posts:group_list', args=[ANOTHER_SLUG])


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',)

        cls.user = User.objects.create_user(
            username='post_author')

        cls.post = Post.objects.create(
            text='Просто тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.post_author = Client()
        self.post_author.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            'posts/profile.html':
                reverse(
                    'posts:profile', kwargs={'username': self.user.username}),
            'posts/post_detail.html':
                reverse('posts:post_detail', kwargs={'post_id': '1'}),
            'posts/post_create.html': reverse('posts:post_create'),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.post_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index список постов."""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_text, self.post.text)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list список постов, отфильтрованных по группе."""
        response = self.post_author.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile список постов, отфильтрованных по пользователю."""
        response = self.post_author.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail один пост отфильтрованный по id."""
        response = self.post_author.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        first_object = response.context['post']
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit, форма редактирования поста,
        отфильтрованного по id ."""
        response = self.post_author.get(reverse(
            'posts:post_edit', kwargs={'post_id': '1'}))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,            
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create, форма создания поста."""
        response = self.post_author.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,            
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_post_on_index(self):
        """Пост появляется на главной странице сайта."""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        group_title = first_object.group.title
        self.assertEqual(group_title, self.group.title)

    def test_post_on_group(self):
        """Пост появляется на странице выбранной группы."""
        response = self.post_author.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        group_title = first_object.group.title
        self.assertEqual(group_title, self.group.title)

    def test_new_post_do_not_view_other_group(self):
        """Новый post не отображается в другой группе."""
        Group.objects.create(
            title='Другой заголовок',
            slug=ANOTHER_SLUG,
            description='Другое тестовое описание',
        )
        response = self.post_author.get(ANOTHER_URL)
        self.assertNotIn(PostPagesTests.post, response.context['page_obj'])

    def test_post_on_profile(self):
        """Пост появляется в профайле пользователя."""
        response = self.post_author.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        first_object = response.context['page_obj'][0]
        group_title = first_object.group.title
        self.assertEqual(group_title, self.group.title)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='Author_2'
        )
        cls.group_1 = Group.objects.create(
            title='Название группы для теста_1',
            slug='test-slug_1',
            description='Описание группы для теста_1'
        )
        objs = (
            Post(
                author=cls.user,
                text='Тестовый текст',
                group=cls.group_1
            )
            for i in range(POST_TEST)
        )
        Post.objects.bulk_create(objs)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_paginator(self):
        """Шаблон index список постов."""
        response = self.authorized_client.get(reverse('posts:index'))
        response_2 = self.authorized_client.get(reverse(
            'posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), COUNTP)
        self.assertEqual(len(response_2.context['page_obj']), SECOND_P)

    def test_group_list_page_paginator(self):
        """Шаблон group_list список постов, отфильтрованных по группе."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_1.slug})
        )
        response_2 = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group_1.slug}
            ) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']), COUNTP)
        self.assertEqual(
            len(response_2.context['page_obj']), SECOND_P)

    def test_profile_page_paginator(self):
        """Шаблон profile список постов, отфильтрованных по пользователю."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        response_2 = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']), COUNTP)
        self.assertEqual(
            len(response_2.context['page_obj']), SECOND_P)

    def test_new_and_edit_post_page_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        urls = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', args=('1'))]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,            
            'image': forms.fields.ImageField,
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                for value, expected in form_fields.items():
                    form_field = response.context['form'].fields.get(value)
                    self.assertIsInstance(form_field, expected)
