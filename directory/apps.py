from django.apps import AppConfig


class DirectoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'directory'
    verbose_name = 'الدليل'
    
    def ready(self):
        """تحميل الـ Signals عند بدء التطبيق"""
        import directory.signals  # ✅ استيراد الـ signals
