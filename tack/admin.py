from django.contrib import admin

# Register your models here.
from tack.models import Users, TackImages
admin.site.register(Users)
admin.site.register(TackImages)