from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

try:
    site = Site.objects.get(pk=3)
    print(f"Site with ID 3 found: {site.domain}")
except Site.DoesNotExist:
    print("Site with ID 3 does not exist.")
    
    # Attempt to create the site, as it seems to be the intended next step.
    try:
        new_site, created = Site.objects.get_or_create(pk=3, defaults={'domain': 'example.com', 'name': 'example.com'})
        if created:
            print("Site with ID 3 was created.")
        else:
            print("Site with ID 3 was found after all, but something is wrong.")
    except Exception as e:
        print(f"Could not create site with ID 3: {e}")

try:
    google_app = SocialApp.objects.get(provider='google')
    print(f"Google SocialApp found: {google_app.name}")
except SocialApp.DoesNotExist:
    print("Google SocialApp does not exist.")
    
    # Attempt to create the SocialApp, as it seems to be the intended next step.
    try:
        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='your-client-id',
            secret='your-secret-key',
        )
        app.sites.add(3)
        print("Google SocialApp created.")
    except Exception as e:
        print(f"Could not create Google SocialApp: {e}")
except Exception as e:
    print(f"An error occurred while checking for the Google SocialApp: {e}")
