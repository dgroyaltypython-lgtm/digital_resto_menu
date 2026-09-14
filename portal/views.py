import json
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .models import (
    MenuCategory,
    ServiceCall,
    TableQRCode,
    PortalSettings,
)
from .menu_excel import export_menu, import_menu
from .qr_utils import create_table_qr_poster


# ============================================================
# CUSTOMER MENU
# ============================================================

def menu(request):
    table = (
        request.GET.get("table", "").strip()
        or "GUEST"
    )

    categories = (
        MenuCategory.objects
        .filter(active=True)
        .prefetch_related("items")
    )

    return render(
        request,
        "portal/menu.html",
        {
            "categories": categories,
            "table": table,
        },
    )


# ============================================================
# CUSTOMER GAMES
# ============================================================

def games(request):
    table = (
        request.GET.get("table", "").strip()
        or "GUEST"
    )

    return render(
        request,
        "portal/games.html",
        {
            "table": table,
        },
    )


# ============================================================
# COUNTER LOGIN
# ============================================================

@ensure_csrf_cookie
def counter_login(request):

    if (
        request.user.is_authenticated
        and request.user.is_staff
    ):
        return redirect(
            "portal:counter_dashboard"
        )

    return render(
        request,
        "portal/counter_login.html",
    )


# ============================================================
# COUNTER DASHBOARD
# ============================================================

@login_required
def counter_dashboard(request):

    if not request.user.is_staff:
        logout(request)

        return redirect(
            "portal:counter_login"
        )

    return render(
        request,
        "portal/counter.html",
    )


# ============================================================
# COUNTER LOGIN API
# ============================================================

@require_POST
def counter_login_api(request):

    try:
        data = json.loads(
            request.body or "{}"
        )
    except (
        json.JSONDecodeError,
        TypeError,
    ):
        data = {}

    username = str(
        data.get("username", "")
    ).strip()

    password = str(
        data.get("password", "")
    )

    if not username or not password:
        return JsonResponse(
            {
                "ok": False,
                "message": (
                    "Username and password "
                    "are required."
                ),
            },
            status=400,
        )

    user = authenticate(
        request,
        username=username,
        password=password,
    )

    if user is None:
        return JsonResponse(
            {
                "ok": False,
                "message": (
                    "Invalid username or password."
                ),
            },
            status=401,
        )

    if not user.is_active:
        return JsonResponse(
            {
                "ok": False,
                "message": (
                    "This account is inactive."
                ),
            },
            status=403,
        )

    if not user.is_staff:
        return JsonResponse(
            {
                "ok": False,
                "message": (
                    "This account is not authorized "
                    "for the counter."
                ),
            },
            status=403,
        )

    login(
        request,
        user,
    )

    return JsonResponse(
        {
            "ok": True,
            "message": (
                "Counter login successful."
            ),
        }
    )


# ============================================================
# CUSTOMER SERVICE CALL
# ============================================================

@require_POST
def service_call(request):

    try:
        data = json.loads(
            request.body or "{}"
        )
    except (
        json.JSONDecodeError,
        TypeError,
    ):
        data = {}

    table = str(
        data.get("table", "")
    ).strip()[:30]

    request_type = str(
        data.get(
            "request_type",
            "Service",
        )
    ).strip()[:50]

    if not table:
        return JsonResponse(
            {
                "ok": False,
                "message": (
                    "Table number is missing."
                ),
            },
            status=400,
        )

    if not request_type:
        request_type = "Service"

    existing = (
        ServiceCall.objects
        .filter(
            table_number=table,
            status="pending",
        )
        .first()
    )

    if existing:
        return JsonResponse(
            {
                "ok": True,
                "id": existing.id,
                "message": (
                    "Your request is already "
                    "with our team."
                ),
            }
        )

    call = ServiceCall.objects.create(
        table_number=table,
        request_type=request_type,
        status="pending",
    )

    return JsonResponse(
        {
            "ok": True,
            "id": call.id,
            "message": (
                "Service team notified."
            ),
        }
    )


# ============================================================
# SERVICE CALL SERIALIZER
# ============================================================

def serialize(call):

    created_at = call.created_at

    if timezone.is_aware(created_at):
        created_at = timezone.localtime(
            created_at
        )

    return {
        "id": call.id,
        "table_number": call.table_number,
        "request_type": call.request_type,
        "status": call.status,
        "created_at": created_at.strftime(
            "%d %b %Y, %I:%M:%S %p"
        ),
    }


# ============================================================
# COUNTER SERVICE CALLS
# ============================================================

@login_required
def service_calls(request):

    if not request.user.is_staff:
        return JsonResponse(
            {
                "calls": [],
            },
            status=403,
        )

    calls = (
        ServiceCall.objects
        .filter(
            status__in=[
                "pending",
                "acknowledged",
            ]
        )
        .order_by(
            "-created_at"
        )[:100]
    )

    return JsonResponse(
        {
            "calls": [
                serialize(call)
                for call in calls
            ]
        }
    )


# ============================================================
# UPDATE SERVICE CALL STATUS
# ============================================================

