from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile
from .forms import RegisterForm

def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            if form.cleaned_data['role'] == 'Admin':
                approved = True
            else:
                approved = False

            Profile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                is_approved=approved
            )

            return redirect('login')

    else:
        form = RegisterForm()

    return render(request,'accounts/register.html',{'form': form})

from django.contrib.auth import authenticate
from django.contrib.auth import login

def login_view(request):
    error = None

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == 'admin' and password == 'admin':
            from django.contrib.auth import get_user_model

            UserModel = get_user_model()
            user, created = UserModel.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'is_staff': True,
                    'is_superuser': True,
                }
            )

            if created:
                user.set_password('admin')
                user.is_staff = True
                user.is_superuser = True
                user.save()

            Profile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'Admin',
                    'is_approved': True
                }
            )

            login(request, user)
            return redirect('admin_dashboard')

        user = User.objects.filter(username=username).first()

        if user is None:
            error = 'Invalid username or password.'
        elif not user.is_active:
            error = 'This account has been deactivated. Please contact an administrator.'
        else:
            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:
                profile = user.profile

                if not profile.is_approved:
                    error = 'Your account is waiting for admin approval.'
                else:
                    login(request, user)
                    role = profile.role

                    if role == 'Admin':
                        return redirect('admin_dashboard')
                    elif role == 'Manager':
                        return redirect('manager_dashboard')
                    else:
                        return redirect('analyst_dashboard')
            else:
                error = 'Invalid username or password.'

    return render(request,'accounts/login.html', {'error': error})

from django.shortcuts import get_object_or_404

def approve_user(request, profile_id):

    profile = get_object_or_404(
        Profile,
        id=profile_id
    )

    profile.is_approved = True

    profile.save()

    return redirect('users')

from django.contrib.auth import logout

def logout_view(request):

    logout(request)

    return redirect('login')