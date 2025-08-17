import uuid, secrets
from django.db import models

class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self):
        return f"{self.slug} — {self.name}"

STATUS_CHOICES = [
    ("pending", "Pending"),
    ("active", "Active"),
    ("error", "Error"),
]

class Domain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="domains")
    host = models.CharField(max_length=255, unique=True)  # e.g. acme.lvh.me or www.acme.com
    is_primary = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    verify_token = models.CharField(max_length=64, default=secrets.token_urlsafe, editable=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant"]),
        ]

    def __str__(self):
        return self.host

