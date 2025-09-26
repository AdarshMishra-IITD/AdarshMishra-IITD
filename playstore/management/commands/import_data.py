
import pandas as pd
from django.core.management.base import BaseCommand
from playstore.models import App, Review
from django.contrib.auth.models import User
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../scripts')))
from scripts.clean_data import clean_googleplaystore, clean_user_reviews

class Command(BaseCommand):
    help = 'Load apps and reviews from CSV files'

    def handle(self, *args, **kwargs):
        # If data already exists, skip to keep command idempotent
        if App.objects.exists():
            self.stdout.write(self.style.WARNING('Apps already present; skipping import.'))
            return
        # Clean data before loading
        base = 'playstore/migrations/csv_data/'
        clean_googleplaystore(base + 'googleplaystore.csv', base + 'googleplaystore_clean.csv')
        clean_user_reviews(base + 'googleplaystore_user_reviews.csv', base + 'googleplaystore_user_reviews_clean.csv')

        # Load apps
        apps_df = pd.read_csv(base + 'googleplaystore_clean.csv')
        for _, row in apps_df.iterrows():
            App.objects.get_or_create(
                name=row.get('App', ''),
                defaults={
                    'category': row.get('Category', ''),
                    'rating': row.get('Rating') if pd.notnull(row.get('Rating')) else None,
                    'reviews_count': row.get('Reviews') if pd.notnull(row.get('Reviews')) else None,
                    'size': row.get('Size', ''),
                    'installs': row.get('Installs', ''),
                    'type': row.get('Type', ''),
                    'price': row.get('Price', ''),
                    'content_rating': row.get('Content Rating', ''),
                    'genres': row.get('Genres', ''),
                    'last_updated': row.get('Last Updated', ''),
                    'current_ver': row.get('Current Ver', ''),
                    'android_ver': row.get('Android Ver', ''),
                }
            )
        self.stdout.write(self.style.SUCCESS('Apps loaded.'))

        # Load reviews
        reviews_df = pd.read_csv(base + 'googleplaystore_user_reviews_clean.csv')
        default_user, _ = User.objects.get_or_create(username='imported_user')
        for _, row in reviews_df.iterrows():
            app = App.objects.filter(name=row.get('App', '')).first()
            if app and pd.notnull(row.get('Translated_Review')):
                Review.objects.create(
                    app=app,
                    user=default_user,
                    text=row.get('Translated_Review', ''),
                    sentiment=row.get('Sentiment', ''),
                    sentiment_polarity=row.get('Sentiment_Polarity') if pd.notnull(row.get('Sentiment_Polarity')) else None,
                    sentiment_subjectivity=row.get('Sentiment_Subjectivity') if pd.notnull(row.get('Sentiment_Subjectivity')) else None,
                    approved=True
                )
        self.stdout.write(self.style.SUCCESS('Reviews loaded.'))
