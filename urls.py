"""
URL configuration for KinoSpotWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from viewer import views
from viewer.views import hello, all_geners, all_movies, all_information, geners, Movies, top_rated_movies, find_movie, \
    movies_by_year,search_movie,MovieListView,MovieCreateView,MovieDetailView,MovieSearchView,MovieUpdateView,MovieDeleteView,ReservationCreateView,ReservationDetailView,movies_by_gener,movie_detail_by_title,download_ticket

urlpatterns = [
    path('admin/', admin.site.urls),
    path("movies/search/", MovieSearchView.as_view(), name="movie_search"),
    path('hello/<name>', hello),
    path ('geners/',all_geners),
    path('movies/', all_movies, name='all_movies'),
    path ('', all_information),
    path ('allgeners/',geners),
    path('allmovies/',Movies),
    path('topmovies/',top_rated_movies),
    path('movie/<title>/', find_movie),
    path("movies/year/<int:year>/",movies_by_year),
    path('movies/search/<str:term>/',search_movie),
    path("", MovieListView.as_view(), name="index"),
    path("movies/", MovieListView.as_view(), name="all_movies"),
    path("movies/create/", MovieCreateView.as_view(), name="movie_create"),
    path("movies/<str:title>/", MovieDetailView.as_view(), name="movie_detail"),
    path("movies/<int:pk>/edit/", MovieUpdateView.as_view(), name="movie_update"),
    path("movies/<int:pk>/delete/", MovieDeleteView.as_view(), name="movie_delete"),
    path('reserve/', ReservationCreateView.as_view(), name='reservation_create'),
    path('reservation/<int:pk>/', ReservationDetailView.as_view(), name='reservation_detail'),
    path('reservation/success/', TemplateView.as_view(template_name='viewer/reservation_success.html'), name='reservation_success'),
    path('movies-by-gener/', views.movies_by_gener, name='movies_by_gener'),
    path('movies/<str:movie_title>/', views.movie_detail_by_title, name='movie_detail_by_title'),
    path("download-ticket/", views.download_ticket, name="download_ticket"),
    path('reservation-confirm/', views.reservation_confirm, name='reservation_confirm'),

]

