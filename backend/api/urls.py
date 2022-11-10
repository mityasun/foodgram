from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path(r'', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
    path(
        'v1/redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]