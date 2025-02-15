from django.contrib import admin
from django.urls import path
from detection import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.detect_page, name='detect'),
    path('history/', views.history_page, name='history'),
    path('analytics/', views.analytics_page, name='analytics'),
    path('process-image/', views.process_image, name='process_image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 