from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("api/emissions/", include("emissions.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/assistant/", include("assistant.urls")),
    path("api/accounts/", include("accounts.urls")),
]
