from django.urls import path

from . import views


app_name = "portal"


urlpatterns = [

    # ========================================================
    # CUSTOMER PORTAL
    # ========================================================

    path(
        "menu/",
        views.menu,
        name="menu",
    ),

    path(
        "games/",
        views.games,
        name="games",
    ),

    # ========================================================
    # COUNTER
    # ========================================================

    path(
        "counter/login/",
        views.counter_login,
        name="counter_login",
    ),

    path(
        "counter/",
        views.counter_dashboard,
        name="counter_dashboard",
    ),

    path(
        "counter/logout/",
        views.counter_logout,
        name="counter_logout",
    ),

    # ========================================================
    # COUNTER APIs
    # ========================================================

    path(
        "api/counter-login/",
        views.counter_login_api,
        name="counter_login_api",
    ),

    path(
        "api/service-call/",
        views.service_call,
        name="service_call",
    ),

    path(
        "api/service-calls/",
        views.service_calls,
        name="service_calls",
    ),

    path(
        "api/service-call/<int:call_id>/status/",
        views.update_call_status,
        name="update_call_status",
    ),

    # ========================================================
    # OPTIONAL PUBLIC/LEGACY EXCEL URLs
    # ========================================================
    #
    # These are kept for compatibility.
    #
    # The actual Admin actions use:
    #
    #   admin:portal_menu_import
    #
    # and export_menu_excel() directly.
    #

    path(
        "admin/menu/import/",
        views.menu_import,
        name="menu_import",
    ),

    path(
        "admin/menu/export/",
        views.menu_export,
        name="menu_export",
    ),
]