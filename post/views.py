from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Post, PostComment, PostLike, PostDislike, PostCommentLike, PostCommentDislike
from .serializers import PostSerializer, PostCommentSerializer, PostLikeSerializer, PostDislikeSerializer, PostCommentLikeSerializer, PostCommentDislikeSerializer


class PostViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    GenericViewSet
):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()


class PostCommentViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    GenericViewSet
):
    serializer_class = PostCommentSerializer
    permission_classes = [IsAuthenticated]
    queryset = PostComment.objects.all()


class PostLikeViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    GenericViewSet
):
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticated]
    queryset = PostLike.objects.all()


class PostDislikeViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    GenericViewSet
):
    serializer_class = PostDislikeSerializer
    permission_classes = [IsAuthenticated]
    queryset = PostDislike.objects.all()


class PostCommentLikeViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    GenericViewSet
):
    serializer_class = PostCommentLikeSerializer
    permission_classes = [IsAuthenticated]
    queryset = PostCommentLike.objects.all()


class PostCommentDislikeViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    GenericViewSet
):
    serializer_class = PostCommentDislikeSerializer
    permission_classes = [IsAuthenticated]
    queryset = PostCommentDislike.objects.all()
