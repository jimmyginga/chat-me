from django.contrib import admin
from .models import Post, PostComment, PostLike, PostDislike,  PostCommentLike, PostCommentDislike

admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(PostLike)
admin.site.register(PostDislike)
admin.site.register(PostCommentLike)
admin.site.register(PostCommentDislike)
