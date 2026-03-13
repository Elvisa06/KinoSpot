from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse
from viewer.models import  Gener,Movie
from django.db.models import Count
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from viewer.forms import MovieForm
from django.views.generic import ListView,DetailView
from .forms import ReservationForm
from .models import Reservation
from django.shortcuts import reverse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import Color
from datetime import datetime



def hello(request, name):
    return HttpResponse(f"Hello {name} from Python class!")

# Shfaq filmat
def all_geners(request):
    geners = Gener.objects.all()
    lista=[]
    for i in geners:
        lista.append(f"{i.name}, ")
    return HttpResponse(lista)


def all_movies(request):
    movies = Movie.objects.all()
    lista=[]
    for i in movies:
        lista.append(f"{i.title}, ")
    return HttpResponse(lista)





def all_information(request):
        movies = Movie.objects.select_related('gener').all().order_by('-released', 'title')
        geners = Gener.objects.all().order_by('name')

        return render(request,"viewer/all_information.html",{"movies":movies,"geners":geners})


def geners(request):
        geners = Gener.objects.annotate(movie_count=Count('movie')).order_by('name')
        return render(request,"viewer/geners_list.html",{"geners":geners})


def Movies(request):
    movies = Movie.objects.all().order_by("title")
    return render(request, "viewer/movies_list.html", {"movies": movies})

def top_rated_movies(request):
    max_rating_movie = Movie.objects.all().order_by('-rating').first()
    movies = Movie.objects.filter(rating=max_rating_movie.rating) if max_rating_movie else []
    return render(request, "viewer/top_rated_movies.html", {"movies": movies})


def find_movie(request, title):
    try:
        movie = Movie.objects.get(title=title)
        result = f"<h2>Filmi qe kerkove:</h2>"
        result += f"<li>{movie.title} ({movie.released})  <li> Rating: {movie.rating}/10 </li>  <li>Zhanri: {movie.gener.name}</li> <li>Pershkrimi: {movie.description}</li>"
    except Movie.DoesNotExist:
        result = "<h2>UPSSS,nuk eshte ne listen tende ky film.</h2>"
    return HttpResponse(result)

def movies_by_year(request, year):
    movies = Movie.objects.filter(released__year=year).order_by('title')
    return render(request, "viewer/movies_by_year.html", {
        "year": year,
        "movies": movies
    })



def movies_by_gener(request):
    gener_name = request.GET.get('gener')
    try:
        gener = Gener.objects.get(name=gener_name)
        movies = gener.movie_set.all()
        movies_data = [
            {'title': m.title} for m in movies
        ]
        return JsonResponse({'movies': movies_data})
    except Gener.DoesNotExist:
        return JsonResponse({'movies': []})



def search_movie(request, term):
    movies = Movie.objects.filter(title__icontains=term)

    if movies.exists():
        result = f"<h2 style ='color:blue'>Movies containing '{term}':</h2><ul>"
        for movie in movies:
            result += f"<li>{movie.title} ({movie.released}) - Rating: {movie.rating}/10 - Zhanri: {movie.gener.name}</li>"
        result += "</ul>"
    else:
        result = "<h2>No movies found.</h2>"

    return HttpResponse(result)





class MovieListView(ListView):
    model = Movie
    template_name = "viewer/movies_list.html"
    context_object_name = "movies"
    ordering = ["-released", "title"]

    def get_queryset(self):
        return (Movie.objects
                .select_related('genre')
                .order_by('-released', 'title'))

class MovieDetailView(DetailView):
    model = Movie
    template_name = "viewer/movie_detail.html"
    context_object_name = "movie"
    slug_field = "title"
    slug_url_kwarg = "title"

    def get_queryset(self):
        # select_related për të shmangur N+1 queries
        return Movie.objects.select_related('gener')

class MovieCreateView(CreateView):
    template_name = "viewer/movie_form.html"
    form_class = MovieForm
    success_url = reverse_lazy("index")

class MovieSearchView(ListView):
    model = Movie
    template_name = "viewer/movies_search.html"
    context_object_name = "results"

    def get_queryset(self):
        self.q = self.request.GET.get("q", "").strip()  # ruaje si atribut klase
        if self.q:
            return (Movie.objects
                    .select_related("gener")
                    .order_by("-released", "title")
                    .filter(title__icontains=self.q))
        return Movie.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.q
        ctx["count"] = ctx["results"].count()
        return ctx

class MovieUpdateView(LoginRequiredMixin,UpdateView):
    model = Movie
    form_class =  MovieForm
    template_name = "viewer/movie_form.html"
    success_url = reverse_lazy("index")

    login_url = "/admin/login/"
    redirect_field_name = "next"

class MovieDeleteView(LoginRequiredMixin,DeleteView):
    model = Movie
    from_class = MovieForm
    template_name = "viewer/movie_confirm_delete.html"
    success_url = reverse_lazy("index")

    login_url ="/admin/login/"
    redirect_field_name = "next"


