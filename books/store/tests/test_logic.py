from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User

from store.logic import set_rating
# import django
# import os

from store.models import Book, UserBookRelation


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "books.settings")
# django.setup()

class LogicTestCase(TestCase):

    def setUp(self):
        user1 = User.objects.create(username='test_username1',
                                    first_name="Ivan", last_name="Petrov")
        user2 = User.objects.create(username='test_username2')
        self.user3 = User.objects.create(username='test_username3')
        self.book_1 = Book.objects.create(name='Test book 1', price=25,
                                          author_name='Author 1', discount=20, owner=user1)

        UserBookRelation.objects.create(user=user1, book=self.book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=self.book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user3, book=self.book_1, like=True, rate=4)

    def test_ok(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual('4.67', str(self.book_1.rating))

    @patch("store.logic.set_rating", autospec=True)
    def test_no_set_rating(self, mock_set_rating):
        user_book = UserBookRelation.objects.get(user=self.user3, book=self.book_1)
        user_book.like = False
        user_book.save()

        mock_set_rating.assert_not_called()

    # def test_plus(self):
    #     result = operations(6, 13, '+')
    #     self.assertEqual(19, result)
    #
    # def test_minus(self):
    #     result = operations(6, 13, '-')
    #     self.assertEqual(-7, result)
    #
    # def test_multiply(self):
    #     result = operations(6, 13, '*')
    #     self.assertEqual(78, result)
