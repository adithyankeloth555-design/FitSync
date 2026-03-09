"""
WSGI config for fitsync project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import pymysql

pymysql.install_as_MySQLdb()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitsync.settings')

from django.core.wsgi import get_wsgi_application

# Auto-run migrations on every startup when on Vercel (SQLite /tmp or Postgres)
if os.environ.get('VERCEL'):
    try:
        from django.core.management import call_command
        call_command('migrate', verbosity=0)
    except Exception as e:
        print(f"Migration warning: {e}")

application = get_wsgi_application()
app = application
