from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Event(models.Model):
    name = models.CharField(max_length=250)
    date = models.DateTimeField()
    location = models.CharField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "events"

class Guest(models.Model):
    country = models.CharField(max_length=100, null=True, blank=True)
    document_id = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "guests"

class FileUpload(models.Model):
    title = models.CharField(max_length=250)
    file = models.FileField(upload_to="uploads/", null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_processed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "file_upload"

class FileUploadGuest(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    fileupload = models.ForeignKey(FileUpload, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.guest.name} - {self.fileupload.title}"

    class Meta:
        db_table = "file_upload_guest"

class EventGuest(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.guest.name} - {self.event.name}"

    class Meta:
        db_table = "event_guest"

class Attendance(models.Model):
    event_guest = models.OneToOneField(EventGuest, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event_guest.guest.name} - {self.attended}"

    class Meta:
        db_table = "attendance"

class SendLog(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.action} - {self.type}"

    class Meta:
        db_table = "send_log"

class UserActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"

    class Meta:
        db_table = "user_action_log"