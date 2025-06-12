from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegisterUserForm, UserUpdateForm, ProfileUpdateForm, EmailAuthenticationForm

class LoginUser(LoginView):
    form_class = EmailAuthenticationForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Вход'}

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('home')

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if 'username' in form.errors:
            form.errors['username'] = ['Пожалуйста, введите правильный email.']
        return response

class LogoutUser(LogoutView):
    next_page = reverse_lazy('users:login')

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Аккаунт {username} успешно создан!')
        return response

class ProfileUser(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/profile.html'
    extra_context = {'title': 'Профиль'}
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['p_form'] = ProfileUpdateForm(self.request.POST, self.request.FILES, instance=self.request.user.profile)
        else:
            context['p_form'] = ProfileUpdateForm(instance=self.request.user.profile)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        p_form = context['p_form']
        if p_form.is_valid():
            p_form.save()
            messages.success(self.request, 'Ваш профиль успешно обновлен!')
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))
