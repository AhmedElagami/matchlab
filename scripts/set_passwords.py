from django.contrib.auth.models import User

# Ensure admin user exists
admin, _ = User.objects.get_or_create(
    username="admin", defaults={"email": "admin@example.com"}
)
admin.email = "admin@example.com"
admin.is_staff = True
admin.is_superuser = True
admin.is_active = True
admin.set_password("admin123")
admin.save()

# Set passwords for all other users
count = 0
for user in User.objects.exclude(username="admin"):
    user.is_active = True
    user.set_password("testpass123")
    user.save()
    count += 1

print(f"Updated {count} fixture users to testpass123")
print("Admin ready: admin / admin123")
