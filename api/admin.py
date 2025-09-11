from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
import openpyxl
import os
from .models import UserActionLog, Event, Guest, FileUpload, FileUploadGuest, Attendance, SendLog, EventGuest

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
                        
                        # Crear el objeto Guest
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


admin.site.register(UserActionLog)
admin.site.register(Event)
admin.site.register(Guest)
admin.site.register(FileUpload, FileUploadAdmin)
admin.site.register(FileUploadGuest)
admin.site.register(EventGuest)
admin.site.register(Attendance)
admin.site.register(SendLog)