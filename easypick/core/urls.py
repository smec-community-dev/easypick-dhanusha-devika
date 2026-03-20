from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('',views.main_home_view,name="main_home"),
    path('login/',views.login_view,name="login"),
    path('logout/',views.logout_view,name='logout'),
    path('admin_login/',views.admin_view,name="admin_login"),
    path('shop/',views.shop_view,name='shop'),
    path('about/',views.about_view,name='about'),
    path('contact/',views.contact_view,name='contact'),
    path('forgot-password/', auth_views.PasswordResetView.as_view( template_name='core/password_reset.html' ), name='password_reset'), 
    path('forgot-password/done/', auth_views.PasswordResetDoneView.as_view( template_name='core/password_reset_done.html' ), name='password_reset_done'), 
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view( template_name='core/password_reset_confirm.html' ), name='password_reset_confirm'), 
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view( template_name='core/password_reset_complete.html' ), name='password_reset_complete')
    
]
