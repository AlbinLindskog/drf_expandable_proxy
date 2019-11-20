from django.urls import path, include

from test_app.routers import router


urlpatterns = [
    path('/', include(router.urls)),
]
