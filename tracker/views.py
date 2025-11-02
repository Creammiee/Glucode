from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import GlucoseRecord

@login_required
def dashboard(request):
    # Only admin can view all users
    if request.user.is_superuser:
        users = User.objects.all()
        records = GlucoseRecord.objects.all().order_by('-recorded_at')
        return render(request, 'users/admin_dashboard.html', {
            'users': users,
            'records': records
        })
    else:
        # Normal users can only see their own records
        records = GlucoseRecord.objects.filter(user=request.user).order_by('-recorded_at')
        return render(request, 'users/user_dashboard.html', {
            'records': records
        })
