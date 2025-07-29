from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Article, Comment, CustomUser, Category
from .serializers import (
    ArticleSerializer, ArticleListSerializer, ArticleDetailSerializer,
    CommentSerializer, UserSerializer, CategorySerializer
)
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = CustomUser.objects.filter(username=username).first()
        
        if user and user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_400_BAD_REQUEST
        )

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination

class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Article.objects.all()
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)
        return queryset.order_by('-created_at')

class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        article = self.get_object()
        article.increment_views()
        serializer = self.get_serializer(article, context={'request': request})
        return Response(serializer.data)

class ArticleCreateView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ArticleUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        article_slug = self.kwargs['slug']
        return Comment.objects.filter(
            article__slug=article_slug,
            parent__isnull=True
        ).order_by('-created_at')

class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        article = get_object_or_404(Article, slug=self.kwargs['slug'])
        parent_id = self.request.data.get('parent')
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id)
        serializer.save(
            author=self.request.user,
            article=article,
            parent=parent
        )

class LikeArticleView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        user = request.user
        liked = False

        if article.likes.filter(id=user.id).exists():
            article.likes.remove(user)
        else:
            article.likes.add(user)
            liked = True

        return Response({
            'liked': liked,
            'like_count': article.likes.count()
        })

class LikeCommentView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        comment = get_object_or_404(Comment, id=pk)
        user = request.user
        liked = False

        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
        else:
            comment.likes.add(user)
            liked = True

        return Response({
            'liked': liked,
            'like_count': comment.likes.count()
        })

class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)