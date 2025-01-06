from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('', views.home_view, name='home'),
    path('menu/', views.menu, name='menu'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('spotify/play/', views.play_music, name='play_music'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
    path('spotify/play_song/', views.play_song, name='play_song'),

]
