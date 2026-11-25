
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView

User = get_user_model()


class UsersPage(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = "users.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.all().order_by("id")

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):

        # DISABLE USER
        if "disable" in request.POST:
            user_id = request.POST.get("disable")
            target_user = get_object_or_404(User, id=user_id)

            if target_user.is_superuser or target_user.id == request.user.id:
                messages.error(request, "This user cannot be disabled!")
            else:
                target_user.is_active = False
                target_user.save()
                messages.success(request, "User disabled successfully!")

        # ENABLE USER
        elif "enable" in request.POST:
            user_id = request.POST.get("enable")
            target_user = get_object_or_404(User, id=user_id)

            if target_user.is_superuser:
                messages.error(request, "Cannot change superuser status!")
            else:
                target_user.is_active = True
                target_user.save()
                messages.success(request, "User enabled successfully!")

        # RESET PASSWORD
        elif "reset" in request.POST:
            user_id = request.POST.get("reset")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            target_user = get_object_or_404(User, id=user_id)

            if target_user.is_superuser:
                messages.error(request, "Cannot reset superuser password here!")
            elif not new_password or not confirm_password:
                messages.error(request, "Password fields cannot be empty!")
            elif new_password != confirm_password:
                messages.error(request, "Passwords do not match!")
            elif len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters!")
            else:
                target_user.set_password(new_password)
                target_user.save()
                messages.success(request, "Password changed successfully!")

        # ADD USER
        elif "first" in request.POST:
            first_name = request.POST.get("first", "").strip()
            last_name = request.POST.get("last", "").strip()
            email = request.POST.get("email", "").strip().lower()
            role = request.POST.get("role", "Cashier")
            password = request.POST.get("pw", "")

            if not first_name or not last_name or not email or not password:
                messages.error(request, "All fields are required!")

            elif User.objects.filter(username=email).exists():
                messages.error(request, "This email is already registered!")

            elif len(password) < 8:
                messages.error(request, "Password must be at least 8 characters!")

            elif role not in ["Admin", "Cashier"]:
                messages.error(request, "Invalid user role!")

            else:
                is_admin = role == "Admin"

                User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    is_staff=is_admin,
                    is_superuser=is_admin
                )

                messages.success(request, "User created successfully!")

        return redirect("accounts:users_page")
