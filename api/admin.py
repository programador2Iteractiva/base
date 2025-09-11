from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.conf import settings
import openpyxl
import os
import qrcode
from PIL import Image
from datetime import datetime
from .models import UserActionLog, Event, Guest, FileUpload, FileUploadGuest, Attendance, SendLog, EventGuest

# Asegúrese de que la carpeta de QR exista
QR_DIR = os.path.join(settings.MEDIA_ROOT, 'qr')
if not os.path.exists(QR_DIR):
    os.makedirs(QR_DIR)

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
                    
                    # Iterar sobre las filas, omitiendo el encabezado
                    for row in sheet.iter_rows(min_row=2, values_only=True):
                        # Asignar valores de las columnas
                        guest_name = row[0] if row[0] is not None else "Nombre no especificado"
                        country = row[1] if len(row) > 1 and row[1] is not None else ""
                        document_id = row[2] if len(row) > 2 and row[2] is not None else ""
                        email = row[3] if len(row) > 3 and row[3] is not None else ""
                        phone = row[4] if len(row) > 4 and row[4] is not None else ""
                        
                        # Crear el objeto Guests
                        guest, created = Guests.objects.get_or_create(
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
                    
                except Exception as e:
                    obj.is_processed = False
                    obj.save()
                    self.message_user(request, f"Error al procesar el archivo: {e}", level="ERROR")
                
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
        for event in queryset:
            guests = EventGuest.objects.filter(event=event).select_related('guest')
            for event_guest in guests:
                guest = event_guest.guest
                # Contenido del QR: el ID del invitado
                qr_data = str(guest.document_id)
                qr_img = qrcode.make(qr_data)
                
                # Nombre del archivo QR
                filename = f"{event.id}_{guest.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                filepath = os.path.join(QR_DIR, filename)

                # Guardar el QR en la carpeta media/qr
                qr_img.save(filepath)
                total_qrs_generated += 1
        
        self.message_user(request, f"{total_qrs_generated} códigos QR generados exitosamente.")
        
admin.site.register(UserActionLog)
admin.site.register(Event, EventAdmin)
admin.site.register(Guest)
admin.site.register(FileUpload, FileUploadAdmin)
admin.site.register(FileUploadGuest)
admin.site.register(EventGuest)
admin.site.register(Attendance)
admin.site.register(SendLog)