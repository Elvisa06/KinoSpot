from django.contrib import admin
from .models import Gener, Movie

# Register your models here.
class MovieAdmin(admin.ModelAdmin):
    list_display = ['id','title','rating', 'released', 'gener', 'description']
    list_filter = ['gener','rating']
    search_fields = ['title','released']
admin.site.register(Gener)
admin.site.register(Movie, MovieAdmin)