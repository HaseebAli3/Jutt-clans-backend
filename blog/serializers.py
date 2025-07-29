from rest_framework import serializers
from .models import CustomUser, Article, Comment, Category
from django.contrib.auth.hashers import make_password

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'bio', 'profile_picture']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)

class CommentAuthorSerializer(serializers.ModelSerializer):
    """
    Simplified user serializer for comments
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'profile_picture']

class BaseCommentSerializer(serializers.ModelSerializer):
    """
    Base serializer for comment-related serializers to avoid code duplication
    """
    author = CommentAuthorSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at', 'like_count', 'is_liked']
        read_only_fields = ['created_at', 'author']

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class CommentSerializer(BaseCommentSerializer):
    """
    Serializer for comment display with nested replies
    """
    replies = serializers.SerializerMethodField()
    article_title = serializers.CharField(source='article.title', read_only=True)

    class Meta(BaseCommentSerializer.Meta):
        fields = BaseCommentSerializer.Meta.fields + ['parent', 'replies', 'article_title']

    def get_replies(self, obj):
        replies = Comment.objects.filter(parent=obj).order_by('-created_at')[:10]
        return CommentSerializer(replies, many=True, context=self.context).data

class ArticleBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for common article fields
    """
    author = CommentAuthorSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'author', 'categories', 'like_count', 'is_liked']

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class ArticleListSerializer(ArticleBaseSerializer):
    """
    Lightweight serializer for article listings
    """
    comment_count = serializers.SerializerMethodField()
    thumbnail = serializers.ImageField(read_only=True)
    excerpt = serializers.SerializerMethodField()

    class Meta(ArticleBaseSerializer.Meta):
        fields = ArticleBaseSerializer.Meta.fields + [
            'thumbnail', 'created_at', 'views', 'comment_count', 'excerpt'
        ]
        read_only_fields = ['slug', 'created_at', 'views']

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_excerpt(self, obj):
        return obj.content[:150] + '...' if len(obj.content) > 150 else obj.content

class ArticleDetailSerializer(ArticleBaseSerializer):
    """
    Detailed serializer for individual article view
    """
    comments = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    thumbnail = serializers.ImageField(read_only=True)

    class Meta(ArticleBaseSerializer.Meta):
        fields = ArticleBaseSerializer.Meta.fields + [
            'thumbnail', 'content', 'created_at', 'updated_at', 
            'views', 'comments'
        ]

    def get_comments(self, obj):
        comments = obj.comments.filter(parent__isnull=True).order_by('-created_at')[:50]
        return CommentSerializer(comments, many=True, context=self.context).data

    def get_content(self, obj):
        return obj.content

class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating articles
    """
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        required=False
    )

    class Meta:
        model = Article
        fields = ['title', 'content', 'thumbnail', 'categories']
        extra_kwargs = {
            'thumbnail': {'required': True}
        }

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        article = Article.objects.create(**validated_data)
        article.categories.set(categories)
        return article

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        instance = super().update(instance, validated_data)
        if categories is not None:
            instance.categories.set(categories)
        return instance