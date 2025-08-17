from django.contrib import admin
from django.urls import path
from pages import views as page_views

urlpatterns = [
    # Public tenant site
    path("", page_views.home_router, name="public_home"),
    path("<slug:slug>/", page_views.page_detail, name="page_detail"),

    # Admin
    path("admin/", admin.site.urls),
]

