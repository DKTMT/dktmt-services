from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Like, Review
from .serializers import PostSerializer, LikeSerializer, ReviewSerializer

class PostList(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        author = request.user_data["name"]
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Print the request data and serializer errors for debugging
        print("Request data:", request.data)
        print("Serializer errors:", serializer.errors)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    def get_post(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        post = self.get_post(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk):
        post = self.get_post(pk)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_post(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LikeList(APIView):
    def post(self, request, post_id):
        author = request.user_data["name"]
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        like = Like(post=post, user=author)
        like.save()
        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReviewList(APIView):
    def post(self, request, post_id):
        author = request.user_data["name"]
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Add this print statement
        print("Request data:", request.data)
        
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, user=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Add this print statement
        print("Serializer errors:", serializer.errors)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetail(APIView):
    def get_review(self, pk):
        try:
            return Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        review = self.get_review(pk)
        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        review = self.get_review(pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
