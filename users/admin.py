from django.contrib import admin
from .models import User
# Register your models here.
class Useradmin(admin.ModelAdmin):
    list_display =['email', 'role', 'company_id']
    class Meta:
        model = User

admin.site.register(User,Useradmin)