class ReservationCreateView(CreateView):
    template_name = "viewer/reservation_form.html"
    form_class = ReservationForm
    success_url = reverse_lazy("reservation_success")

    def form_valid(self, form):
        reservation = form.save()

        user_email = form.cleaned_data.get('email')
        movie_title = form.cleaned_data.get('movie')
        cinema = form.cleaned_data.get('cinema')
        hall = form.cleaned_data.get('hall')
        time = form.cleaned_data.get('time')
        tickets = form.cleaned_data.get('tickets')

        # URL i faqes së rezervimit (mund ta bësh dinamik me pk)
        reservation_link = self.request.build_absolute_uri(
            reverse('reservation_detail', args=[reservation.pk])
        )

        # Logo e kinemasë (mund ta ruash në static)
        logo_url = self.request.build_absolute_uri('/static/images/cineplex_logo.png')

        html_message = render_to_string('viewer/reservation_email.html', {
            'movie_title': movie_title,
            'cinema': cinema,
            'hall': hall,
            'time': time,
            'tickets': tickets,
            'reservation_link': reservation_link,
            'logo_url': logo_url,
        })

        email = EmailMessage(
            subject='Konfirmimi i Rezervimit të Biletës',
            body=html_message,
            from_email='emaili.juaj@gmail.com',
            to=[user_email],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)

        return super().form_valid(form)



class ReservationDetailView(DetailView):
    model = Reservation
    template_name = 'viewer/reservation_detail.html'
    context_object_name = 'reservation'


def movie_detail_by_title(request, title):
    # Merr filmin sipas titullit (case-insensitive)
    movie = get_object_or_404(
        Movie.objects.select_related('gener'),  # lidhet me gjininë
        title__iexact=title  # kërkim pa marrë parasysh shkronjat
    )
    return render(request, 'viewer/movie_detail.html', {'movie': movie})

def all_movies(request):
    movies = Movie.objects.all()
    return render(request, "viewer/movies_list.html", {"movies": movies})

from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
import os
from django.conf import settings
import qrcode
from io import BytesIO
from reportlab.lib.utils import ImageReader




