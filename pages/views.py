from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Page
from django.views.decorators.csrf import requires_csrf_token


def _nav_pages(request):
    tenant = getattr(request, "tenant", None)
    if not tenant:
        return []
    return Page.objects.filter(
        tenant=tenant, is_published=True
    ).order_by("nav_order", "title").only("slug", "nav_label", "is_home", "title")

def _render_page(request, page: Page):
    return render(
        request,
        "pages/page_detail.html",
        {
            "page": page,
            "blocks": list(page.blocks.all()),
            "nav_pages": _nav_pages(request),
        },
    )

def home_router(request):
    """
    If a tenant is resolved, render its published Home page.
    Otherwise show a tiny placeholder (so / still works on non-tenant hosts).
    """
    tenant = getattr(request, "tenant", None)
    if tenant:
        page = (
            Page.objects.filter(tenant=tenant, is_home=True, is_published=True)
            .prefetch_related("blocks")
            .first()
        )
        if page:
            return _render_page(request, page)
        # No home yet → try first published page as a soft fallback
        page = (
            Page.objects.filter(tenant=tenant, is_published=True)
            .order_by("nav_order", "title")
            .prefetch_related("blocks")
            .first()
        )
        if page:
            return _render_page(request, page)

    return HttpResponse(
        "<div style='padding:2rem;font-family:ui-sans-serif;color:#e5e7eb;"
        "background:#0a0a0a'>No tenant home page yet.</div>"
    )

def page_detail(request, slug: str):
    tenant = getattr(request, "tenant", None)
    if not tenant:
        raise Http404("Tenant not resolved")
    page = get_object_or_404(
        Page.objects.prefetch_related("blocks"),
        tenant=tenant,
        slug=slug,
        is_published=True,
    )
    return _render_page(request, page)

@requires_csrf_token
def site_404(request, exception):
    tenant = getattr(request, "tenant", None)
    ctx = {
        "nav_pages": _nav_pages(request),
        "tenant": tenant,
        "path": request.path,
    }
    return render(request, "pages/site_404.html", ctx, status=404)
