from django.contrib import admin

from applications.tickets.models import Category, Ticket

admin.site.register(Category)
admin.site.register(Ticket)