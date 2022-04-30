import datetime
from email.utils import localtime
from urllib import response
from django.utils import timezone
from django.test import TestCase
from catalog.models import Author
from django.urls import reverse
from django.contrib.auth.models import User  # for borrower testing
from catalog.models import Book, BookInstance, Genre, Language


class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # create 8 authors for pagination test
        number_of_authors = 8

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f"Joe {author_id}",
                last_name=f"Biden {author_id}"
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_the_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_five(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 5)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 3)


class LoanedBookInstancesByUserListViewTest(TestCase):
    # We've used SetUp() rather than setUpTestData() because we'll be modifying some of these objects later.

    def setUp(self):
        # create two users
        user1 = User.objects.create_user(username="user1", password="batuki1")
        user2 = User.objects.create_user(username="user2", password="batuki2")
        user1.save()
        user2.save()

        # create a book
        test_author = Author.objects.create(first_name="John", last_name="Doe")
        test_language = Language.objects.create(name="English")
        test_genre = Genre.objects.create(name="Fantansy")
        test_book = Book.objects.create(
            title="My Book T",
            author=test_author,
            summary="My book beautiful summary",
            isbn="EJIEMFRUM48",
            language=test_language,
        )
        # create book genre as a post-step
        # Direct assignment of many-to-many types not allowed.
        book_genre_objects = Genre.objects.all()
        test_book.genre.set(book_genre_objects)

        test_book.save()

        # create 30 BookInstance copies
        test_book_copies = 30
        for book_copy in range(test_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy % 5)
            the_borrower = user1 if book_copy % 2 else user2
            status = 'm'

            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(
            response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username="user1", password="batuki1")
        response = self.client.get(reverse('my-borrowed'))

        # test user is logged in
        self.assertEqual(str(response.context['user']), 'user1')

        # check that we go a response "success"
        self.assertEqual(response.status_code, 200)
        # check that we used the correct template
        self.assertTemplateUsed(
            response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username="user1", password="batuki1")
        response = self.client.get(reverse('my-borrowed'))

        # check user is logged in
        self.assertEqual(str(response.context['user']), 'user1')
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # now change all books to be on loan
        books = BookInstance.objects.all()[0:10]
        for book in books:
            book.status = 'o'
            book.save()

        # check again that now we have borrowed books in the list
        response = self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']), 'user1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('bookinstance_list' in response.context)

        # confirm all books belong to user1 and are on loan
        for book_item in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], book_item.borrower)
            self.assertEqual(book_item.status, 'o')

    def test_pages_ordered_by_due_date(self):
        # change all books to be on loan
        books = BookInstance.objects.all()
        for book in books:
            book.status = 'o'
            book.save()

        # login
        login = self.client.login(username="user1", password="batuki1")

        # check login sucess
        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(response.context['user']), 'user1')
        self.assertEqual(response.status_code, 200)

        # test pagination
        self.assertEqual(len(response.context['bookinstance_list']), 10)

        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back
