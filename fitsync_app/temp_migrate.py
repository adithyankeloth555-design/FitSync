from django.core.management import call_command
from django.http import HttpResponse

def run_migrations_view(request):
    try:
        call_command('migrate', interactive=False)
        return HttpResponse("Migrations completed successfully.")
    except Exception as e:
        return HttpResponse(f"Error running migrations: {str(e)}")
