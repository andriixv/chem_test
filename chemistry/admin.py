from django.contrib import admin
from .models import Grade, Section, Category, Question

# Register your models here.
admin.site.register(Grade)
admin.site.register(Section)
admin.site.register(Category)
admin.site.register(Question)