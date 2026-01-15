from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap

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

    # CHATBOT (UNCOMMENTED)
    path("api/chatbot/", views.chatbot_response, name="chatbot_response"),

    # ADMIN PANEL
    path("admin/", admin.site.urls),

    #google site verification
    path("googleb5949ab1058f2676.html", views.google_verify),

    #seo
    path("robots.txt", views.robots_txt),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
