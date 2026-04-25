import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ewaste_backend.settings')

application = get_wsgi_application()

# Auto-create superuser on every boot (safe — skips if already exists)
try:
    from django.core.management import call_command
    call_command("migrate", "--run-syncdb", verbosity=0)
    call_command("initadmin", verbosity=0)
except Exception as e:
    import sys
    print(f"[wsgi] initadmin error: {e}", file=sys.stderr)
