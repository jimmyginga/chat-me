from rest_framework.serializers import ModelSerializer

from .models import Post, PostComment, PostLike, PostDislike, PostCommentLike, PostCommentDislike


class PostSerializer(ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'

class PostCommentSerializer(ModelSerializer):

    class Meta:
        model = PostComment
        fields = '__all__'

class PostLikeSerializer(ModelSerializer):

    class Meta:
        model = PostLike
        fields = '__all__'

class PostDislikeSerializer(ModelSerializer):

    class Meta:
        model = PostDislike
        fields = '__all__'

class PostCommentLikeSerializer(ModelSerializer):

    class Meta:
        model = PostCommentLike
        fields = '__all__'

class PostCommentDislikeSerializer(ModelSerializer):

    class Meta:
        model = PostCommentDislike
        fields = '__all__'