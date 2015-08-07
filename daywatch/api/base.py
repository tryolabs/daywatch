from rest_framework import viewsets
from rest_framework import views
from rest_framework.permissions import IsAuthenticated


class DayWatchView():
    """A superclass for model-based and non-model view classes."""

    permission_classes = (IsAuthenticated,)

    def ex(self, field):
        return self.request.QUERY_PARAMS.get(field, None)


class DayWatchModelView(DayWatchView, viewsets.ModelViewSet):
    """A view for models."""

    def filter(self, name):
        if isinstance(name, tuple):
            param = self.ex(name[0])
            exp = name[1]
            if(param):
                self.queryset = self.queryset.filter(**{exp: param})
        else:
            param = self.ex(name)
            if(param):
                self.queryset = self.queryset.filter(**{name: param})

    def filters(self, names):
        for field_name in names:
            self.filter(field_name)

    def get_queryset(self):
        self.queryset = self.model.objects.all()
        self.filters(self.filter_fields)
        user = self.request.user
        if hasattr(self, 'filter_user'):
            self.queryset = self.filter_user(user)
        return self.queryset


class DayWatchManualView(DayWatchView, views.APIView):
    pass
