from django.contrib import admin
from core import models
# Register your models here.


admin.site.register(models.User)
admin.site.register(models.Property)
admin.site.register(models.TenantProfile)
admin.site.register(models.Unit)
admin.site.register(models.RentPayment)