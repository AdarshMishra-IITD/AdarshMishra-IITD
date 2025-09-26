
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import App, Review, ReviewApproval, UserProfile
from django.contrib.auth.models import User
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

_SEARCH_CACHE = {
	'version': 0,  # bump if logic changes
	'app_count': 0,
	'vectorizer': None,
	'matrix': None,
	'app_ids': [],
}

def _build_search_cache():  # pragma: no cover - simple helper
	apps = list(App.objects.all().only('id', 'name'))
	names = [a.name for a in apps]
	if not names:
		_SEARCH_CACHE.update({'app_count': 0, 'vectorizer': None, 'matrix': None, 'app_ids': []})
		return
	vectorizer = TfidfVectorizer()
	matrix = vectorizer.fit_transform(names)
	_SEARCH_CACHE.update({
		'app_count': len(apps),
		'vectorizer': vectorizer,
		'matrix': matrix,
		'app_ids': [a.id for a in apps],
	})

def search(request):
	query = request.GET.get('q', '').strip()
	results = []
	if query:
		# Refresh cache if app count changed (cheap heuristic)
		current_count = App.objects.count()
		if _SEARCH_CACHE['vectorizer'] is None or _SEARCH_CACHE['app_count'] != current_count:
			_build_search_cache()
		vec = _SEARCH_CACHE['vectorizer']
		mat = _SEARCH_CACHE['matrix']
		if vec is not None and mat is not None:
			query_vec = vec.transform([query])
			similarities = cosine_similarity(query_vec, mat).flatten()
			# Get top 10 with similarity threshold
			indices = similarities.argsort()[-10:][::-1]
			app_id_list = []
			for i in indices:
				if similarities[i] > 0.1:
					app_id_list.append(_SEARCH_CACHE['app_ids'][int(i)])
			results = list(App.objects.filter(id__in=app_id_list)) if app_id_list else []
	return render(request, 'search.html', {'results': results, 'query': query})

def autocomplete(request):
	term = request.GET.get('term', '').strip()
	if len(term) < 3:
		return JsonResponse([], safe=False)
	suggestions = list(App.objects.filter(name__icontains=term).values_list('name', flat=True)[:10])
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
