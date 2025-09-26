
from django.db import models
from django.contrib.auth.models import User

class App(models.Model):
	name = models.CharField(max_length=255)
	category = models.CharField(max_length=100, blank=True, null=True)
	rating = models.FloatField(blank=True, null=True)
	reviews_count = models.CharField(max_length=20, blank=True, null=True)
	size = models.CharField(max_length=50, blank=True, null=True)
	installs = models.CharField(max_length=50, blank=True, null=True)
	type = models.CharField(max_length=10, blank=True, null=True)
	price = models.CharField(max_length=20, blank=True, null=True)
	content_rating = models.CharField(max_length=50, blank=True, null=True)
	genres = models.CharField(max_length=100, blank=True, null=True)
	last_updated = models.CharField(max_length=50, blank=True, null=True)
	current_ver = models.CharField(max_length=50, blank=True, null=True)
	android_ver = models.CharField(max_length=50, blank=True, null=True)

	def __str__(self):
		return self.name

class Review(models.Model):
	app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='reviews')
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	text = models.TextField()
	sentiment = models.CharField(max_length=20, blank=True, null=True)
	sentiment_polarity = models.FloatField(blank=True, null=True)
	sentiment_subjectivity = models.FloatField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	approved = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.app.name} - {self.text[:30]}"

class ReviewApproval(models.Model):
	review = models.OneToOneField(Review, on_delete=models.CASCADE)
	supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approvals')
	approved = models.BooleanField(default=False)
	reviewed_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Approval for {self.review}"

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	is_supervisor = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.user.username} (Supervisor: {self.is_supervisor})"
