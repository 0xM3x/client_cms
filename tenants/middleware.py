from django.utils.deprecation import MiddlewareMixin
from .models import Tenant, Domain

def _parse_host(request) -> str | None:
    host = request.get_host() or ""
    host = host.split(":")[0].strip().lower()
    return host or None

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.tenant = None
        slug = (request.GET.get("tenant") or "").strip().lower() or None
        host = _parse_host(request)

        tenant = None
        if slug:
            tenant = Tenant.objects.filter(slug=slug).first()
        if not tenant and host:
            dom = Domain.objects.select_related("tenant").filter(host=host).first()
            tenant = dom.tenant if dom else None

        request.tenant = tenant
        # quick debug log in runserver
        if host:
            print(f"[tenant] host={host} slug={slug or '-'} -> tenant={getattr(tenant,'slug','-')}")

