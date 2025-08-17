from django.contrib import admin, messages
from django.utils import timezone
from django.db import models
from django.urls import path, reverse
from django.shortcuts import redirect
from django.core import signing

from .models import Page, Block


class BlockInline(admin.TabularInline):
    model = Block
    extra = 0
    fields = ("order", "kind", "data")
    ordering = ("order", "id")
    formfield_overrides = {
        models.JSONField: {
            "widget": admin.widgets.AdminTextareaWidget(attrs={"rows": 6, "cols": 100})
        }
    }
    verbose_name = "Block"
    verbose_name_plural = "Blocks"


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "tenant",
        "slug",
        "is_published",
        "is_home",
        "nav_order",
        "updated_at",
    )
    list_filter = ("tenant", "is_published", "is_home")
    search_fields = ("title", "slug", "nav_label")
    ordering = ("tenant__slug", "nav_order", "title")
    list_select_related = ("tenant",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [BlockInline]
    readonly_fields = ("created_at", "updated_at", "published_at")
    change_form_template = "admin/pages/page/change_form.html"
    fieldsets = (
        (None, {
            "fields": (
                "tenant",
                ("title", "slug"),
                ("is_published", "is_home"),
                ("nav_label", "nav_order"),
            )
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("published_at", "created_at", "updated_at"),
        }),
    )

    # ---------- Admin actions ----------
    actions = ["publish_pages", "unpublish_pages", "make_home_page"]

    def publish_pages(self, request, queryset):
        now = timezone.now()
        updated = 0
        for page in queryset:
            if not page.is_published or page.published_at is None:
                page.is_published = True
                if page.published_at is None:
                    page.published_at = now
                page.save()
                updated += 1
        self.message_user(request, f"Published {updated} page(s).", level=messages.SUCCESS)

    publish_pages.short_description = "Publish selected pages"

    def unpublish_pages(self, request, queryset):
        updated = queryset.update(is_published=False)
        # keep published_at for historical info; we don't null it to preserve history
        self.message_user(request, f"Unpublished {updated} page(s).", level=messages.WARNING)

    unpublish_pages.short_description = "Unpublish selected pages"

    def make_home_page(self, request, queryset):
        """
        Mark exactly one selected page as the tenant's home page.
        If multiple are selected, we’ll apply to each (last one wins per tenant).
        The Page.save() already enforces single-home-per-tenant by unsetting others.
        """
        count = 0
        for page in queryset:
            page.is_home = True
            page.save()  # triggers model logic to unset other home pages for the same tenant
            count += 1
        self.message_user(request, f"Set {count} page(s) as home.", level=messages.SUCCESS)

    make_home_page.short_description = "Make selected page(s) the Home for its tenant"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<path:object_id>/preview/",
                self.admin_site.admin_view(self.preview_view),
                name="pages_page_preview",
            ),
        ]
        return custom + urls
    
    def preview_view(self, request, object_id):
        page = self.get_object(request, object_id)
        token = signing.dumps({"page_id": page.pk}, salt="pages.preview")
        url = request.build_absolute_uri(reverse("page_preview", args=[token]))
        return redirect(url)
