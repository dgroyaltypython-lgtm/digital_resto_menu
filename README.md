# Coastal Pearl QR Service Portal — V5

Production-oriented Django package for the Coastal Pearl digital menu, table service counter, games and table QR management.

## Included
- Customer menu with table-aware QR URLs.
- 10 touch-friendly games with preserved glassmorphism styling.
- Live counter service-call dashboard.
- Admin menu category/item management.
- Admin Menu Excel import/export.
- Admin Portal Settings for the public production URL.
- Admin Table QR management with print-ready PNG poster download.
- WhiteNoise static-file configuration.
- PythonAnywhere-friendly environment configuration.

## Local run
1. Create/activate a virtual environment.
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py createsuperuser`
5. Optional: `python manage.py seed_menu`
6. `python manage.py runserver`

## Production
Set environment variables:
- `DJANGO_SECRET_KEY` to a long random secret
- `DJANGO_DEBUG=0`
- `DJANGO_ALLOWED_HOSTS=yourusername.pythonanywhere.com`

Then:
- `python manage.py migrate`
- `python manage.py collectstatic --noinput`

In Django Admin:
1. Open **Portal Settings**.
2. Enter the public HTTPS URL, e.g. `https://yourusername.pythonanywhere.com`.
3. Save it as active.
4. Open **Table QR Codes** → Add a table (e.g. T01).
5. Save, then click **Download Poster**.
6. Print and place the poster on that table.

The QR encodes `/menu/?table=T01` using the configured production URL, so the counter receives service calls for the correct table.

## Important
Do not commit `.env`, secrets, or the virtual environment to source control.
