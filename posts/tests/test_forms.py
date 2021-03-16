import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User
from yatube import settings
from yatube.settings import MEDIA_ROOT

MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class YatubeFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='StasBaretskiy')
        cls.user_2 = User.objects.create(username='BaretskiyStas')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_group',
            description='Test description')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """Валидная форма создает запись в Post"""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Раз, два и три.',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                text='Раз, два и три.',
                image='posts/small.gif'
            ).exists()
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        """При редактировании поста, изменяется запись в базе данных"""
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id,
        }
        test_post = Post.objects.create(
            text='Тестовый текст записи',
            author=self.user,
        )
        posts_count = Post.objects.count()
        kwargs = {'username': self.user.username, 'post_id': test_post.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs=kwargs),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            group=self.group.id,
            text='Измененный текст').exists())
        self.assertRedirects(response, reverse('posts:post', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)
        
    def test_upload_wrong_format_file(self):
        """Проверка формата загружаемого файла изображения"""
        not_image = SimpleUploadedFile(
            name='text_file.txt',
            content=b'test',
            content_type='text/plain'
        )
        form_data = {
            'text': 'Раз, два, три, четыре, пять',
            'group': self.group.id,
            'image': not_image
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertFormError(response, 'form', 'image', errors=[
            'Загрузите правильное изображение. Файл, '
            'который вы загрузили, поврежден или не является изображением.'
        ])
