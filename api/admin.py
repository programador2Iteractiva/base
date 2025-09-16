import logging
from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html
from django.conf import settings
import openpyxl
import os
import qrcode
from PIL import Image
from datetime import datetime
import requests # Import requests

from .models import UserActionLog, Event, Guest, FileUpload, FileUploadGuest, Attendance, SendLog, EventGuest

# Asegúrese de que la carpeta de QR exista
QR_DIR = os.path.join(settings.MEDIA_ROOT, 'qr')
if not os.path.exists(QR_DIR):
    os.makedirs(QR_DIR)

# API URL for sending emails
EMAIL_API_URL = "https://box365.com.co/api/emails"
# IMPORTANT: Replace with your actual site's domain.
SITE_BASE_URL = "https://admin.registro-eventos.interactiva.com.co" 

def send_email(guest_email, guest_name, event_name, qr_url):
    """
    Sends an email with the QR code image to a guest.
    """
    subject = f"Invitación para el evento: {event_name}"
    body = f"""
    <div style="font-family: Arial, sans-serif; text-align: center;">
        <h1 style="color: #333;">¡Hola {guest_name}!</h1>
        <p style="font-size: 16px;">Aquí está tu código QR para ingresar al evento **{event_name}**.</p>
        <p style="font-size: 16px;">Por favor, presenta este código en la entrada.</p>
        <img src="{qr_url}" alt="Código QR de Invitación" style="width: 250px; height: 250px; border: 1px solid #ddd; border-radius: 8px;">
        <p style="font-size: 12px; color: #888;">Si no puedes ver la imagen, haz clic derecho y selecciona "Descargar imagen".</p>
    </div>
    """

    payload = {
        "campaign_id": 26, # You may need to change this
      "name": "Novo Nordisk COL",
        "from": "novonordiskcol@send.box365.com.co",
        "reply_to": "dcardenas@interactiva.net.co",
        "to": guest_email,
        "subject": subject,
        "body": body
    }
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(EMAIL_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            return True, f"Email enviado a {guest_email} con éxito."
        else:
            return False, f"Error al enviar email a {guest_email}: {response.text} - {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Error de conexión al enviar email: {e}"


class FileUploadAdmin(admin.ModelAdmin):
    list_display = ("title", "event", "is_processed", "is_active", "created")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.is_processed = False
            super().save_model(request, obj, form, change)

            if obj.file:
                try:
                    # Cargar el archivo .xlsx
                    workbook = openpyxl.load_workbook(obj.file.path)
                    sheet = workbook.active
                    
                    guest_count = 0

                    # Iterar sobre las filas, omitiendo el encabezado
                    for row in sheet.iter_rows(min_row=2, values_only=True):
                        # Asignar valores de las columnas

                        if row[3] is None or row[2] is None:
                            continue

                        guest_name = row[0] if row[0] is not None else "Nombre no especificado"
                        country = row[1] if len(row) > 1 and row[1] is not None else ""
                        document_id = row[2] if len(row) > 2 and row[2] is not None else ""
                        email = row[3] if len(row) > 3 and row[3] is not None else ""
                        phone = row[4] if len(row) > 4 and row[4] is not None else ""

                        guest_count += 1
                        
                        # Crear el objeto Guests
                        guest, created = Guest.objects.get_or_create(
                            email=email,
                            defaults={'name': guest_name, 'country': country, 'document_id': document_id, 'phone': phone}
                        )

                        # Crear la relación EventGuest
                        EventGuest.objects.get_or_create(
                            event=obj.event,
                            guest=guest,
                        )

                        # Crear la relación FileUploadGuest
                        FileUploadGuest.objects.create(
                            guest=guest,
                            fileupload=obj
                        )
                    
                    # Marcar el archivo como procesado
                    obj.is_processed = True
                    obj.save()

                    UserActionLog.objects.create(
                        user=request.user,
                        action = f"Cargue archivo {obj.title} con {guest_count} invitados"
                    )
                    
                except Exception as e:
                    obj.is_processed = False
                    obj.save()
                    self.message_user(request, f"Error al procesar el archivo: {obj.title} {e}", level="ERROR")
                    
                    UserActionLog.objects.create(
                        user=request.user,
                        action = f"Error al procesar el archivo de cargue: {e}"
                    )
                
                finally:
                    # Eliminar el archivo físico después de procesar
                    if os.path.exists(obj.file.path):
                        os.remove(obj.file.path)
                    obj.file.delete(save=False)
        else:
            super().save_model(request, obj, form, change)


class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "location", "is_active", "created")
    actions = ["send_invitations"]

    @admin.action(description="Enviar invitaciones (generar QR para los invitados)")
    def send_invitations(self, request, queryset):
        total_qrs_generated = 0
        total_emails_sent = 0
        errors = []

        try:
            for event in queryset:
                guests = EventGuest.objects.filter(event=event).select_related('guest')
                for event_guest in guests:
                    guest = event_guest.guest
                    qr_data = f"{str(guest.document_id)}#{str(event.id)}"
                    qr_img = qrcode.make(qr_data)
                    
                    filename = f"{event.id}_{guest.document_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                    filepath = os.path.join(QR_DIR, filename)
                    qr_img.save(filepath)
                    
                    qr_url = f"{SITE_BASE_URL}{settings.MEDIA_URL}qr/{filename}"
                    
                    success, message = send_email(guest.email, guest.name, event.name, qr_url)
                    if success:
                        total_emails_sent += 1
                        total_qrs_generated += 1
                    else:
                        errors.append(message)
                        UserActionLog.objects.create(user=request.user, action=message)

            if total_emails_sent > 0:
                self.message_user(request, f"Se generaron y enviaron {total_qrs_generated} invitaciones exitosamente.", level="SUCCESS")
                UserActionLog.objects.create(
                    user=request.user,
                    action=f"Se generaron y enviaron {total_qrs_generated} invitaciones exitosamente."
                )
            if errors:
                for err in errors:
                    self.message_user(request, err, level="ERROR")

        except Exception as e:
            self.message_user(request, f"Error al enviar invitaciones: {e}", level="ERROR")
            UserActionLog.objects.create(
                user=request.user,
                action=f"Error al enviar invitaciones: {e}"
            )


admin.site.register(UserActionLog)
admin.site.register(Event, EventAdmin)
admin.site.register(Guest)
admin.site.register(FileUpload, FileUploadAdmin)
admin.site.register(FileUploadGuest)
admin.site.register(EventGuest)
admin.site.register(Attendance)
admin.site.register(SendLog)