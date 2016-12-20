from django.contrib.sites.requests import RequestSite


def site(request):
    site_info = {'protocol': request.is_secure() and 'https' or 'http'}
    site_info['domain'] = RequestSite(request).domain
    return {'site_info': site_info}
