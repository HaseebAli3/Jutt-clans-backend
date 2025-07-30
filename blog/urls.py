from django.urls import path
from .views import (
    UserCreateView, UserLoginView, UserUpdateView,
    ArticleListView, ArticleDetailView, ArticleCreateView, ArticleUpdateView, ArticleDeleteView,
    ArticleSearchView, LikeArticleView,
    CommentListView, CommentCreateView, CommentDeleteView, CommentUpdateView, LikeCommentView,
    CategoryListView
)

urlpatterns = [
    path('auth/register/', UserCreateView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/update/', UserUpdateView.as_view(), name='update-user'),

    path('categories/', CategoryListView.as_view(), name='category-list'),

    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/search/', ArticleSearchView.as_view(), name='article-search'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('articles/create/', ArticleCreateView.as_view(), name='article-create'),
    path('articles/<int:pk>/update/', ArticleUpdateView.as_view(), name='article-update'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article-delete'),
    path('articles/<int:pk>/like/', LikeArticleView.as_view(), name='like-article'),

    path('articles/<int:pk>/comments/', CommentListView.as_view(), name='comment-list'),
    path('articles/<int:pk>/comments/create/', CommentCreateView.as_view(), name='comment-create'),
    path('comments/<int:pk>/update/', CommentUpdateView.as_view(), name='comment-update'),
    path('comments/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
    path('comments/<int:pk>/like/', LikeCommentView.as_view(), name='like-comment'),
]
