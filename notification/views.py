from django.shortcuts import render

# Create your views here.
def notification_page(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'customer/notifications.html', {
        'notifications': notifications
    })