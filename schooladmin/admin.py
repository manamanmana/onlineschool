from django.contrib import admin
from .models import User, Genre, MaterRate, LessonRecord

# Register your models here.

admin.site.register(User)
admin.site.register(Genre)
admin.site.register(MaterRate)
admin.site.register(LessonRecord)
