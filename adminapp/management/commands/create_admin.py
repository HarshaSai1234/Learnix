from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from adminapp.models import Admin

class Command(BaseCommand):
    help = 'Create initial admin account'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='Admin', help='Admin username')
        parser.add_argument('--email', type=str, default='admin@learnix.com', help='Admin email')
        parser.add_argument('--password', type=str, default='Admin12345', help='Admin password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if Admin.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Admin with username "{username}" already exists!'))
            return

        admin = Admin.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )
        self.stdout.write(self.style.SUCCESS(f'Successfully created admin account:'))
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Email: {email}')
        self.stdout.write(f'  Password: {password}')
