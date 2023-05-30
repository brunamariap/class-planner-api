from django.contrib import admin
from .models import Class, ClassCanceled,Course, CourseDiscipline, Discipline, Schedule, Teach, TemporaryClass

admin.site.register(Class)
admin.site.register(ClassCanceled)
admin.site.register(Course)
admin.site.register(CourseDiscipline)
admin.site.register(Discipline)
admin.site.register(Schedule)
admin.site.register(Teach)
admin.site.register(TemporaryClass)