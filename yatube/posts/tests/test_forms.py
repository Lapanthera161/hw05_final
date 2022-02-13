import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

TEMP_DIR = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')

USERNAME = 'post_author'
INDEX_URL = reverse('posts:index')


@override_settings(MEDIA_ROOT=TEMP_DIR)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=cls.user,
        )
        cls.edit_post_url = reverse(
            'posts:post_edit', args=('1'))
        cls.post_url = reverse(
            'posts:post_detail', args=('1'))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_DIR, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает пост в Post."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif')
        form_data = {
            'group': PostCreateFormTests.group.pk,
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/profile/post_author/')
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author='1',
                text='Тестовый текст',
                group='1',                
                image='posts/small.gif',
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует пост в Post."""
        posts_count = Post.objects.count()
        other_group = Group.objects.create(
            title='Заголовок группы',
            slug='test-slug_other',
            description='Другое тестовое описание',
        )
        uploaded = SimpleUploadedFile(
            name='other_small.gif',
            content=SMALL_GIF,
            content_type='image/gif')
        form_data = {
            'group': other_group.pk,
            'text': 'Редактируемый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            PostCreateFormTests.edit_post_url,
            data=form_data,
            follow=True
        )
        edit_post = response.context['post']
        self.assertRedirects(response, PostCreateFormTests.post_url)
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.group, other_group)
        self.assertEqual(edit_post.author, PostCreateFormTests.user)
        self.assertEqual(Post.objects.count(), posts_count)
