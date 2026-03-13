from django import forms
from viewer.models import Movie ,Reservation

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ["title", "gener", "rating", "released", "description"]

from django import forms
from .models import Reservation, Movie


CINEMA_CHOICES = [
    ('TEG', 'Cineplex TEG'),
    ('QTU', 'Cineplex QTU'),
]

class ReservationForm(forms.ModelForm):
    full_name = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'required': True
        })
    )

    movie_title = forms.ModelChoiceField(
        queryset=Movie.objects.all(),
        label="Movie Title",
        empty_label=None,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Choose a movie'
        })
    )

    cinema = forms.ChoiceField(
        choices=CINEMA_CHOICES,
        label="Cinema",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Choose the cinema'
        })
    )

    hall = forms.ChoiceField(
        choices=[],
        label="Hall",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Choose the hall'
        })
    )

    email = forms.EmailField(
        label="Your Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )


    class Meta:
        model = Reservation
        fields = ['full_name', 'movie_title', 'show_time', 'cinema', 'hall', 'tickets', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Enter your full name'  # placeholder për emrin
            }),
            'movie_title': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Choose a movie'  # placeholder për movie
            }),
            'show_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'placeholder': 'dd/mm/yyyy --:--'
            }),
            'cinema': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Choose the cinema'  # placeholder për cinema
            }),
            'hall': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Choose the hall'  # placeholder për hall
            }),
            'tickets': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Enter number of tickets'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
        }

    def save(self, commit=True):
        reservation = super().save(commit=False)
        reservation.movie_title = self.cleaned_data['movie_title'].title
        reservation.hall = self.cleaned_data['hall']
        reservation.email = self.cleaned_data['email']
        if commit:
            reservation.save()
        return reservation

