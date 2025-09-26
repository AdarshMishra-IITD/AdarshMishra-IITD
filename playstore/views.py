
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import App, Review, ReviewApproval, UserProfile
from django.contrib.auth.models import User
from django.db.models import Q
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login as auth_login


# Custom registration form with email
class CustomUserCreationForm(UserCreationForm):
	email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

	class Meta(UserCreationForm.Meta):
		model = User
		fields = UserCreationForm.Meta.fields + ('email',)

	def save(self, commit=True):
		user = super().save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

def register(request):
	if request.method == 'POST':
		form = CustomUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			UserProfile.objects.create(user=user)
			auth_login(request, user)
			messages.success(request, 'Registration successful!')
			return redirect('profile')
		else:
			messages.error(request, 'Please correct the errors below.')
	else:
		form = CustomUserCreationForm()
	return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
	profile = UserProfile.objects.get(user=request.user)
	return render(request, 'registration/profile.html', {'profile': profile})

def search(request):
	query = request.GET.get('q', '')
	results = []
	if query:
		apps = App.objects.all()
		names = [app.name for app in apps]
		if names:
			vectorizer = TfidfVectorizer()
			tfidf_matrix = vectorizer.fit_transform(names)
			query_vec = vectorizer.transform([query])
			similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
			top_indices = similarities.argsort()[-10:][::-1]
			results = [apps[int(i)] for i in top_indices if similarities[i] > 0.1]
		else:
			results = []
	return render(request, 'search.html', {'results': results, 'query': query})

def autocomplete(request):
	import logging
	logger = logging.getLogger(__name__)
	term = request.GET.get('term', '')
	suggestions = []
	logger.info(f"Autocomplete called with term: '{term}'")
	if len(term) >= 3:
		suggestions = list(App.objects.filter(name__icontains=term).values_list('name', flat=True)[:10])
	logger.info(f"Suggestions returned: {suggestions}")
	return JsonResponse(suggestions, safe=False)

def app_detail(request, app_id):
	app = get_object_or_404(App, id=app_id)
	reviews = app.reviews.filter(approved=True)
	# Sentiment stats
	sentiment_counts = {
		'positive': reviews.filter(sentiment__iexact='positive').count(),
		'negative': reviews.filter(sentiment__iexact='negative').count(),
		'neutral': reviews.filter(sentiment__iexact='neutral').count(),
		'total': reviews.count(),
	}
	return render(request, 'app_detail.html', {
		'app': app,
		'reviews': reviews,
		'sentiment_counts': sentiment_counts,
	})

@login_required
def add_review(request, app_id):
	app = get_object_or_404(App, id=app_id)
	if request.method == 'POST':
		text = request.POST.get('text')
		review = Review.objects.create(app=app, user=request.user, text=text, approved=False)
		from django.contrib import messages
		messages.success(request, 'Your review has been submitted and is pending approval.')
		return redirect('app_detail', app_id=app.id)
	return render(request, 'add_review.html', {'app': app})

@login_required
def supervisor_reviews(request):
	profile = UserProfile.objects.get(user=request.user)
	if not profile.is_supervisor:
		return redirect('search')
	reviews = Review.objects.filter(approved=False)
	sentiment_counts = {
		'positive': reviews.filter(sentiment__iexact='positive').count(),
		'negative': reviews.filter(sentiment__iexact='negative').count(),
		'neutral': reviews.filter(sentiment__iexact='neutral').count(),
		'total': reviews.count(),
	}
	return render(request, 'supervisor_reviews.html', {
		'reviews': reviews,
		'sentiment_counts': sentiment_counts,
	})

@login_required
def approve_review(request, review_id):
	profile = UserProfile.objects.get(user=request.user)
	if not profile.is_supervisor:
		return redirect('search')
	review = get_object_or_404(Review, id=review_id)
	if request.method == 'POST':
		review.approved = True
		review.save()
		ReviewApproval.objects.create(review=review, supervisor=request.user, approved=True)
	return redirect('supervisor_reviews')
