from rest_framework import viewsets

from lego.apps.permissions.views import AllowedPermissionsMixin
from lego.apps.social_groups.models import InterestGroup
from lego.apps.social_groups.permissions import InterestGroupPermissions
from lego.apps.social_groups.serializers import (InterestGroupCreateAndUpdateSerializer,
                                                 InterestGroupSerializer)


class InterestGroupViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = InterestGroup.group_objects.all()
    permission_classes = [InterestGroupPermissions]
    serializer_class = InterestGroupSerializer
    ordering = 'id'

    def get_queryset(self):
        if self.action == 'retrieve':
            return self.queryset.prefetch_related('users')

        return self.queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return InterestGroupCreateAndUpdateSerializer
        return InterestGroupSerializer
