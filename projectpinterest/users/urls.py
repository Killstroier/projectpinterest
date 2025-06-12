from django.urls import path, reverse_lazy
from .views import LoginUser, LogoutUser, RegisterUser, ProfileUser
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutUser.as_view(), name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('profile/', ProfileUser.as_view(), name='profile'),
    path('password/', auth_views.PasswordChangeView.as_view(
        template_name='users/password_change.html',
        success_url='/users/password/done/'
    ), name='password_change'),
    path('password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='users/password_change_done.html'
    ), name='password_change_done'),
    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html',
        success_url=reverse_lazy('users:password_reset_done')
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'), name='password_reset_complete'),
] 