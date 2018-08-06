from rest_framework.generics import ListAPIView

from .models import Feed
from .serializers import FeedSerializer


class FeedListView(ListAPIView):
    serializer_class = FeedSerializer

    def get_queryset(self):
        return Feed.objects.filter(user_to=self.request.user)
