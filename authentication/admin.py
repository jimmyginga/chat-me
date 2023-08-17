from django.contrib import admin
from .models import User

# class Admin(admin.ModelAdmin):
#     fieldsets = [
#         ('General',
#          {
#              'fields': ['username', 'password'],
#          }),
#         ('Personal info',
#          {
#              'fields': ['first_name', 'last_name', 'email'],
#          }),
#         ('Permissions',
#          {
#              'fields': ['is_active', 'is_staff', 'is_superuser'],
#          }),
#         ('Important dates',
#          {
#              'fields': ['last_login', 'date_joined'],
#          }),
#     ]

admin.site.register(User)
