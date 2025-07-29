from django.contrib import admin
from .models import CustomUser, Article, Comment, Category
admin.register(CustomUser)
admin.site.register(Article)
admin.site.register(Category)
admin.site.register(Comment)

# Register your models here.
