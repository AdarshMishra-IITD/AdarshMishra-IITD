from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from playstore.models import UserProfile

class Command(BaseCommand):
    help = "Create or update a user and mark them as supervisor (playstore.UserProfile.is_supervisor=True)."

    def add_arguments(self, parser):
        parser.add_argument("username", help="Username to create or elevate")
        parser.add_argument("--password", help="Password (if creating). If omitted and user does not exist you'll be prompted.")
        parser.add_argument("--email", help="Email (if creating)")
        parser.add_argument("--no-input", action="store_true", help="Do not prompt for password; required if running non-interactively without --password.")
        parser.add_argument("--remove", action="store_true", help="Instead of granting, revoke supervisor role.")

    def handle(self, username, password=None, email=None, no_input=False, remove=False, **options):
        try:
            user = User.objects.get(username=username)
            created = False
        except User.DoesNotExist:
            if remove:
                raise CommandError("User does not exist; cannot revoke supervisor role.")
            if not password:
                if no_input:
                    raise CommandError("--no-input provided but no --password given for new user.")
                from django.contrib.auth.password_validation import validate_password
                from getpass import getpass
                while not password:
                    pwd1 = getpass(f"Set password for new user '{username}': ")
                    pwd2 = getpass("Confirm password: ")
                    if pwd1 != pwd2:
                        self.stderr.write(self.style.WARNING("Passwords do not match. Try again."))
                        continue
                    try:
                        validate_password(pwd1)
                    except Exception as e:  # pragma: no cover - interactive branch
                        self.stderr.write(self.style.WARNING(f"Password validation error: {e}"))
                        continue
                    password = pwd1
            user = User.objects.create_user(username=username, password=password, email=email or "")
            created = True

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if remove:
            if profile.is_supervisor:
                profile.is_supervisor = False
                profile.save()
                self.stdout.write(self.style.SUCCESS(f"Revoked supervisor role from '{username}'."))
            else:
                self.stdout.write(f"User '{username}' was not a supervisor.")
            return

        if not profile.is_supervisor:
            profile.is_supervisor = True
            profile.save()
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} user '{username}' and granted supervisor role."))
        else:
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created user '{username}' (already marked supervisor)."))
            else:
                self.stdout.write(f"User '{username}' is already a supervisor.")

        self.stdout.write(f"Login via /accounts/login/ then access /supervisor/reviews/.")
