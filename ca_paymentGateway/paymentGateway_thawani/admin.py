from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Course, CourseRegistration

admin.site.register(Course)
admin.site.register(CourseRegistration)