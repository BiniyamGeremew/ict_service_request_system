from users.models import Notification

def notifications_processor(request):
    user_group = None
    if request.user.is_authenticated:
        groups = request.user.groups.values_list('name', flat=True)
        if groups.exists():
            user_group = groups[0]  # assuming 1 group per user

    if user_group:
        # First, get all notifications for the group
        all_notifications = Notification.objects.filter(target_group=user_group).order_by('-created_at')
        # Count unread before slicing
        unread_count = all_notifications.filter(is_read=False).count()
        # Then slice for display
        notifications = all_notifications[:5]
    else:
        notifications = Notification.objects.none()
        unread_count = 0

    return {
        'notifications': notifications,
        'unread_count': unread_count,
    }
