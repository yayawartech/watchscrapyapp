from django.urls import path, re_path
from goldapp import views

urlpatterns = [
    path("", views.home),
    path("updateConfig/", views.update_configuration),
    path("chart_data/<str:val>", views.chart_data),
    path("fetchNow/", views.fetchNow),
    
    re_path(r'^getdata_json/(?P<percentage>\d+(?:\.\d+)?)/(?P<goldgram>\d+(?:\.\d+)?)',
            views.myajaxview, name='getdata_json'),
    re_path(r'^gold_data/(?P<carat>\w+?)/(?P<goldgram>\d+(?:\.\d+)?)/(?P<percentage>\d+(?:\.\d+)?)',
            views.gold_data, name='gold_data'),
    re_path(r'^platinum_data/(?P<platinumgram>\d+(?:\.\d+)?)/(?P<percentage>\d+(?:\.\d+)?)',
            views.platinum_data, name='platinum_data'),
    re_path(r'^silver_data/(?P<carat>\w+?)/(?P<silvergram>\d+(?:\.\d+)?)/(?P<percentage>\d+(?:\.\d+)?)',
            views.silver_data, name='silver_data'),
]
