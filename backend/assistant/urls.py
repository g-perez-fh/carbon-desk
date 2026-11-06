from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register("conversations", views.ConversationViewSet)
router.register("summaries", views.MonthlySummaryViewSet)

urlpatterns = [
    path("recommendations/", views.RecommendationsView.as_view(), name="recommendations"),
    *router.urls,
]
