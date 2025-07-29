from django.urls import path
from .views import (
    # User Authentication Views
    UserCreateView, UserLoginView,
    
    # Article Views
    ArticleListView, ArticleDetailView, ArticleCreateView, 
    ArticleUpdateDeleteView, ArticleByCategoryView,
    
    # Comment Views
    CommentCreateView, CommentDeleteView, CommentListView,
    
    # Like Views
    LikeArticleView, LikeCommentView,
    
    # Category Views
    CategoryListView, CategoryDetailView
)

urlpatterns = [
    # Authentication Endpoints
    path('auth/register/', UserCreateView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    
    # Article Endpoints
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/create/', ArticleCreateView.as_view(), name='article-create'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article-detail'),
    path('articles/<slug:slug>/update/', ArticleUpdateDeleteView.as_view(), name='article-update'),
    path('articles/<slug:slug>/delete/', ArticleUpdateDeleteView.as_view(), name='article-delete'),
    
    # Category Endpoints
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<slug:slug>/articles/', ArticleByCategoryView.as_view(), name='articles-by-category'),
    
    # Comment Endpoints
    path('articles/<slug:slug>/comments/', CommentListView.as_view(), name='comment-list'),
    path('articles/<slug:slug>/comments/create/', CommentCreateView.as_view(), name='comment-create'),
    path('comments/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
    
    # Like Endpoints
    path('articles/<slug:slug>/like/', LikeArticleView.as_view(), name='article-like'),
    path('comments/<int:pk>/like/', LikeCommentView.as_view(), name='comment-like'),
]