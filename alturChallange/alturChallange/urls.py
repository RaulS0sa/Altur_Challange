"""
URL configuration for alturChallange project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from alturChallange import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.upload_list, name="upload_list"),
    path("api/calls/", views.api_calls, name="api_calls"),
    path("api/calls/<uuid:call_id>/", views.api_call_detail, name="api_call_detail"),
    path("api/calls/<uuid:call_id>/export/",views.api_call_export,name="api_call_export",),
    path("analytics/", views.analytics_dashboard, name="analytics"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
