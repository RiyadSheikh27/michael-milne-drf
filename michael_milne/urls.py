from django.contrib import admin
from django.urls import path, include
from utils.swagger import schema_view  # your existing schema_view
from drf_yasg.renderers import OpenAPIRenderer, SwaggerUIRenderer, ReDocRenderer



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/user/', include('authentication.urls')),
    path('api/v1/', include('property.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
