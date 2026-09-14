from django.contrib import admin
from django.contrib import messages
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from .models import (
    MenuCategory,
    MenuItem,
    ServiceCall,
    TableQRCode,
    PortalSettings,
)
from . import views
from .menu_excel import export_menu, import_menu


# ============================================================
# MENU CATEGORY
# ============================================================

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "active",
        "sort_order",
    )

    list_editable = (
        "active",
        "sort_order",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "sort_order",
        "name",
    )


# ============================================================
# MENU ITEM
# ============================================================

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "marathi_name",
        "category",
        "price",
        "item_type",
        "available",
        "active",
    )

    list_filter = (
        "category",
        "item_type",
        "available",
        "active",
    )

    list_editable = (
        "price",
        "available",
        "active",
    )

    search_fields = (
        "name",
        "marathi_name",
    )

    list_select_related = (
        "category",
    )

    # ========================================================
    # ADMIN ACTIONS
    # ========================================================

    actions = (
        "export_menu_excel",
        "open_import_excel",
    )

    @admin.action(description="Export complete menu to Excel")
    def export_menu_excel(self, request, queryset):
        """
        Export the complete restaurant menu.

        The selected MenuItems are intentionally ignored because
        export_menu() exports the complete menu structure.
        """

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

        workbook.save(response)

        return response

    @admin.action(description="Import / Upload menu Excel")
    def open_import_excel(self, request, queryset):
        """
        Open the Admin Excel import page.

        Django Admin actions are POST based, so this action
        redirects the administrator to the upload page.
        """

        return HttpResponseRedirect(
            reverse("admin:portal_menu_import")
        )

    # ========================================================
    # CUSTOM ADMIN URL
    # ========================================================

    def get_urls(self):
        """
        Add the Excel import page to Django Admin.
        """

        urls = super().get_urls()

        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(
                    views.menu_import
                ),
                name="portal_menu_import",
            ),
        ]

        return custom_urls + urls


# ============================================================
# SERVICE CALL
# ============================================================

@admin.register(ServiceCall)
class ServiceCallAdmin(admin.ModelAdmin):

    list_display = (
        "table_number",
        "request_type",
        "status",
        "created_at",
        "acknowledged_at",
        "completed_at",
    )

    list_filter = (
        "status",
        "request_type",
    )

    search_fields = (
        "table_number",
    )

    readonly_fields = (
        "created_at",
        "acknowledged_at",
        "completed_at",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# TABLE QR CODE
# ============================================================

@admin.register(TableQRCode)
class TableQRCodeAdmin(admin.ModelAdmin):

    list_display = (
        "table_number",
        "active",
        "created_at",
        "download_qr",
    )

    list_filter = (
        "active",
    )

    search_fields = (
        "table_number",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "table_number",
    )

    def get_urls(self):
        """
        Add custom QR poster download URL.

        IMPORTANT:
        The URL uses `object_id`, therefore
        download_table_qr() accepts object_id.
        """

        urls = super().get_urls()

        custom_urls = [
            path(
                "<path:object_id>/download-qr/",
                self.admin_site.admin_view(
                    views.download_table_qr
                ),
                name="portal_tableqrcode_download",
            ),
        ]

        return custom_urls + urls

    @admin.display(description="Print QR")
    def download_qr(self, obj):
        """
        Generate / Download QR poster button.
        """

        url = reverse(
            "admin:portal_tableqrcode_download",
            args=[obj.pk],
        )

        return format_html(
            '<a class="button" href="{}">'
            'Generate / Download Poster'
            "</a>",
            url,
        )


# ============================================================
# PORTAL SETTINGS
# ============================================================

@admin.register(PortalSettings)
class PortalSettingsAdmin(admin.ModelAdmin):

    list_display = (
        "public_portal_url",
        "qr_title",
        "active",
        "updated_at",
    )

    list_filter = (
        "active",
    )

    search_fields = (
        "public_portal_url",
        "qr_title",
    )

    readonly_fields = (
        "updated_at",
    )

    def has_add_permission(self, request):
        """
        Allow only one PortalSettings record.
        """

        return not PortalSettings.objects.exists()

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):
        """
        Ensure only one PortalSettings record
        is active at a time.
        """

        if obj.active:
            PortalSettings.objects.exclude(
                pk=obj.pk
            ).update(
                active=False
            )

        super().save_model(
            request,
            obj,
            form,
            change,
        )


# ============================================================
# ADMIN BRANDING
# ============================================================

admin.site.site_header = (
    "Coastal Pearl · Administration"
)

admin.site.site_title = (
    "Coastal Pearl Admin"
)

admin.site.index_title = (
    "Restaurant Management"
)