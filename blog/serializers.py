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
    Simplified user serializer for comments to reduce payload size
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'profile_picture']

class CommentSerializer(serializers.ModelSerializer):
    author = CommentAuthorSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    article_title = serializers.CharField(source='article.title', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'content', 'created_at', 'parent', 
            'replies', 'like_count', 'is_liked', 'article_title'
        ]
        read_only_fields = ['created_at', 'author']
    
    def get_replies(self, obj):
        """
        Get nested replies with pagination for better performance
        """
        replies = Comment.objects.filter(parent=obj).order_by('-created_at')[:10]  # Limit to 10 replies
        serializer = CommentSerializer(replies, many=True, context=self.context)
        return serializer.data
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class ArticleListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for article listings
    """
    author = CommentAuthorSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'thumbnail', 'author',
            'created_at', 'views', 'like_count', 'comment_count',
            'categories'
        ]
    
    def get_comment_count(self, obj):
        return obj.comments.count()

class ArticleDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for individual article view
    """
    author = CommentAuthorSerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)
    content = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'thumbnail', 'content', 'author',
            'created_at', 'updated_at', 'views', 'comments', 
            'like_count', 'is_liked', 'categories'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'views']

    def get_comments(self, obj):
        """
        Get top-level comments only with pagination
        """
        comments = obj.comments.filter(parent__isnull=True).order_by('-created_at')[:50]
        serializer = CommentSerializer(comments, many=True, context=self.context)
        return serializer.data
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def get_content(self, obj):
        """
        Sanitize content or add markdown processing if needed
        """
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
        fields = [
            'title', 'content', 'thumbnail', 'categories'
        ]
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