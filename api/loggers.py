import logging
from django.apps import apps  # Importa apps para obtener modelos dinámicamente

class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        try:
            UserActionLog = apps.get_model('api', 'UserActionLog')
            user = getattr(record, 'user', None)
            action = self.format(record)
            UserActionLog.objects.create(user=user, action=action)
        except Exception as e:
            logging.error(f"Error en DatabaseLogHandler.emit: {e}")
