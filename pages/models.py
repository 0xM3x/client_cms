from django.db import models
from django.utils import timezone

class Page(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE, related_name="pages")
    slug = models.SlugField(max_length=120)
    title = models.CharField(max_length=200)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    is_home = models.BooleanField(default=False)
    nav_label = models.CharField(max_length=80, blank=True)
    nav_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("tenant", "slug"),)
        ordering = ("nav_order", "title")

    def save(self, *args, **kwargs):
        if not self.nav_label:
            self.nav_label = self.title
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        # enforce single home page per tenant
        if self.is_home:
            Page.objects.filter(tenant=self.tenant, is_home=True).exclude(pk=self.pk).update(is_home=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tenant.slug} / {self.title}"

class Block(models.Model):
    HERO = "hero"
    IMAGE = "image"
    KIND_CHOICES = [
        (HERO, "Hero"),
        (IMAGE, "Image"),
    ]
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="blocks")
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    order = models.PositiveIntegerField(default=0)
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return f"{self.page} [{self.kind}] #{self.order}"

