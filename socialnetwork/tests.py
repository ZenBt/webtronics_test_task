from collections import OrderedDict
from django.urls import resolve, reverse
from django.test import SimpleTestCase
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from .views import CreateUserView, LikeAPIView
from .models import User, Post, Like
from .serializers import PostSerializer, UserSerializer, LikeSerializer


class TestUrls(SimpleTestCase):
    
    def test_token_obtain_url_resolves(self):
        url = reverse('token_obtain_pair')
        self.assertEqual(resolve(url).func.view_class, TokenObtainPairView)
    
    def test_token_refresh_url_resolves(self):
        url = reverse('token_refresh')
        self.assertEqual(resolve(url).func.view_class, TokenRefreshView)
    
    def test_token_verify_url_resolves(self):
        url = reverse('token_verify')
        self.assertEqual(resolve(url).func.view_class, TokenVerifyView)
    
    def test_create_user_url_resolves(self):
        url = reverse('singup')
        self.assertEqual(resolve(url).func.view_class, CreateUserView)
    
    def test_like_url_resolves(self):
        url = reverse('like', kwargs={'post_id': 1})
        self.assertEqual(resolve(url).func.view_class, LikeAPIView)


class TestCreateUserAPIView(APITestCase):
    def test_create_user(self):
        url = reverse('singup')
        self.assertEqual(len(User.objects.all()), 0)
        response = self.client.post(url, data={'username':'User1', 'password':'storngpwd'})
        self.assertEqual(len(User.objects.all()), 1)
        self.assertEqual('User1', response.data['username'])


class TestPostViewSet(APITestCase):
    
    def setUp(self):
        self.author_1 = User.objects.create_user(username='User1', password='storngpwd')
        self.admin_1 = User.objects.create_superuser(username='admin', email='test@gmail.com', password='morestrongpwd123')
        self.post_1 = Post.objects.create(title='Test1', content='somecontent1', author=self.author_1)
    
    def test_get_all_post(self):
        url = reverse('post-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        expected_data = [OrderedDict([('id', self.post_1.id), ('title', 'Test1'), ('content', 'somecontent1'), ('author_name', 'User1'), ('total_likes', 0)])]
        self.assertEqual(expected_data, response.data)

    
    def test_get_post_detail(self):
        url = reverse('post-detail', kwargs={'pk': self.post_1.id})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        expected_data = {'id': self.post_1.id, 'title': 'Test1', 'content': 'somecontent1', 'author_name': 'User1', 'total_likes': 0}
        self.assertEqual(expected_data, response.data)

    def test_post_fail_without_auth(self):
        url = reverse('post-list')
        response = self.client.post(url, data={'title':'Test2', 'content':'somecontent2'})
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_post_ok_with_token_auth(self):
        url_auth = reverse('token_obtain_pair')
        
        token = self.client.post(url_auth, data={'username':self.author_1.username,
                                                 'password': 'storngpwd'}).data['access']
        url = reverse('post-list')
        self.assertEqual(len(Post.objects.all()), 1)
        data = {'title':'Test2', 'content':'somecontent2'}
        response = self.client.post(url, data=data, HTTP_AUTHORIZATION='Bearer '+token)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(len(Post.objects.all()), 2)
        expected_data = {'id': Post.objects.last().id, 'title': 'Test2', 'content': 'somecontent2', 'author_name': 'User1'}
        self.assertEqual(expected_data, response.data)
    

class TestLikeAPIViewWithoutAuth(APITestCase):
    
    def setUp(self):
        self.author_1 = User.objects.create_user(username='User1', password='storngpwd')
        self.post_1 = Post.objects.create(title='Test1', content='somecontent1', author=self.author_1)
        self.url = reverse('like', kwargs={'post_id': self.post_1.id})
    
    def test_get_not_authorized(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
    
    def test_post_not_authorized(self):
        response = self.client.get(self.url, {'is_liked': True})
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
    
    def test_put_not_authorized(self):
        response = self.client.put(self.url, data={'is_liked': False})
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)


class TestLikeAPIView(APITestCase):
    
    def setUp(self):
        self.author_1 = User.objects.create_user(username='User1', password='storngpwd')
        self.admin_1 = User.objects.create_superuser(username='admin', email='test@gmail.com', password='morestrongpwd123')
        self.post_1 = Post.objects.create(title='Test1', content='somecontent1', author=self.author_1)
        url_auth = reverse('token_obtain_pair')
        
        self.token = self.client.post(url_auth, data={'username':self.author_1.username,
                                                 'password': 'storngpwd'}).data['access']
        self.token_2 = self.client.post(url_auth, data={'username':self.admin_1.username,
                                                 'password': 'morestrongpwd123'}).data['access']

    def test_put_before_post(self):
        url = reverse('like', kwargs={'post_id': self.post_1.id})
        response = self.client.put(url, data={'is_liked': False}, HTTP_AUTHORIZATION='Bearer '+ self.token)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
    
    def test_post_after_post(self):
        url = reverse('like', kwargs={'post_id': self.post_1.id})
        self.client.post(url, data={'is_liked': False}, HTTP_AUTHORIZATION='Bearer '+ self.token)
        response = self.client.post(url, data={'is_liked': True}, HTTP_AUTHORIZATION='Bearer '+ self.token)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
    
    def test_post(self):
        url = reverse('like', kwargs={'post_id': self.post_1.id})
        response = self.client.post(url, data={'is_liked': True}, HTTP_AUTHORIZATION='Bearer '+ self.token)
        self.assertEqual(status.HTTP_200_OK, response.status_code)    
        expected_data = {'like': {'id': Like.objects.last().id, 'post': self.post_1.id, 'author_name': 'User1', 'is_liked': True}}
        self.assertEqual(expected_data, response.data)
        
    def test_put_ok(self):
        url = reverse('like', kwargs={'post_id': self.post_1.id})
        response = self.client.post(url, data={'is_liked': True}, HTTP_AUTHORIZATION='Bearer '+ self.token)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        response = self.client.put(url, data={'is_liked': False}, HTTP_AUTHORIZATION='Bearer '+ self.token)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['like']['is_liked'], False)
        
    def test_like_counter(self):
        url_post = reverse('post-detail', kwargs={'pk': self.post_1.id})
        response_1 = self.client.get(url_post).data
        self.assertEqual(response_1['total_likes'], 0)
        url = reverse('like', kwargs={'post_id': self.post_1.id})
        response = self.client.post(url, data={'is_liked': True}, HTTP_AUTHORIZATION='Bearer '+ self.token)
        response_1 = self.client.get(url_post).data
        self.assertEqual(response_1['total_likes'], 1)
        response = self.client.post(url, data={'is_liked': True}, HTTP_AUTHORIZATION='Bearer '+ self.token_2)
        response_1 = self.client.get(url_post).data
        self.assertEqual(response_1['total_likes'], 2)
        response = self.client.put(url, data={'is_liked': False}, HTTP_AUTHORIZATION='Bearer '+ self.token_2)
        response = self.client.put(url, data={'is_liked': False}, HTTP_AUTHORIZATION='Bearer '+ self.token)
        response_1 = self.client.get(url_post).data
        self.assertEqual(response_1['total_likes'], 0)
