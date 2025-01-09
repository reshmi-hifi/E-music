from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileForm
from .models import Profile, Notification  # Added Notification
import os
import requests

# Function to create default notifications for users
def create_default_notifications(user):
    Notification.objects.create(
        user=user,
        message="Welcome to our platform! Check out our new subscription offer!",
        is_read=False
    )
    Notification.objects.create(
        user=user,
        message="Don't forget to check your profile for updates!",
        is_read=False
    )
    Notification.objects.create(
        user=user,
        message="Stay tuned for upcoming promotions and updates.",
        is_read=False
    )

# Profile View
@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserChangeForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()  # Save user form data (username, etc.)
            p_form.save()  # Save profile form data (bio, profile_picture, etc.)
            return redirect('profile')  # Redirect to the same profile page after successful save
    else:
        u_form = UserChangeForm(instance=request.user)
        p_form = ProfileForm(instance=request.user.profile)

    return render(request, 'profile.html', {'u_form': u_form, 'p_form': p_form})


# Registration View
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            create_default_notifications(user)  # Create default notifications after user registers
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                create_default_notifications(user)  # Create default notifications when user logs in
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

# Home View
@login_required
def home_view(request):
    return render(request, 'home.html')

# Menu View
def menu(request):
    return render(request, 'menu.html')

# Subscribe View
def subscribe(request):
    return render(request, 'subscribe.html')

# Notifications View
@login_required
def notifications_view(request):
    # Check if the user already has notifications
    if not Notification.objects.filter(user=request.user).exists():
        # Create default notifications if none exist
        Notification.objects.create(
            user=request.user,
            message="Welcome to our service! Stay tuned for updates.",
            is_read=False
        )
        Notification.objects.create(
            user=request.user,
            message="Check out our new subscription features.",
            is_read=False
        )
        Notification.objects.create(
            user=request.user,
            message="Don't miss our upcoming events!",
            is_read=False
        )

        # Fetch the notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})


# Spotify API Views
def play_music(request):
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
    scope = 'user-read-playback-state user-modify-playback-state streaming'

    spotify_auth_url = (
        f"https://accounts.spotify.com/authorize?client_id={client_id}"
        f"&response_type=code&redirect_uri={redirect_uri}"
        f"&scope={scope}"
    )
    return redirect(spotify_auth_url)

def spotify_callback(request):
    print("Callback hit")  # Debugging line
    code = request.GET.get('code')
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret,
        }
    )

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')

        # Store the access token and refresh token in session
        request.session['spotify_access_token'] = access_token
        request.session['spotify_refresh_token'] = refresh_token

        # Debugging lines to verify the access and refresh tokens
        print("Access Token:", access_token)
        print("Refresh Token:", refresh_token)

        return redirect('play_song')  # Redirect to play_song after getting the access token
    else:
        print(response.json())  # Print error if token exchange failed
        return JsonResponse({'error': 'Authentication failed'}, status=400)

def play_song(request):
    access_token = request.session.get('spotify_access_token')
    if not access_token:
        print("No access token found")  # Debugging line
        return JsonResponse({'error': 'User not authenticated'}, status=403)

    # Set the track URI (replace with the URI of a song you want to play)
    track_uri = "spotify:track:2WO5nzB7QtKn9ZRc9Jkalt"  # Another valid track URI (replace with your desired track URI)

    response = requests.put(
        "https://api.spotify.com/v1/me/player/play",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"uris": [track_uri]}  # Play this track
    )

    if response.status_code == 204:
        return JsonResponse({'message': 'Playback started'})
    else:
        print(response.json())  # Print the response error
        return JsonResponse({'error': response.json()}, status=response.status_code)
