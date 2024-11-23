from .models import TopBarText  # Feltételezve, hogy van egy modell

def topbar_texts(request):
    return {
        'topbar_texts': TopBarText.objects.all()
    }
