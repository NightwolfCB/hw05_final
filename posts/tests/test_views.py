import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User
from yatube.settings import BASE_DIR, MEDIA_ROOT

MEDIA_ROOT = tempfile.mkdtemp(dir=BASE_DIR)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class YatubeViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Ремонт от Стаса',
            slug='remont_ot_stasa',
            description='Pемонт своими руками'
        )
        cls.user = User.objects.create_user(username='StasBaretskiy')
        cls.user_2 = User.objects.create(username='BaretskiyStas')
        cls.user_3 = User.objects.create(username='Chansonnier')
        cls.user_4 = User.objects.create(username='TurboShanson')
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Старые навыки не пропадают, понимаешь.',
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.authorized_client_3 = Client()
        self.authorized_client_3.force_login(self.user_3)
        self.authorized_client_4 = Client()
        self.authorized_client_4.force_login(self.user_3)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_pages_names = {
            'index.html': reverse('posts:index'),
            'new.html': reverse('posts:new_post'),
            'group.html': (
                reverse('posts:group', kwargs={'slug': self.group.slug})
            ),
            'posts/post.html':
                reverse('posts:post', kwargs={'username': self.user.username,
                                              'post_id': self.post.id}),
            'posts/profile.html':
                reverse('posts:profile',
                        kwargs={'username': self.user.username}),
            'posts/post_edit.html':
                reverse('posts:post_edit',
                        kwargs={'username': self.user.username,
                                'post_id': self.post.id})
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:index'))
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        post_image_0 = response.context.get('page')[0].image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0.username, self.user.username)
        self.assertEqual(post_image_0, self.post.image)

    def test_group_pages_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context.get('group').title, self.group.title)
        self.assertEqual(response.context.get('group').description,
                         self.group.description)
        self.assertEqual(response.context.get('group').slug, self.group.slug)
        self.assertEqual(response.context.get('page')[0].image,
                         self.post.image)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_shows_in_index_page(self):
        """Созданный пост с указанной группой появляется на главной
        странице сайта"""
        response = self.authorized_client.get(reverse('posts:index'))
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0.username, self.user.username)

    def test_post_shows_in_correct_group(self):
        """Созданный пост находится на странице выбранной группы"""
        group_wrong = Group.objects.create(
            title='Лестница стремянка',
            slug='test_group_wrong',
            description='Падение шансонье'
        )
        response_wrong = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': group_wrong.slug})
        )
        self.assertNotIn(self.post, response_wrong.context['posts'])

    def test_post_edit_page_show_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом"""
        response = self.authorized_client.get(f'/{self.user.username}/'
                                              f'{self.post.id}/edit/')
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        """Шаблон профиля пользователя сформирован с правильным контекстом"""
        response = self.authorized_client.get(f'/{self.user.username}/')
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        post_image_0 = response.context.get('page')[0].image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0.username, self.user.username)
        self.assertEqual(post_image_0, self.post.image)

    def test_post_page_show_correct_context(self):
        """Шаблон поста сформирован с правильным контекстом"""
        response = self.authorized_client.get(f'/{self.user.username}/'
                                              f'{self.post.id}/')
        post_text = response.context.get('post').text
        post_author = response.context.get('post').author
        post_image_0 = response.context.get('post').image
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author.username, self.user.username)
        self.assertEqual(post_image_0, self.post.image)

    def test_comment_create(self):
        """Авторизированный пользователь может комментировать посты"""
        comments = {
            'post': self.post,
            'author': self.user,
            'text': 'Три Два Раз'
        }
        self.authorized_client.post(reverse('posts:add_comment',
                                    kwargs={'username': self.user.username,
                                            'post_id': self.post.id}),
                                    data=comments)
        response = self.authorized_client.get(
            reverse('posts:post', kwargs={'username': self.user.username,
                                          'post_id': self.post.id}))
        self.assertEqual(response.context.get('comments')[0].text,
                         'Три Два Раз')

    def test_anonymous_unable_to_comment(self):
        """Неавторизированный пользователь не может комментировать посты"""
        comment = {'post': self.post,
                   'author': self.user,
                   'text': 'Раз Два Три'}
        response = self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}), data=comment)
        self.assertEqual(response.status_code, 302)

    def test_follow_index_page_show_correct_context(self):
        """Шаблон ленты новостей сформирован с правильным контекстом"""
        Follow.objects.create(
            user=self.user,
            author=self.user_2
        )
        Follow.objects.create(
            user=self.user_3,
            author=self.user_4
        )
        post_new_1 = Post.objects.create(
            author=self.user_2,
            text='Романтик коллекшн',
            group=self.group
        )
        post_new_2 = Post.objects.create(
            author=self.user_4,
            text='Романс за пацана',
            group=self.group
        )
        response_1 = self.authorized_client.get(reverse('posts:follow_index'))
        response_2 = self.authorized_client_3.get(
            reverse('posts:follow_index'))
        post_new_text_1 = response_1.context.get('page')[0].text
        post_new_text_2 = response_2.context.get('page')[0].text
        self.assertEqual(post_new_text_1, post_new_1.text)
        self.assertEqual(post_new_text_2, post_new_2.text)
        self.assertNotEqual(post_new_text_1, post_new_2.text)
        self.assertNotEqual(post_new_text_2, post_new_1.text)
        self.assertNotEqual(post_new_text_1, post_new_text_2)
