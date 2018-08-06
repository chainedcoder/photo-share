from rest_framework.response import Response
from rest_framework import pagination


class CustomPaginator(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


class SmallResultsSetPagination(CustomPaginator):
    page_size = 10
