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
    url(r'^searchUsers',views.search_users,name='searchUsers'),
    url(r'^autoComplete',views.auto_complete_model,name='autoComplete'),
    url(r'^FollowUser',views.follow_user,name='followUser'),
    url(r'^autoBoardComplete',views.auto_board_complete,name='autoBoardComplete'),
    url(r'^searchBoards',views.search_boards,name='searchBoards'),
    url(r'^ConfirmFav',views.confirm_fav,name='confirmFav'),
    url(r'^viewFavorites',views.view_favorites,name='viewFavorites'),
    url(r'^searchTags',views.search_tags,name='searchTags'),
    url(r'^manageemail', views.manage_email, name='manageemail'),
    url(r'^profileupdate', views.update_user_profile, name='updateUserProfile'),
    url(r'^showdashboard', views.update_dashboard, name='updateDashboard'),
    url(r'^register', views.register, name='register'),
    url(r'^createtack', views.create_tack, name='tack'),
    url(r'^newurltack', views.create_tack_url, name='tack'),
    url(r'^saveTack',views.save_tack,name='saveTack'),
    url(r'^UrlsaveTack',views.url_save_tack,name='urlSaveTack'),
    url(r'^createboard', views.create_board, name='createBoard'),
    url(r'^savesubscription',views.save_subscription,name='savesubscription'),
    url(r'^saveBoard', views.save_board,name='saveBoard'),
    url(r'^shareBoard', views.share_board,name='shareBoard'),
    url(r'^shareWithUser',views.share_with_user,name='shareWithUser'),
    url(r'^unShareBoard',views.unshare_board,name='unShareBoard'),
    url(r'^editBoardPrivacy',views.edit_board_privacy,name='editBoardPrivacy'),
    url(r'^changeBoardPrivacy',views.change_board_privacy,name='changeBoardPrivacy'),
    url(r'^board',views.show_tacks,name='showTacks'),
    url(r'^displayTack',views.display_tack,name='displayTacks'),
    url(r'^createTackInBoard',views.create_tack_in_board,name='createTackInBoard'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    url(r'^editTack',views.edit_tack,name='editTack'),
    url(r'^displayInfoScreen',views.display_info_screen,name='displayInfoScreen'),
    url(r'^SaveFollow',views.save_follow,name='saveFollow')

)
