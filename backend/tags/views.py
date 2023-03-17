from rest_framework import viewsets

from .models import Tag

from .serializers import TagSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ("get",)

    def get_queryset(self):
        query_params = self.request.query_params

        name_filter = query_params.get("name")
        if name_filter:
            return self.queryset.filter(
                name__startswith=name_filter
            )

        return self.queryset
