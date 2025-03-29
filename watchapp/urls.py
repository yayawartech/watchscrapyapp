# from django.conf.urls import url
# from django.urls import path
# from . import views

# urlpatterns = [
# 	url(r'^$', views.login, name='login'),
# 	url(r'^logout/$', views.logout, name='logout'),
# 	url(r'^home/$', views.home, name='home'),
# 	url(r'^watch/$', views.index, name='index'),
# 	url(r'^watch/lot/(?P<lot>[A-Za-z0-9]+)/$', views.lot_details, name='lot_details'),
# 	url(r'^jobs/(?P<job>[0-9]+)/$', views.job_details, name='job_details'),
# 	url(r'^jobs/kill/(?P<job>[0-9]+)/$', views.job_kill, name='job_kill'),
# 	url(r'^jobs/run/(?P<job>[0-9]+)/$', views.job_run, name='job_run'),
# 	url(r'^watch/advsearch/$', views.advsearch, name='advsearch'),
# 	url(r'^jobs/$', views.allJobs, name='allJobs'),
# 	url(r'^jobs-progress/(?P<job>[0-9]+)/$', views.job_progress_details, name='job_progress_details'),
# 	url(r'^jobs/complete/$', views.completedJobs, name='completedJobs'),
# 	url(r'^jobs/failed/$', views.failedJobs, name='failedJobs'),
# 	url(r'^jobs/add$', views.addJobs, name='addJobs'),
# 	url(r'^jobs/create$', views.createJobs, name='createJobs'),
# 	url(r'^setup$', views.setup, name='setup'),
# 	url(r'^houses$', views.houses, name='houses'),
# 	url(r'^houses/(?P<house>[0-9]+)/$', views.house_details, name='house_details'),
# 	url(r'^jobs/runURL/(?P<auction>[0-9]+)/$', views.auction_run, name='auction_run'),
#         url(r'^rolex_year$',views.rolex_year,name='rolex_year'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),
    path('watch/', views.index, name='index'),
    path('watch/lot/<str:lot>/', views.lot_details, name='lot_details'),
    path('watch/lot/edit/<str:lot>/', views.edit_lot_details, name='edit_lot_details'),
    path('jobs/<int:job>/', views.job_details, name='job_details'),
    path('jobs/kill/<int:job>/', views.job_kill, name='job_kill'),
    path('jobs/run/<int:job>/', views.job_run, name='job_run'),
    path('watch/advsearch/', views.advsearch, name='advsearch'),
    path('jobs/', views.allJobs, name='allJobs'),
    path('jobs-progress/<int:job>/', views.job_progress_details, name='job_progress_details'),
    path('jobs/complete/', views.completedJobs, name='completedJobs'),
    path('jobs/failed/', views.failedJobs, name='failedJobs'),
    path('jobs/add', views.addJobs, name='addJobs'),
    path('jobs/create', views.createJobs, name='createJobs'),
    path('setup', views.setup, name='setup'),
    path('houses', views.houses, name='houses'),
    path('houses/<int:house>/', views.house_details, name='house_details'),
    path('jobs/runURL/<int:auction>/', views.auction_run, name='auction_run'),
    path('rolex_year', views.rolex_year, name='rolex_year'),
]
