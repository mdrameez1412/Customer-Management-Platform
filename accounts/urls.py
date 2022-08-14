from django.urls import path
from .import views
urlpatterns = [
    path('register/',views.registerpage, name="register"),
    path('login/',views.loginpage,name="login"),
    path('logout/',views.logoutuser,name="logout"),
    path('', views.home,name="home"),
    path('user/', views.userPage, name="user-page"),
    path('account/', views.accountSettings, name='account'),
    path('products/', views.products, name="products"),
    path('customer/<str:pk>/', views.customers,name="customer"),
    path('create_order/<str:pk>',views.createorders,name='create_order'),
    path('update_order/<str:pk>',views.updateorder,name='update_order'),
    path('delete_order/<str:pk>',views.deleteorder,name='delete_order'),
]