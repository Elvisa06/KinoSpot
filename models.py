from django.db import models


# Create your models here.
class Gener(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

#movie
class Movie(models.Model):
    title = models.CharField(max_length=128)
    gener = models.ForeignKey(Gener, on_delete=models.DO_NOTHING)
    rating = models.IntegerField()
    released = models.DateField()
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title

class Reservation(models.Model):
    movie_title = models.CharField(max_length=200)
    show_time = models.DateTimeField()
    cinema = models.CharField(max_length=100)
    hall = models.CharField(max_length=50)
    tickets = models.PositiveIntegerField()
    email = models.EmailField(max_length=254)

    def __str__(self):
        return f"{self.movie_title} - {self.show_time.strftime('%Y-%m-%d %H:%M')}"


