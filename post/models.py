from django.db import models
from authentication.models import User


class Post(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts_created')


class PostComment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments_created')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='post_comments')
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments_tagged')


class PostLike(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='liked_posts')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='post_likes')


class PostDislike(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='disliked_posts')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='post_dislikes')


class PostCommentLike(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='liked_posts_comments')
    comment = models.ForeignKey(
        PostComment, on_delete=models.CASCADE, related_name='post_comment_likes')


class PostCommentDislike(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='disliked_posts_comments')
    comment = models.ForeignKey(
        PostComment, on_delete=models.CASCADE, related_name='post_comment_dislikes')
