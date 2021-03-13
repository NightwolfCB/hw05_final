from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User


class YatubeCacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='BaretskiyStas')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        response_0 = self.authorized_client.get(reverse('posts:index'))
        post = Post.objects.create(author=self.user, text='text123')
        response_1 = self.authorized_client.get(reverse('posts:index'))
        Post.objects.filter(id=post.id).delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_0.content, response_3.content)
