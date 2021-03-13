from django.test import Client, TestCase

from posts.models import Group, Post, User


class YatubeURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_group',
            description='Test description'
        )
        cls.user = User.objects.create_user(username='StasBaretskiy')
        cls.post = Post.objects.create(author=cls.user, text='Тестовый текст')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Главная страница доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_added_url_exists_at_desired_location(self):
        """Страница группы /group/test_group/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test_group/')
        self.assertEqual(response.status_code, 200)

    def test_post_list_url_exists_at_desired_location(self):
        """Страница создания нового поста /new/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_post_list_url_redirect_anonymous(self):
        """Страница по адресу /new/ перенаправляет неавторизированного
        пользователя."""
        response = self.guest_client.get('/new/')
        self.assertEqual(response.status_code, 302)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': '/',
            'group.html': f'/group/{self.group.slug}/',
            'new.html': '/new/',
            'posts/post.html': f'/{self.user.username}/{self.post.id}/',
            'posts/profile.html': f'/{self.user.username}/',
            'posts/post_edit.html': f'/{self.user.username}/{self.post.id}/edit/'
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_url_redirect_anonymous_on_login_page(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина."""
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_username_url_exists_at_desired_location(self):
        """Страница /username/ доступна любому пользователю."""
        response = self.guest_client.get(f'/{self.user.username}/')
        self.assertEqual(response.status_code, 200)

    def test_username_post_id_url_exists_at_desired_location(self):
        """Страница /username/post_id/ доступна любому пользователю."""
        response = self.guest_client.get(f'/{self.user.username}/'
                                         f'{self.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_username_post_id_edit_guest_url_exists_at_desired_location(self):
        """Страница /username/post_id/edit/ перенаправит
        неавторизированного пользователя на страницу входа"""
        response = self.guest_client.get(f'/{self.user.username}/'
                                         f'{self.post.id}/edit/')
        self.assertRedirects(response, '/auth/login/?next=/'
                             f'{self.user.username}/{self.post.id}/edit/')

    def test_username_post_id_edit_author_url_exists_at_desired_location(
            self):
        """Страница /username/post_id/edit/ доступна только автору поста."""
        response = self.authorized_client.get(f'/{self.user.username}/'
                                              f'{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_username_post_id_edit_not_author_url_exists_at_desired_location(self):
        """Страница /username/post_id/edit/ доступна только автору поста.
        Авторизированного пользователя, но не автора поста, перенаправит на
        страницу просмотра этой записи"""
        user_not_author = User.objects.create_user(username='not_author')
        authorized_client_2 = Client()
        authorized_client_2.force_login(user_not_author)
        response = authorized_client_2.get(f'/{self.user.username}/'
                                           f'{self.post.id}/edit/')
        self.assertRedirects(response, f'/{self.user.username}/'
                             f'{self.post.id}/')

    def test_wrong_url_returns_404(self):
        """Страница /lol_kek_cheburek/ возвращает ошибку 404"""
        response = self.guest_client.get('/lol_kek_cheburek/')
        self.assertEqual(response.status_code, 404)
