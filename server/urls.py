"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from rest_framework import permissions, routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from chat.views import ChatViewSet
from meeting.views import MeetingViewSet, RatingViewSet
from network.views import NetworkViewSet
from post.views import PostViewSet, PostCommentViewSet, PostLikeViewSet, PostDislikeViewSet, PostCommentLikeViewSet, PostCommentDislikeViewSet
from recording.views import RecordingViewSet, RecordingCommentViewSet, FavoriteViewSet, RecordingLikeViewSet, RecordingDislikeViewSet, RecordingCommentLikeViewSet, RecordingCommentDislikeViewSet
from schedule.views import ScheduleViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r'chats', ChatViewSet, basename="chat")
router.register(r'meetings', MeetingViewSet, basename="meeting")
router.register(r'ratings', RatingViewSet, basename="rating")
router.register(r'networks', NetworkViewSet, basename="network")
router.register(r'posts', PostViewSet, basename="post")
router.register(r'postcomments', PostCommentViewSet, basename="postcomment")
router.register(r'postlikes', PostLikeViewSet, basename="postlike")
router.register(r'postdislikes', PostDislikeViewSet, basename="postdislike")
router.register(r'postcommentlikes', PostCommentLikeViewSet, basename="postcommentlike")
router.register(r'postcommentdislikes', PostCommentDislikeViewSet, basename="postcommentdislike")
router.register(r'recordings', RecordingViewSet, basename="recording")
router.register(r'recordingcomments', RecordingCommentViewSet, basename="recordingcomment")
router.register(r'favorites', FavoriteViewSet, basename="favorite")
router.register(r'recordinglikes', RecordingLikeViewSet, basename="recordinglike")
router.register(r'recordingdislikes', RecordingDislikeViewSet, basename="recordingdislike")
router.register(r'recordingcommentlikes', RecordingCommentLikeViewSet, basename="recordingcommentlike")
router.register(r'recordingcommentdislikes', RecordingCommentDislikeViewSet, basename="recordingcommentdislike")
router.register(r'schedules', ScheduleViewSet, basename="schedule")


urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0),
         name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
    path('api/auth/', include('authentication.urls')),
    path('api/', include(router.urls)),
    path("admin/", admin.site.urls),
]
