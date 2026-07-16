from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from blog.api import router as blog_router

api = NinjaAPI(
    title="Blog API",
    description="A simple blog API built with Django and Ninja",
    version="1.0.0",
)
api.add_router("/", blog_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
