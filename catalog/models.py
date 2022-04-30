from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
import uuid  # required for unique book instances


class Genre(models.Model):
    """Model representing a book genre"""
    name = models.CharField(
        max_length=200, help_text="Enter a book genre(e.g. Science Fiction)")

    def __str__(self):
        """String for representing the book object"""
        return self.name


class Language(models.Model):
    """Model representing a language(e.g English, French, Swahili)"""
    name = models.CharField(
        max_length=200, help_text="Enter the book's natural language. (e.g. English")

    def __str__(self):
        """string for representing the model object(in Admin site, etc)"""
        return self.name


class Book(models.Model):
    """Model representing a book (but not a specific copy of book)"""
    title = models.CharField(max_length=200)
    # foreign key used because a book can have only one author,
    # but authors can have multiple books
    # Author as a string rather than an object, because it hasn't been declared yet

    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(
        max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13, unique=True,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    # ManyToManyField used because genre can cantain many books, and a book can cover many genres
    # Genre class has already been defined so we can specify the object above
    genre = models.ManyToManyField(
        Genre, help_text="Select a genre for this book")
    language = models.ForeignKey(
        'Language', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        """String for representing the model object"""
        return self.title

    def display_genre(self):
        """Create a list for the display. This is required to display genre in admin"""
        return ', '.join(genre.name for genre in self.genre.all()[:3])
    display_genre.short_description = 'Genre'

    def get_absolute_url(self):
        """Returns a url to access a detail record for this book"""
        return reverse("book_detail", args=[str(self.id)])


class BookInstance(models.Model):
    """Model representing a specific copy of a book
    (e.g. that can be borrowed from the library)"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique id for this particular book across whole library")

    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On Loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS,
                              default='m', blank=True, help_text="Book availability")

    def is_overdue(self):
        # We first verify whether due_back is empty before making a comparison
        # (first test(if self.due_back) returns either True or False)
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    class Meta:
        ordering = ['due_back']
        # permissions are defined in meta class
        permissions = (('can_mark_returned', 'Set book as returned'),
                       ('can_renew', 'Can renew borrowed books'))

    def __str__(self):
        """string for representing the model object"""
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    """"Model representing an author"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class meta:
        ordering = ['last_name', 'first_name']
        permissions = [('can_cook_food', 'Can cook food')]

    def get_absolute_url(self):
        """Returns the urls to access a particular author instance"""
        return reverse("author_detail", args=[str(self.id)])

    def __str__(self):
        """String for representing a Model object"""
        return f"{self.last_name}, {self.first_name}"
