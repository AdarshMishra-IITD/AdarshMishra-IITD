from django.contrib import admin
from .models import App, Review, ReviewApproval, UserProfile

admin.site.register(App)
admin.site.register(Review)
admin.site.register(ReviewApproval)
admin.site.register(UserProfile)
