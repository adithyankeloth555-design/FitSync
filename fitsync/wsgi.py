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

# Auto-run migrations on Vercel startup (needed for serverless environments)
if os.environ.get('VERCEL'):
    try:
        from django.core.management import call_command
        # Run database migrations
        call_command('migrate', '--run-syncdb', verbosity=0)
        # Collect static files (WhiteNoise serves them)
        call_command('collectstatic', '--noinput', verbosity=0)
    except Exception as e:
        print(f"Startup warning: {e}")

application = get_wsgi_application()
app = application
