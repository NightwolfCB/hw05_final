from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from yatube import settings


class YatubePaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        number_of_posts = 228
        cls.user = User.objects.create(username='GladiatorPWNZ')
        cls.group = Group.objects.create(
            title='Da da ya',
            slug='da',
            description='yaaa'
        )
        for post_num in range(number_of_posts):
            Post.objects.create(
                text='da ya ' * post_num,
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_containse_ten_records(self):
        """На первой странице ровно 10 постов"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get('page').object_list), settings.PAGE_SIZE)

    def test_twenty_third_page_containse_eight_records(self):
        """На двадцать третьей странице ровно 8 постов"""
        response = self.client.get(reverse('posts:index') + '?page=23')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get('page').object_list), 8)