def download_ticket(request):
    data = request.session.get('ticket_data')
    if not data:
        return redirect('reservation_form')    #Merr të dhenat e rezervimit,Kontrollon
                                               # nese ekziston 1 objekt ticket_data nsession.
                                               # if no kthen te rservation_form


    response = HttpResponse(content_type='application/pdf') #Krijon nje pergjigje HTTP si PDF dhe krijon emrin e file
    response['Content-Disposition'] = f'attachment; filename="ticket_{data.get("movie_title","ticket")}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # --- Sfondo i faqes: pak i zbehtë ---
    p.setFillColor(colors.HexColor("#FFDFDF"))
    p.rect(0, 0, width, height, fill=1, stroke=0)

    # --- Titulli ne krye ---
    p.setFont("Courier-BoldOblique", 28)
    p.setFillColor(colors.HexColor("#D72631"))
    p.drawCentredString(width / 2, height - 3*cm, "Movie Ticket")

    # Vijë ndarëse
    p.setStrokeColor(colors.HexColor("#D72631"))
    p.setLineWidth(2)
    p.line(2*cm, height-3.7*cm, width-2*cm, height-3.7*cm)

    # --- Kuti e mesazhit me sfond të bardhë ---
    details_top = height - 5*cm
    details_height = 11*cm
    box_bottom = details_top - details_height
    p.setFillColor(colors.white)
    p.roundRect(2*cm, box_bottom, width - 4*cm, details_height, 10, fill=1, stroke=0)

    # --- Parametra për mesazhin ---
    margin_x = 2.5*cm
    line_spacing = 1.4*cm
    red_color = colors.HexColor("#D72631")
    max_width = width - 2*margin_x

    cinema_name = data.get('cinema', '')
    full_message = (
        f"We’re thrilled to welcome you to {cinema_name} to enjoy the movie you’ve been assigned, "
        f"whether you’re coming solo or with friends. Grab some tasty popcorn, sit back, and let the adventure unfold on the big screen. "
        f"We hope you have an amazing time!"
    )

    def wrap_text_natural(text_string, max_width, canvas_obj, fontname="Helvetica", fontsize=13):
        words = text_string.split(' ')
        line = ""
        for word in words:
            test_line = line + word + " "
            if canvas_obj.stringWidth(test_line, fontname, fontsize) > max_width:
                yield line.strip()
                line = word + " "
            else:
                line = test_line
        if line:
            yield line.strip()

    # Llogarit lartësinë totale të tekstit
    num_lines_message = len(list(wrap_text_natural(full_message, max_width, p)))
    total_text_height = line_spacing * (1 + num_lines_message + 1)

    # Pozicioni vertikal i mesazhit në mes të kutisë
    info_y = box_bottom + (details_height + total_text_height)/2 - line_spacing

    # 1️⃣ Rreshti i parë: "Hello [Emri]!"
    hello_text = "Hello "
    name_text = data.get('full_name', '')
    p.setFont("Helvetica", 13)
    p.setFillColor(red_color)
    p.drawString(margin_x, info_y, hello_text)
    hello_width = p.stringWidth(hello_text, "Helvetica", 13)
    p.setFont("Helvetica-Bold", 13)
    p.drawString(margin_x + hello_width, info_y, name_text + "!")
    info_y -= line_spacing

    # 2️⃣ Mesazhi kryesor – wrap dhe drawText
    text = p.beginText()
    text.setTextOrigin(margin_x, info_y)
    text.setFillColor(red_color)
    text.setFont("Helvetica", 13)
    for line in wrap_text_natural(full_message, max_width, p):
        text.textLine(line)
    p.drawText(text)

    # Vendos info_y për rreshtin e tretë me hapësirë të bollshme
    info_y -= line_spacing * 2

    # 3️⃣ Fjalia për QR code – rresht i tretë
    last_line = "Don’t forget to scan the QR code to view all your reservation details."
    p.setFont("Helvetica", 13)
    p.setFillColor(red_color)
    p.drawString(margin_x, info_y, last_line)

    # --- QR Code shumë poshtë mbi footer ---
    qr_data = f"""
KinoSpot Ticket
Name: {data.get('full_name', '')}
Movie: {data.get('movie_title', '')}
Show Time: {data.get('show_time', '')}
Cinema: {data.get('cinema', '')}
Hall: {data.get('hall', '')}
Tickets: {data.get('tickets', '')}
Reserved for: {data.get('email', '')}
"""
    qr_img = qrcode.make(qr_data)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    qr_reader = ImageReader(buffer)

    qr_x = width - 6*cm
    qr_y = 2*cm + 1*cm  # pak mbi footer
    p.drawImage(qr_reader, qr_x, qr_y, width=5*cm, height=5*cm)

    # Teksti mbi QR Code (qendër)
    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(red_color)
    p.drawCentredString(qr_x + 2.5*cm, qr_y + 5*cm + 0.2*cm, "Scan Me")

    # KinoSpot dhe Where movies meet you! – majtas QR, larg QR dhe vertikalisht njëri mbi tjetrin
    kino_x = qr_x - 8*cm  # larg nga QR
    kino_y = qr_y + 4*cm

    # KinoSpot – Bold + Italic, më i madh
    p.setFont("Helvetica-BoldOblique", 20)
    p.setFillColor(red_color)
    p.drawString(kino_x, kino_y, "KinoSpot")

    # Where movies meet you! – poshtë KinoSpot, pak më majtas, shkrim normal, më i madh
    p.setFont("Helvetica", 14)
    p.drawString(kino_x - 1.2*cm, kino_y - 1*cm, "Where movies meet you!")

    # Kufiri rreth kutisë
    p.setStrokeColor(colors.HexColor("#D72631"))
    p.setLineWidth(1)
    p.roundRect(2*cm, box_bottom, width - 4*cm, details_height, 10, stroke=1, fill=0)

    # --- Footer ---
    p.setFillColor(colors.HexColor("#B22222"))
    p.rect(0, 0, width, 2*cm, fill=1, stroke=0)
    p.setFillColor(colors.white)
    p.setFont("Helvetica", 10)
    footer_text = "Phone: +355 68 5445 900 | Gmail: info@kinospot.al | Instagram: kinospot_albania | Location: Cinemplex QTU/TEG"
    p.drawCentredString(width / 2, 0.7*cm, footer_text)

    p.showPage()
    p.save()

    return response


def reservation_confirm(request):
    if request.method == "POST":
        # Merr të dhënat nga forma
        full_name = request.POST.get("full_name")
        movie_id = request.POST.get("movie_title")
        movie = get_object_or_404(Movie, id=movie_id)

        show_time_str = request.POST.get("show_time")
        # Konverto në datetime për template
        show_time_dt = datetime.strptime(show_time_str, "%Y-%m-%dT%H:%M")
        # Ruaj në session si string të formatit "dd/mm/yyyy HH:MM"
        formatted_show_time = show_time_dt.strftime("%d/%m/%Y %H:%M")

        data = {
            'full_name': full_name,             # shtuar Full Name
            'movie_title': movie.title,
            'show_time': formatted_show_time,   # string, jo datetime
            'cinema': request.POST.get("cinema"),
            'hall': request.POST.get("hall"),
            'tickets': request.POST.get("tickets"),
            'email': request.POST.get("email"),
        }

        request.session['ticket_data'] = data  # ruaj në session
        return render(request, 'viewer/reservation_confirm.html', {'data': data})

    return redirect('reservation_form')