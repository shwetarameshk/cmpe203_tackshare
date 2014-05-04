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
    url(r'^accounts', views.home,name='home'),
    url(r'^login', views.login_user, name='loginUser'),
    url(r'^logout', views.logout_user, name='logoutUser'),
    url(r'^update', views.update_user, name='updateUser'),
    url(r'^searchUsers',views.searchUsers,name='searchUsers'),
    url(r'^autoComplete',views.autocompleteModel,name='autoComplete'),
    url(r'^FollowUser',views.followUser,name='followUser'),
    url(r'^autoBoardComplete',views.autoBoardComplete,name='autoBoardComplete'),
    url(r'^searchBoards',views.searchBoards,name='searchBoards'),
    url(r'^ConfirmFav',views.confirmFav,name='confirmFav'),
    url(r'^viewFavorites',views.viewFavorites,name='viewFavorites'),
    url(r'^searchTags',views.searchTags,name='searchTags'),
    url(r'^manageemail', views.manageemail, name='manageemail'),
    url(r'^profileupdate', views.update_user_profile, name='updateUserProfile'),
    url(r'^showdashboard', views.update_dashboard, name='updateDashboard'),
    url(r'^register', views.register, name='register'),
    url(r'^createtack', views.createTack, name='tack'),
    url(r'^newurltack', views.createTackUrl, name='tack'),
    url(r'^saveTack',views.saveTack,name='saveTack'),
    url(r'^UrlsaveTack',views.UrlsaveTack,name='urlSaveTack'),
    url(r'^createboard', views.createBoard, name='createBoard'),
    url(r'^savesubscription',views.savesubscription,name='savesubscription'),
    url(r'^saveBoard', views.saveBoard,name='saveBoard'),
    url(r'^shareBoard', views.shareBoard,name='shareBoard'),
    url(r'^shareWithUser',views.shareWithUser,name='shareWithUser'),
    url(r'^unShareBoard',views.unShareBoard,name='unShareBoard'),
    url(r'^editBoardPrivacy',views.editBoardPrivacy,name='editBoardPrivacy'),
    url(r'^changeBoardPrivacy',views.changeBoardPrivacy,name='changeBoardPrivacy'),
    url(r'^board',views.showTacks,name='showTacks'),
    url(r'^displayTack',views.displayTack,name='displayTacks'),
    url(r'^createTackInBoard',views.createTackInBoard,name='createTackInBoard'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    url(r'^editTack',views.editTack,name='editTack'),
    url(r'^displayInfoScreen',views.displayInfoScreen,name='displayInfoScreen')
)
