
from django.shortcuts import render
from accounts.middleware import role_required

@role_required(['manager', 'admin'])
def index(request):
    return render(request, 'shop/index.html')