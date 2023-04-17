from django.urls import path
from .views import PostList, PostDetail, LikeList, ReviewList, ReviewDetail

urlpatterns = [
    path('posts/', PostList.as_view()),
    path('posts/<int:pk>/', PostDetail.as_view()),
    path('posts/<int:post_id>/like/', LikeList.as_view()),
    path('posts/<int:post_id>/reviews/', ReviewList.as_view()),
    path('reviews/<int:pk>/', ReviewDetail.as_view()),
]
