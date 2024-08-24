from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Menu Items API",
      default_version='v1',
      description="API for managing menu items",
      terms_of_service="https://www.ernesttsamo.assesment.com/terms/",
      contact=openapi.Contact(email="ernestsamo16@gmail.com"),
      license=openapi.License(name="My Personal License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', RedirectView.as_view(url='/api/', permanent=True)),
    path('admin-assesment/', admin.site.urls),
    path('api/', include('menu_hierarchy.urls')), 
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]