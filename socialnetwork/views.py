from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView, Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from django.db.models import Count, Q
from django.core.exceptions import BadRequest

from .models import Post, Like, User
from .serializers import UserSerializer, PostSerializer, LikeSerializer
from .custom_permissions import IsAuthorOrAdmin


class CreateUserView(CreateAPIView):
    model = User
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    
    def get_queryset(self):
        return Post.objects.annotate(total_likes=Count('like__post', filter=Q(like__is_liked=True)))


class LikeAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAuthorOrAdmin)
    serializer_class = LikeSerializer

    def get_like_obj(self, post_id, author_id):
        try:
            obj = Like.objects.get(Q(post=post_id) & Q(author=author_id))
        except Like.DoesNotExist:
            raise BadRequest('You have never liked this post')
        return obj

    def post(self, request, post_id):
        if len(Like.objects.filter(Q(post=post_id) & Q(author=request.user.id)).all()) != 0:
            raise BadRequest('You have already liked this post')
        request.data._mutable=True
        request.data.update({'post':post_id})
        serializer = LikeSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'like': serializer.data})
    
    def put(self, request, post_id):
        
        request.data._mutable=True
        request.data.update({'post':post_id})
        serializer = LikeSerializer(self.get_like_obj(post_id, request.user.id), context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
            
        serializer.save()
        
        return Response({'like': serializer.data})





class CommentAPIView(APIView):
    permission_classes = (IsAuthenticated)
    serializer_class = LikeSerializer

    def post(self, request, post_id):
        request.data._mutable=True
        request.data.update({'post':post_id})
        serializer = LikeSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'like': serializer.data})
    
    def put(self, request, post_id):
        request.data._mutable=True
        request.data.update({'post':post_id})
        serializer = LikeSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'like': serializer.data})