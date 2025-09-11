from django.contrib import admin
from .models import UserActionLog, Events, Guests, FileUpload, FileUploadGuest, AttendanceLog, SendLog

admin.site.register(UserActionLog)
admin.site.register(Events)
admin.site.register(Guests)
admin.site.register(FileUpload)
admin.site.register(FileUploadGuest)
admin.site.register(AttendanceLog)
admin.site.register(SendLog)