from django.views.generic.base import TemplateView


class APIHome(TemplateView):
    """View to render the API landing page"""

    template_name = 'home.html'