@require_POST
@login_required
def update_call_status(request, call_id):

    if not request.user.is_staff:
        return JsonResponse(
            {
                "ok": False,
                "message": "Not authorized.",
            },
            status=403,
        )

    try:
        call = ServiceCall.objects.get(
            pk=call_id
        )
    except ServiceCall.DoesNotExist:
        return JsonResponse(
            {
                "ok": False,
                "message": (
                    "Service call not found."
                ),
            },
            status=404,
        )

    try:
        data = json.loads(
            request.body or "{}"
        )
    except (
        json.JSONDecodeError,
        TypeError,
    ):
        data = {}

    status = data.get("status")

    if status not in {
        "acknowledged",
        "completed",
    }:
        return JsonResponse(
            {
                "ok": False,
                "message": "Invalid status.",
            },
            status=400,
        )

    now = timezone.now()

    if status == "acknowledged":

        call.status = "acknowledged"
        call.acknowledged_at = now

        call.save(
            update_fields=[
                "status",
                "acknowledged_at",
            ]
        )

    else:

        call.status = "completed"
        call.completed_at = now

        call.save(
            update_fields=[
                "status",
                "completed_at",
            ]
        )

    return JsonResponse(
        {
            "ok": True,
            "call": serialize(call),
        }
    )


# ============================================================
# COUNTER LOGOUT
# ============================================================

def counter_logout(request):

    logout(request)

    return redirect(
        "counter_login"
    )


# ============================================================
# STAFF CHECK
# ============================================================

def _staff_user(request):

    return (
        request.user.is_authenticated
        and request.user.is_staff
    )


# ============================================================
# MENU EXCEL IMPORT
# ============================================================

@login_required
def menu_import(request):
    """
    Excel upload page opened from the Django Admin action.
    """

    if not _staff_user(request):
        return redirect(
            "admin:login"
        )

    if request.method == "POST":

        uploaded = request.FILES.get(
            "menu_file"
        )

        if not uploaded:

            messages.error(
                request,
                "Please choose an .xlsx file.",
            )

            return redirect(
                "admin:portal_menu_import"
            )

        if not uploaded.name.lower().endswith(
            ".xlsx"
        ):

            messages.error(
                request,
                "Only .xlsx Excel files are supported.",
            )

            return redirect(
                "admin:portal_menu_import"
            )

        try:

            result = import_menu(
                uploaded
            )

            messages.success(
                request,
                (
                    "Menu imported successfully: "
                    f"{result['imported']} rows "
                    f"({result['created']} created, "
                    f"{result['updated']} updated)."
                ),
            )

            return redirect(
                "admin:portal_menuitem_changelist"
            )

        except Exception as exc:

            messages.error(
                request,
                f"Import failed: {exc}",
            )

            return redirect(
                "admin:portal_menu_import"
            )

    return render(
        request,
        "admin/portal/menu_import.html",
    )


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def menu_import_export(request):
    return menu_import(request)


# ============================================================
# MENU EXPORT
# ============================================================

@login_required
def menu_export(request):

    if not _staff_user(request):
        return redirect(
            "admin:login"
        )

    workbook = export_menu()

    response = HttpResponse(
        content_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        'attachment; filename="Coastal_Pearl_Menu.xlsx"'
    )

    workbook.save(
        response
    )

    return response


# ============================================================
# TABLE QR POSTER DOWNLOAD
# ============================================================

def download_table_qr(
    request,
    object_id=None,
    table_id=None,
):
    """
    Generate and download a table QR poster.

    Admin URL:

        <path:object_id>/download-qr/

    Therefore object_id is accepted.

    table_id remains supported for compatibility.
    """

    # --------------------------------------------------------
    # Resolve primary key
    # --------------------------------------------------------

    table_pk = (
        object_id
        if object_id is not None
        else table_id
    )

    if table_pk is None:

        return HttpResponse(
            "Table QR code ID is missing.",
            status=400,
        )

    # --------------------------------------------------------
    # Find table
    # --------------------------------------------------------

    try:

        table = TableQRCode.objects.get(
            pk=table_pk
        )

    except TableQRCode.DoesNotExist:

        return HttpResponse(
            "Table QR code not found.",
            status=404,
        )

    # --------------------------------------------------------
    # Active check
    # --------------------------------------------------------

    if not table.active:

        return HttpResponse(
            "This table QR code is inactive.",
            status=404,
        )

    # --------------------------------------------------------
    # Active portal settings
    # --------------------------------------------------------

    settings = (
        PortalSettings.objects
        .filter(active=True)
        .order_by("-updated_at")
        .first()
    )

    if (
        not settings
        or not settings.public_portal_url
    ):

        return HttpResponse(
            (
                "Set an active Public Portal URL "
                "in Admin → Portal Settings "
                "before generating QR codes."
            ),
            status=400,
        )

    # --------------------------------------------------------
    # Build menu URL
    # --------------------------------------------------------

    base_url = (
        settings.public_portal_url
        .strip()
        .rstrip("/")
    )

    menu_url = (
        f"{base_url}/menu/"
        f"?{urlencode({'table': table.table_number})}"
    )

    # --------------------------------------------------------
    # Generate poster
    # --------------------------------------------------------

    poster = create_table_qr_poster(
        table.table_number,
        menu_url,
        title=settings.qr_title,
        message=settings.qr_message,
    )

    # --------------------------------------------------------
    # PNG response
    # --------------------------------------------------------

    response = HttpResponse(
        poster.getvalue(),
        content_type="image/png",
    )

    safe_table = "".join(
        ch
        if ch.isalnum() or ch in "-_"
        else "_"
        for ch in table.table_number
    )

    response["Content-Disposition"] = (
        "attachment; "
        f'filename="Coastal_Pearl_Table_'
        f'{safe_table}_QR.png"'
    )

    return response