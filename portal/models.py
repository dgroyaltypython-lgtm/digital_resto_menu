from django.db import models


class MenuCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=160)
    marathi_name = models.CharField(max_length=160, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    item_type = models.CharField(max_length=30, default="Veg")
    available = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["category__sort_order", "sort_order", "name"]
        indexes = [
            models.Index(fields=["active", "available"]),
            models.Index(fields=["category", "active"]),
        ]

    def __str__(self):
        return self.name


class ServiceCall(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("acknowledged", "Acknowledged"),
        ("completed", "Completed"),
    ]
    REQUEST_TYPES = [
        ("Service", "Service"),
        ("Water", "Water"),
        ("Bill", "Bill"),
        ("Assistance", "Assistance"),
    ]

    table_number = models.CharField(max_length=30, db_index=True)
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPES, default="Service")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["table_number", "status"]),
        ]


class TableQRCode(models.Model):
    table_number = models.CharField(max_length=30, unique=True, db_index=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["table_number"]

    def __str__(self):
        return f"Table {self.table_number}"


class PortalSettings(models.Model):
    public_portal_url = models.URLField(
        max_length=500,
        help_text="Example: https://yourusername.pythonanywhere.com",
    )
    qr_title = models.CharField(
        max_length=200,
        default="Group of BBN Coastal Pearl Samudrathali",
    )
    qr_message = models.CharField(
        max_length=300,
        default='Digital Menu - "Scan QR and check our menu"',
    )
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Portal Settings"
        verbose_name_plural = "Portal Settings"

    def __str__(self):
        return "Portal Settings"
