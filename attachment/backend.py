from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
            
        except User.DoesNotExist:
            print(f"User with email {email} does not exist.")
            return None
        except Exception as e:
            print(f"An error occurred during authentication: {e}")
            return None
      
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
   