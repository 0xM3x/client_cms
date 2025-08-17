from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from .models import Page
from django.views.decorators.csrf import requires_csrf_token
from django.core import signing
from django.utils import timezone




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

def page_preview(request, token: str):
    """
    Render a Page by signed token (valid 10 minutes) regardless of is_published.
    Link is generated from Admin and meant for staff use.
    """
    try:
        data = signing.loads(token, max_age=600, salt="pages.preview")  # 10 minutes
        page_id = data["page_id"]
    except signing.SignatureExpired:
        return HttpResponseForbidden("Preview link expired.")
    except signing.BadSignature:
        raise Http404("Invalid preview token.")

    page = get_object_or_404(Page.objects.prefetch_related("blocks"), pk=page_id)
    # Ensure templates show the correct tenant brand/nav even if host didn’t resolve
    setattr(request, "tenant", page.tenant)
    return _render_page(request, page)

def tenant_sitemap(request):
    tenant = getattr(request, "tenant", None)
    if not tenant:
        raise Http404("Tenant not resolved")

    pages_qs = (
        Page.objects.filter(tenant=tenant, is_published=True)
        .only("slug", "is_home", "updated_at")
        .order_by("nav_order", "title")
    )
    home = pages_qs.filter(is_home=True).first()
    base = f"{request.scheme}://{request.get_host()}"

    ctx = {
        "base": base,
        "pages": pages_qs,
        "home_updated": getattr(home, "updated_at", None),
    }
    return render(request, "pages/sitemap.xml", ctx, content_type="application/xml")
