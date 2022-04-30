from django.contrib import admin
from .models import Author, Book, BookInstance, Language, Genre

# admin.site.register(BookInstance)
# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Language)


class BookInline(admin.TabularInline):
    model = Book
    extra = 0


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    # field names to be displayed in the list are declared in a tuple in the required order
    list_display = ('last_name', 'first_name',
                    'date_of_birth', 'date_of_death')
    # using fields - The fields attribute lists just those fields that are
    # to be displayed on the form, in order.
    # they are display vertically by default, use tuple to display horizontary
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]
# display related records inline(either stackedinline-default, or tabularinline)


class BookInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    fields = [('title', 'author'), ('summary', 'genre'), ('isbn', 'language')]
    inlines = [BookInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    # filter by status and due date using (list_filter)
    list_filter = ('status', 'due_back')

    # organizing detail views
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )
