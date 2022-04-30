
from django.shortcuts import render, get_object_or_404
from catalog.models import Book, BookInstance, Author, Genre
from django.views import generic
# when using generic classes(list and detail)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# when using functions
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from catalog.forms import RenewBookForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.urls import reverse
import datetime


def index(request):
    """View function for the catalog home page"""
    # generate counts of all of the main objects
    num_books = Book.objects.all().count()
    num_authors = Author.objects.all().count()

    # The all() is implied by default
    num_instances = BookInstance.objects.count()
    num_genres = Genre.objects.count()

    # fiction books
    war_books = Book.objects.filter(title__startswith='the').count()

    # number of available books(status = 'a')
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()

    # count page visits using sessions, client-specific
    # get num_visits, if it doesn't exist, set it to 0
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_authors': num_authors,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_genres': num_genres,
        'war_books': war_books,
        'title': "Home",
        'num_visits': num_visits,
    }

    # render the HTML template index.html with the data from the context variable
    return render(request, 'index.html', context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to currenct users"""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AllLoanedBooksListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """Class based view listing all books that have been borrowed, only logged in staff 
    are supposed to view this."""
    model = BookInstance
    template_name = 'catalog/all_borrowed_books.html'
    paginate_by = 15
    permission_required = ('catalog.can_mark_returned')

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

# decorators are processed in order


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian"""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # if post request, then process the data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request a.k.a binding
        form = RenewBookForm(request.POST)

        # check if the form is valid
        if form.is_valid():
            # process the data in form.cleaned_data as equired.
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new url
            return HttpResponseRedirect(reverse('all_borrowed'))

    # if this is the first time the view is called, create the default form
    else:
        proposed_renew_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renew_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book-renew-librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    permission_required = ('catalog.add_author')
    # fields to display
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2007'}


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    permission_required = ('catalog.change_author')
    # all fields, not recommended method.(potential security issue of more fileds added)
    fields = '__all__'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    permission_required = ('catalog.delete_author')  # built-in django perm
    # you have to provide sucess url for delete
    # reverse_lazy() used here because we're providing a URL to a class-based view attribute.
    success_url = reverse_lazy('authors')


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'isbn', 'summary', 'genre', 'language']
    permission_required = 'catalog.add_book'  # built-in django perm


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'isbn', 'summary', 'genre', 'language']
    permission_required = ('catalog.change_book')


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    permission_required = 'catalog.delete_book'
    success_url = reverse_lazy('books')
