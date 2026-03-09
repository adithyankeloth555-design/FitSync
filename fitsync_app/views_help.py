from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HelpTicket

@login_required
def admin_help_tickets_view(request):
    if request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied. Administrative privileges required.")
        return redirect('help')
    
    # Handle ticket response
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        admin_response = request.POST.get('admin_response')
        
        ticket = get_object_or_404(HelpTicket, id=ticket_id)
        ticket.admin_response = admin_response
        ticket.is_resolved = True
        ticket.save()
        
        messages.success(request, f"Response sent to {ticket.user.username}'s ticket.")
        return redirect('admin_help_tickets')
    
    # Get all tickets, ordered by status (unresolved first)
    all_tickets = HelpTicket.objects.all().order_by('is_resolved', '-created_at')
    pending_tickets = HelpTicket.objects.filter(is_resolved=False)
    resolved_tickets = HelpTicket.objects.filter(is_resolved=True)
    
    return render(request, 'fitsync_app/admin_help_tickets.html', {
        'all_tickets': all_tickets,
        'pending_tickets': pending_tickets,
        'resolved_tickets': resolved_tickets,
    })
