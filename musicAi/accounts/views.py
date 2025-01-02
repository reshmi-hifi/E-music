from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserUpdateForm, ProfileUpdateForm, ProfileForm
from .models import Profile

def profile_view(request):
    if request.method == 'POST':
        u_form = UserChangeForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')  # Redirect to the profile page after saving changes
    else:
        u_form = UserChangeForm(instance=request.user)
        p_form = ProfileForm(instance=request.user.profile)

    return render(request, 'profile.html', {
        'u_form': u_form,
        'p_form': p_form,
    })

# Registration View
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to the home page after successful login
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

# Home Page View
@login_required
def home_view(request):
    return render(request, 'home.html')  # Renders the home page template

@login_required
def home(request):
    return render(request, 'home.html')  # Renders the home page template

def menu(request):
    return render(request, 'menu.html')

def subscribe(request):
    return render(request, 'subscribe.html')
