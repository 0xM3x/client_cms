from django.contrib import admin
from django.urls import path
from pages import views as page_views

urlpatterns = [
    # Put admin FIRST so it doesn't get captured by the slug route
    path("admin/", admin.site.urls),

    # Public tenant site
    path("", page_views.home_router, name="public_home"),
    path("<slug:slug>/", page_views.page_detail, name="page_detail"),
]

# Custom 404 (works when DEBUG=False)
handler404 = "pages.views.site_404"
