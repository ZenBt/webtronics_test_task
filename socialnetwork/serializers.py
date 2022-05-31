from rest_framework import serializers

from .models import Post, Like, User


class UserSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True)
    
    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'],
                                        password=validated_data['password'])
        return user
    
    class Meta:
        model = User
        fields = ( "id", "username", "password", )


class PostSerializer(serializers.ModelSerializer):
    
    total_likes = serializers.IntegerField(read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True, default=serializers.CurrentUserDefault())
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author_name', 'total_likes', 'author',)


class LikeSerializer(serializers.ModelSerializer):
    
    author_name = serializers.CharField(source='author.username', read_only=True, default=serializers.CurrentUserDefault())
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_liked = serializers.BooleanField()
    
    class Meta:
        model = Like
        fields = ('id', 'post', 'author_name', 'is_liked', 'author')
