from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg, Sum, F
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksSerializersTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='test_username1',
                                    first_name="Ivan", last_name="Petrov")
        user2 = User.objects.create(username='test_username2')
        user3 = User.objects.create(username='test_username3')
        book_1 = Book.objects.create(name='Test book 1', price=25,
                                     author_name='Author 1', discount=20, owner=user1)
        book_2 = Book.objects.create(name='Test book 2', price=55,
                                     author_name='Author 2')

        UserBookRelation.objects.create(user=user1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True, rate=5)
        user_book_3 = UserBookRelation.objects.create(user=user3, book=book_1, like=True, rate=3)
        user_book_3.rate = 4
        user_book_3.save()

        UserBookRelation.objects.create(user=user1, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True, rate=4)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        #data = BooksSerializer([book_1, book_2], many=True).data

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            #rating=Avg('userbookrelation__rate'),
            final_price=Case(
                When(discount=None, then='price'), default=F('price') - F('discount')
                ),
            owner_name=F('owner__username')
        ).order_by('id')

        data = BooksSerializer(books, many=True).data

        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Author 1',
                # 'likes_count': 3,
                'annotated_likes': 3,
                'rating': '4.67',
                'discount': '20.00',
                'final_price': '5.00',
                'owner_name': 'test_username1',
                'readers': [
                    {
                        'first_name': "Ivan",
                        'last_name': "Petrov"
                    },
                    {
                        'first_name': "",
                        'last_name': ""
                    },
                    {
                        'first_name': "",
                        'last_name': ""
                    },
                ]
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Author 2',
                # 'likes_count': 2,
                'annotated_likes': 2,
                'rating': '3.50',
                'discount': None,
                'final_price': '55.00',
                'owner_name': None,
                'readers': [
                    {
                        'first_name': "Ivan",
                        'last_name': "Petrov"
                    },
                    {
                        'first_name': "",
                        'last_name': ""
                    },
                    {
                        'first_name': "",
                        'last_name': ""
                    },
                ]
            }
        ]
        print(expected_data)
        print(data)
        self.assertEqual(expected_data, data)
