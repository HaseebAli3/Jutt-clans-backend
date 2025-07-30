# views.py
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from .models import Article, Category, Comment, CustomUser
from .serializers import (
    ArticleSerializer, CommentSerializer, CategorySerializer, UserSerializer
)
from rest_framework.authentication import TokenAuthentication

# User registration
class UserCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

# User login
class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = CustomUser.objects.filter(username=username).first()
        if user and user.check_password(password):
            return Response({'user': UserSerializer(user).data})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

# Update user profile
class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# Category list
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Article CRUD
class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        category_id = self.request.query_params.get('category')
        if category_id:
            return Article.objects.filter(category_id=category_id).order_by('-created_at')
        return Article.objects.all().order_by('-created_at')

class ArticleSearchView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Article.objects.filter(Q(title__icontains=query)).order_by('-created_at')

class ArticleDetailView(APIView):
    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        article.increment_views()
        serializer = ArticleSerializer(article, context={"request": request})
        return Response(serializer.data)

class ArticleCreateView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        author = self.request.user
        if not author.is_staff:
            author = CustomUser.objects.filter(is_staff=True).first()
        serializer.save(author=author)

class ArticleUpdateView(generics.UpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

class ArticleDeleteView(generics.DestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

class LikeArticleView(APIView):
    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        user = request.user
        if user.is_authenticated:
            if article.likes.filter(id=user.id).exists():
                article.likes.remove(user)
            else:
                article.likes.add(user)
        return Response({'like_count': article.likes.count()})

# Comment CRUD
class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        article_id = self.kwargs['pk']
        return Comment.objects.filter(article_id=article_id, parent__isnull=True).order_by('-created_at')

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        article = get_object_or_404(Article, pk=self.kwargs['pk'])
        parent_id = self.request.data.get('parent')
        parent = get_object_or_404(Comment, id=parent_id) if parent_id else None

        # Prevent duplicate comments on the same parent
        if parent and Comment.objects.filter(author=self.request.user, parent=parent).exists():
            raise serializer.ValidationError("You can comment only once on a reply.")

        serializer.save(author=self.request.user, article=article, parent=parent)

class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

class CommentUpdateView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

class LikeCommentView(APIView):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, id=pk)
        user = request.user
        if user.is_authenticated:
            if comment.likes.filter(id=user.id).exists():
                comment.likes.remove(user)
            else:
                comment.likes.add(user)
        return Response({'like_count': comment.likes.count()})