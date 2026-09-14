from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="MenuCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["sort_order", "name"]},
        ),
        migrations.CreateModel(
            name="MenuItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("marathi_name", models.CharField(blank=True, max_length=160)),
                ("price", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("item_type", models.CharField(default="Veg", max_length=30)),
                ("available", models.BooleanField(default=True)),
                ("active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="portal.menucategory")),
            ],
            options={"ordering": ["category__sort_order", "sort_order", "name"]},
        ),
        migrations.CreateModel(
            name="ServiceCall",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("table_number", models.CharField(db_index=True, max_length=30)),
                ("request_type", models.CharField(choices=[("Service","Service"),("Water","Water"),("Bill","Bill"),("Assistance","Assistance")], default="Service", max_length=50)),
                ("status", models.CharField(choices=[("pending","Pending"),("acknowledged","Acknowledged"),("completed","Completed")], db_index=True, default="pending", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("acknowledged_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
