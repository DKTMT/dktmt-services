from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    post = models.ForeignKey(Post, related_name="likes", on_delete=models.CASCADE)
    user = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    post = models.ForeignKey(Post, related_name="reviews", on_delete=models.CASCADE)
    user = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
