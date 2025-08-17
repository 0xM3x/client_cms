from django.contrib import admin
from .models import Tenant, Domain

class DomainInline(admin.TabularInline):
    model = Domain
    extra = 0
    fields = ("host", "is_primary", "status", "verify_token", "verified_at")
    readonly_fields = ("verify_token", "verified_at")

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "created_at")
    search_fields = ("slug", "name")
    inlines = [DomainInline]

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("host", "tenant", "is_primary", "status", "created_at")
    search_fields = ("host", "tenant__slug")
    list_filter = ("status", "is_primary")

