from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Michael Milne API",
        default_version='v1',
        description="Michael Milne API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="riyad.cse27@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
