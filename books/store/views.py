from django.db.models import Count, Case, When, Avg, F
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import Book, UserBookRelation
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BooksSerializer, UserBookRelationSerializer
from rest_framework.mixins import UpdateModelMixin


class BookViewSet(ModelViewSet):
    #queryset = Book.objects.all()
    queryset = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            #rating=Avg('userbookrelation__rate'),
            final_price=Case(
                        When(discount=None, then='price'), default=F('price') - F('discount')
                     ),
            owner_name=F('owner__username')
            #final_price = F('price') - F('discount')
        #).select_related('owner').prefetch_related('readers').order_by('id')
        ).prefetch_related('readers').order_by('id')
    serializer_class = BooksSerializer
    #authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price']
    search_fields = ['name', 'author_name']
    ordering_fields = ['price', 'author_name']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, _ = UserBookRelation.objects.get_or_create(user=self.request.user, book_id =self.kwargs['book'])
        return obj


def auth(request):
    return render(request, 'oauth.html')
