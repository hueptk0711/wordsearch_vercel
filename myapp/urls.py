from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from myproject import settings
from django.urls import path
from . import views
import sys

print(sys.executable)
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('wordsearch', views.wordsearch, name='wordsearch'),
    path('generate', views.generate, name="generate"),
    path('guide', views.guide,name="guide" ),
    path('about_us',views.about_us, name="about_us"),
    path('home',views.home, name="home"),
    path('download/<str:pdf_filename>/', views.download, name='download'),  # Route to download function
] 

urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
urlpatterns += staticfiles_urlpatterns()