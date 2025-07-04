from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Crée un token d\'API pour un utilisateur'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nom d\'utilisateur')
        parser.add_argument(
            '--create-user',
            action='store_true',
            help='Créer l\'utilisateur s\'il n\'existe pas',
        )

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            if options['create_user']:
                user = User.objects.create_user(username=username)
                self.stdout.write(
                    self.style.SUCCESS(f'Utilisateur "{username}" créé.')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Utilisateur "{username}" n\'existe pas. Utilisez --create-user pour le créer.')
                )
                return

        token, created = Token.objects.get_or_create(user=user)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Token créé pour "{username}": {token.key}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Token existant pour "{username}": {token.key}')
            ) 