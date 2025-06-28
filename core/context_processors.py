from . import models

def system_settings(request):
    """Context processor for system setting"""
    settings = models.SystemSetting.objects.first()
    return {"settings": settings}
