from django.core.management.base import BaseCommand, CommandError

from adminside.models import Admin, Role


class Command(BaseCommand):
    help = "Create (or update) a single super admin account for bootstrap."

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True, help="admin name")
        parser.add_argument("--email", required=True, help="admin email")
        parser.add_argument("--phone", required=True, help="admin phone")
        parser.add_argument("--password", required=True, help="admin password")
        parser.add_argument(
            "--role",
            default="admin",
            help="Role name to use for the super admin (default: admin)",
        )

    def handle(self, *args, **options):
        role_name = options["role"].strip()
        if not role_name:
            raise CommandError("Role cannot be empty.")

        role, _ = Role.objects.get_or_create(
            role=role_name,
            defaults={"is_admin": True, "permission": ["all"]},
        )

        if not role.is_admin:
            role.is_admin = True
            role.permission = ["all"]
            role.save(update_fields=["is_admin", "permission", "updated_at"])

        email = options["email"].strip().lower()

        existing_super_admin = Admin.objects.filter(role=role, deleted_at__isnull=True).exclude(email=email).first()
        if existing_super_admin:
            raise CommandError(
                f"A super admin already exists with email {existing_super_admin.email}. "
                "Update that account instead of creating another one."
            )

        admin, created = Admin.objects.get_or_create(
            email=email,
            defaults={
                "name": options["name"].strip(),
                "phone": options["phone"].strip(),
                "status": True,
                "role": role,
            },
        )

        if created:
            admin.set_password(options["password"])
            admin.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS("Super admin created successfully."))
            return

        admin.name = options["name"].strip()
        admin.phone = options["phone"].strip()
        admin.status = True
        admin.role = role
        admin.set_password(options["password"])
        admin.save(update_fields=["name", "phone", "status", "role", "password", "updated_at"])
        self.stdout.write(self.style.WARNING("Super admin already existed; account has been updated."))
