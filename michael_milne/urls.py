from django.contrib import admin
from django.urls import path, include
from utils.swagger import schema_view 
from drf_yasg.renderers import OpenAPIRenderer, SwaggerUIRenderer, ReDocRenderer
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/user/', include('authentication.urls')),
    path('api/v1/', include('property.urls')),
    path('api/v1/payments/', include('payments.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )