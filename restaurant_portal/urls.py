from django.contrib import admin
from django.urls import include, path
from portal import views

urlpatterns = [
    path("admin/menu-import-export/", views.menu_import_export, name="admin_menu_import_export"),
    path("admin/menu-export/", views.menu_export, name="admin_menu_export"),
    path("admin/", admin.site.urls),
    path("", include("portal.urls")),
]
