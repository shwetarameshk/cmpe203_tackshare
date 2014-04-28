from django.conf.urls import patterns, include, url
from tack import views
from tackshare import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'TackShare.tack.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', include('tack.urls')),
    url(r'^login', views.login_user, name='loginUser'),
    url(r'^logout', views.logout_user, name='logoutUser'),
    url(r'^update', views.update_user, name='updateUser'),
    url(r'^profileupdate', views.update_user_profile, name='updateUserProfile'),
    url(r'^showdashboard', views.update_dashboard, name='updateDashboard'),
    url(r'^register', views.register, name='register'),
    url(r'^createtack', views.createTack, name='tack'),
    url(r'^saveTack',views.saveTack,name='saveTack'),
    url(r'^createboard', views.createBoard, name='createBoard'),
    url(r'^createNewBoard',views.createNewBoard,name='createNewBoard'),
    url(r'^saveBoard', views.saveBoard,name='saveBoard'),
    url(r'^shareBoard', views.shareBoard,name='shareBoard'),
    url(r'^board',views.showTacks,name='showTacks'),
    url(r'^displayTack',views.displayTack,name='displayTacks'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
)
