from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # MAIN PAGES
    path("", views.homepage, name="homepage"),
    path("services/", views.services, name="services"),
    path("about/", views.about, name="about"),
    path("team/", views.team, name="team"),
    path("contact/", views.contact, name="contact"),

    # AUTH
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),

    # HARDWARE PAGE
    path("detection/", views.detection, name="detection"),
    #path("api/detect/", views.detect_api, name="detect_api"),

    # CAMERA AI
    path("ewaste-camera/", views.ewaste_camera_page, name="ewaste_camera_page"),
    path("api/camera-detect/", views.camera_ai_api, name="camera-ai"),

    # SERVICES
    path("data-destruction/", views.data_destruction, name="data_destruction"),
    path("refurbishment/", views.refurbishment, name="refurbishment"),

    # PICKUP
    path("pickup/", views.pickup, name="pickup"),

    # ADMIN REQUESTS
    path("reqs/", views.reqs, name="reqs"),

    # CHATBOT
    #path("api/chatbot/", views.chatbot_response, name="chatbot_response"),

    # ADMIN PANEL
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)