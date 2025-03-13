from .models import Category, NavbarLink

def navbar_processor(request):
    return {
        'categories': Category.objects.all(),
        'navbar_links': NavbarLink.objects.all(),
    }