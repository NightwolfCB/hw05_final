from django.test import TestCase

from posts.models import Group, Post, User


class YatubeModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create()
        cls.post = Post.objects.create(
            text='А' * 200,
            author=cls.user
        )
        cls.group = Group.objects.create(
            title='Б' * 200,
            slug='test_group',
            description='В' * 200
        )

    def test_post_verbose_name(self):
        """verbose_name в полях Post совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст публикации',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Сообщество',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        """help_text в полях Post совпадает с ожидаемым."""
        post = self.post
        field_help_texts = {
            'text': 'Напишите текст вашей публикации',
            'author': 'Ваше имя',
            'group': 'Выберите группу'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_post_content_is_text_field(self):
        """__str__  post - это строчка с содержимым post.text."""
        post = self.post
        expected_post_content = post.text[:15]
        self.assertEquals(expected_post_content, str(post))

    def test_group_verbose_name(self):
        """verbose_name в полях Group совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Слаг',
            'description': 'Описание'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_group_help_text(self):
        """help_text в полях Group совпадает с ожидаемым."""
        group = self.group
        field_help_texts = {
            'title': 'Название вашего сообщества',
            'slug': 'Укажите адрес для вашего сообщества. Используйте '
                     'только латиницу, цифры, дефисы и знаки '
                     'подчёркивания',
            'description': 'Краткое описание вашего сообщества'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_group_title_is_text_field(self):
        """__str__  group - это строчка с содержимым group.title."""
        group = self.group
        expected_group_content = group.title
        self.assertEquals(expected_group_content, str(group))
