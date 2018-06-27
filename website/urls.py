"""voong_finance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('welcome', views.welcome, name='welcome'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.login_view, name='login'),
    path('create-transaction', views.create_transaction, name='create_transaction'),
    path('modify-transaction', views.modify_transaction, name='modify_transaction'),
    path('sign-out', views.sign_out, name='sign_out'),
    path('get-balances', views.get_balances, name='get_balances'),
    path('html-snippets/repeat-transaction-deletion-prompt',
         views.get_repeat_transaction_deletion_prompt,
         name='get_repeat_transaction_deletion_prompt'),
    path('html-snippets/repeat-transaction-update-prompt',
         views.get_repeat_transaction_update_prompt,
         name='get_repeat_transaction_update_prompt'),
    path('', views.index),
    path('update-repeat-transaction',
         views.update_repeat_transaction,
         name='update_repeat_transaction'),
    path('verify-email', views.verify_email, name='verify_email'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path(
        'reset-password',
        auth_views.PasswordResetView.as_view(
            template_name='website/password_reset.html'
        )
    ),

]
