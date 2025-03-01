from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.not_author = User.objects.create(username='Не автор')

    def test_pages_availability(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:home', None),
            ('notes:detail', (self.note.slug,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete', 'notes:detail'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_access_for_non_author(self):
        self.client.force_login(self.not_author)
        response = self.client.get(reverse('notes:edit', args=(self.note.slug,)))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        response = self.client.get(reverse(
            'notes:delete',
            args=(self.note.slug,))
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_access_for_author(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:edit', args=(self.note.slug,)))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.client.get(reverse(
            'notes:delete',
            args=(self.note.slug,))
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_user_redirects(self):
        login_url = reverse('users:login')
        for name in ('notes:add', 'notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(
                    name,
                    args=(self.note.slug,)
                ) if name in ('notes:edit', 'notes:delete') else reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
