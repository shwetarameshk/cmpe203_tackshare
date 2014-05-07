from asyncore import write
import json
from django.contrib.auth.decorators import login_required
from django.core.files.temp import NamedTemporaryFile
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import requests
from tack.models import Users, TackImages, Boards, subscription, Followers
from django.db.models import Q
from tackshare import settings
from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from urlparse import urlparse
import urllib2
from django.core.files import File
from django.core.mail import send_mail
from PIL import Image
from itertools import chain
from django.core.files.base import ContentFile
import connect

# Create your views here.

def home(request):
    """
    This method is used to display the user's dashboard. Dashboard contains all the boards created by the user and the boards shared with the user.
    """
    if request.user.is_authenticated():
        whoami = get_user(request)
        print whoami
        yourBoards = Boards.objects.order_by('name').filter(username=whoami)
        if not yourBoards:
            yourBoards = "None"
        otherBoards = Boards.objects.order_by('name').filter(~Q(username = whoami))
        visibleBoards = []
        for board in otherBoards:
            visibleTo = board.visible_to_users
            if str(whoami) in visibleTo:
                visibleBoards.append(board)
        if not visibleBoards:
            visibleBoards = "None"
        print visibleBoards
        numPublicBoards = Boards.objects.filter(username=whoami,privacy='Public').count()
        numPrivateBoards = Boards.objects.filter(username=whoami,privacy='Private').count()
        numTacks = TackImages.objects.filter(username=whoami).count()
        return render_to_response("Dashboard.html", {'MEDIA_URL': settings.MEDIA_URL,'yourBoards':yourBoards,
                                                     'otherBoards':visibleBoards,
                                                    'numPublicBoards':numPublicBoards,
                                                    'numPrivateBoards':numPrivateBoards,
                                                    'numTacks':numTacks})
    else:
        return render_to_response('Home.html')

@login_required
def logout_user(request):
    """
    This method is used to log out the user from the current session.
    """
    logout(request)
    return render_to_response('Home.html')

@login_required
def update_user(request):
    """
    This method is used to update the user's profile.
    """
    return render_to_response('updateprofile.html', {'firstname':User.get_full_name(request.user),'username':User.get_username(request.user)})

@login_required
@csrf_exempt
def update_user_profile(request):
    """
    This method is used to update the user's password.
    """
    if request.POST["password"] == request.POST["passwordAgain"]:
        u = User.objects.get(username__exact=str(get_user(request)))
        u.set_password(request.POST["password"])
        u.save()
        return redirect("/")
    else:
        return render_to_response('updateprofile.html', {'firstname':User.get_full_name(request.user),'username':User.get_username(request.user),'status':"password didn't match"})

@csrf_exempt
def login_user(request):
    """
    This method is for user's login and authentication
    """
    #Authenticate the user
    user = authenticate(username=request.POST["username"], password=request.POST["password"])
    if user is not None:
        login(request, user)
        return redirect("/")
    else:
        return render_to_response("Home.html", {'status': "Invalid Username or password"})


@csrf_exempt
def register(request):
    """
    This method is used to register a new user.
    """
    if request.POST["password"] == request.POST["passwordAgain"]:
        user = User.objects.create_user(request.POST["username"],request.POST["email"],request.POST["password"])
        user.first_name=request.POST["firstname"]
        user.last_name=request.POST["lastname"]
        user.save()
        subscription(username= request.POST["username"],
                       follow = 'on',
                       addtack = 'on',
                       favorite = 'on').save()
        #Send email on registration
        send_mail("registered","Dude!! Welcome to the Fun World. Login to your account http://www.tackshare.com","tackshare@gmail.com",[request.POST["email"]],fail_silently="false")
        return render_to_response("Home.html", {'status': request.POST["username"]+"!! Registered Successfully! Please Login"})
    else:
        return render_to_response("Home.html", {'status': 'Your passwords didn\'t match'})

@login_required
@csrf_exempt
def create_tack(request):
    """
    This method is used to display the Create Tack form
    """
    boards = Boards.objects.filter(username=get_user(request))
    return render_to_response("CreateTack.html",{'user': str(get_user(request)),'boards':boards})

@login_required
@csrf_exempt
def create_tack_url(request):
    """
    This method is used to display the Create Tack from URL form
    """
    boards = Boards.objects.filter(username=get_user(request))
    return render_to_response("CreatetackFromUrl.html",{'user': str(get_user(request)),'boards':boards})

@login_required
@csrf_exempt
def update_dashboard(request):
    """
    This method is used to save a new board.
    """
    Boards(name=request.POST["board_name"],
           description=request.POST["board_desc"],
           privacy=request.POST["board_privacy"],
           username=get_user(request),
           ).save()
    #Redirect to home page
    return redirect("/")

@login_required
@csrf_exempt
def save_tack(request):
    """
    This method is used to save a new tack.
    """
    img_url = request.POST["img_url"]
    bookmark_url = request.POST["tack_url"]
    file_input = request.FILES.get('file')
    if request.POST["new_board"]!="":
        boardName = request.POST["new_board"]
    else:
        boardName = request.POST["ex_board"]
        enteredTags=request.POST["tags"]
    if not enteredTags:
        tagArray=[]
    else:
        #Get tags for the tack
        tagArray=[]
        tagsSplit=enteredTags.split()
        print tagsSplit
        for ts in tagsSplit:
            print ts
            tagArray.append(str(ts))
        print tagArray
        print str(tagArray)
    if file_input:
        try:
            im=Image.open(request.FILES["file"])
            tackFileType = "image"
        except IOError:
            tackFileType = "not image"
        tack_file = file_input
    elif img_url:
        r = requests.get(img_url)
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(r.content)
        img_temp.flush()
        parsed_uri=urlparse(img_url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        print domain
        tack_file = File(img_temp)
        tackFileType="fromurl"
    #Save tack details
    TackImages(file_name=request.POST["tack_name"],
               tack_file = tack_file,
               file_type = tackFileType,
               tags=tagArray,
               username=get_user(request),
               bookmark=request.POST["tack_url"],
               board=boardName
               ).save()
    #Add tack to board
    board = Boards.objects.get(name=boardName)
    tack_name = request.POST["tack_name"]
    board.tacks.append(tack_name)
    board.save()
    return redirect("/board?boardName="+boardName)

@login_required
@csrf_exempt
def url_save_tack(request):
    """
    This method is used to save a new tack.
    """
    if request.POST["new_board"]!="":
        boardname = request.POST["new_board"]
    else:
        boardName = request.POST["ex_board"]
    img_url = request.POST["tack_url"]
    print img_url
    r = requests.get(img_url)
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(r.content)
    img_temp.flush()
    parsed_uri=urlparse(img_url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    print domain
    #Save tack details
    TackImages(file_name=request.POST["tack_name"],
               tack_file = File(img_temp),
               file_type = "image",
               tags=request.POST["tags"],
               username=get_user(request),
               bookmark=request.POST["tack_url"],
               board=boardName
               ).save()
    #Add tack to board
    board = Boards.objects.get(name=boardName)
    tack_name = request.POST["tack_name"]
    board.tacks.append(tack_name)
    board.save()
    tackNames = board.tacks
    tacks = TackImages.objects.filter(file_name__in=tackNames)
    return redirect("/board?boardName="+boardName)


@login_required
@csrf_exempt
def save_board(request):
    """
    This method is used to create a new board
    """
    response_data = {}
    response_data['result']="failure"
    try:
        Boards(name=request.POST["board_name"],
                   description=request.POST["board_desc"],
                   privacy=request.POST["board_privacy"],
                   username=get_user(request),
                   ).save()
        #Return success
        response_data['result']="success"
    except:
        #Return failure
        response_data['result']="failure"
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
def create_board(request):
    return render_to_response("CreateBoard.html",{'user': str(get_user(request))})

@login_required
def show_tacks(request):
    """
    This method is used to display the tacks in a selected board.
    """
    boardName = request.GET.get('boardName')
    board = Boards.objects.get(name=boardName)
    tackNames = board.tacks
    if not board.visible_to_users:
        sharedWith="none"
    else:
        sharedWith = board.visible_to_users
    #Get all tacks in the board
    tacks = TackImages.objects.filter(file_name__in=tackNames)
    if not tacks:
        tacks = ""
    return render_to_response("BoardsHome.html",{'MEDIA_URL': settings.MEDIA_URL, 'tacks':tacks, 'boardName':boardName,'sharedWith':sharedWith})

@login_required
def display_tack(request):
    """
    This method is used to display the details of a tack.
    """
    tackName = request.GET.get('tackName')
    #Get tack details
    tacks = TackImages.objects.filter(file_name=tackName)
    tack = tacks[0]
    boards = Boards.objects.filter(username=get_user(request))
    tags = ','.join(tack.tags)
    return render_to_response("DisplayTack.html",{'MEDIA_URL': settings.MEDIA_URL, 'tack':tack, 'boards' : boards, 'tags' : tags})


@login_required
def share_board(request):
    """
    This method is used to display the Share Board form
    """
    boardName = request.GET.get('boardName')
    board = Boards.objects.get(name=boardName)
    if not board.visible_to_users:
        sharedWith="none"
    else:
        sharedWith = board.visible_to_users
    return render_to_response("ShareBoard.html",{'boardName':boardName,'sharedWith':sharedWith})

@login_required
@csrf_exempt
def unshare_board(request):
    """
    This method is used to edit the list of users a board is shared with.
    """
    boardName = request.GET.get('boardName')
    userName = request.GET.get('userName')
    board = Boards.objects.get(name=boardName)
    #Remove user from visible_to list
    board.visible_to_users.remove(userName)
    board.save()
    sharedWith = board.visible_to_users
    return render_to_response("ShareBoard.html",{'boardName':boardName,'sharedWith':sharedWith})

@login_required
@csrf_exempt
def share_with_user(request):
    """
    This method is used to share a board with a user.
    """
    shareWith = request.POST['search']
    boardName = request.POST['boardName']
    board = Boards.objects.get(name=boardName)
    #Add user name to board's list of visible users
    board.visible_to_users.append(shareWith)
    board.save()
    return redirect("/board?boardName="+boardName)

@login_required
def manage_email(request):
    """
    This method is used to display the Email Management form
    """
    subsc = subscription.objects.filter(username=get_user(request))
    print subsc.values()
    return render_to_response("ManageEmail.html",{'subscriptions':subsc})

@csrf_exempt
@login_required
def save_subscription(request):
    """
    This method is used to save the user's email preferences.
    """
    subsc=subscription.objects.filter(username = get_user(request)).update(
        follow=request.POST['onoffswitch1'],
        addtack=request.POST['onoffswitch2'],
        favorite=request.POST['onoffswitch3'])
    return redirect("/")

@csrf_exempt
@login_required
def create_tack_in_board(request):
    """
    This method is used to display the Create Tack inside Board form
    """
    return render_to_response("CreateTackInBoard.html",{'user': str(get_user(request)),'boardName':request.GET.get('boardName')})

@csrf_exempt
def search_users(request):
    """
    This method is used to search for registered users.
    """
    searchString=request.POST["search"]
    userResults=User.objects.filter(username=searchString)
    if(len(userResults)>0):
        userName=User.get_username(userResults[0])
        #Get all boards of the searched user
        publicBoards = Boards.objects.order_by('name').filter(privacy="Public",username=searchString)
        otherBoards = Boards.objects.order_by('name').filter(privacy="Private",username=searchString)
        visibleBoards = []
        for board in otherBoards:
            visibleTo = board.visible_to_users
            if str(get_user(request)) in visibleTo:
                visibleBoards.append(board)
        resultBoards = list(chain(publicBoards,visibleBoards))
        return render_to_response("DisplaySearchUser.html",{'userResult':userResults,'publicBoards':resultBoards,'userName':userName})

@csrf_exempt
def auto_complete_model(request):
    """
    This method is used for processing the auto complete option for search users.
    """
    if request.is_ajax():
        searchString=request.POST["search"]
        search_qs = User.objects.filter(username__startswith=searchString)
        print search_qs
        results = []
        for r in search_qs:
            results.append(r.username)
        print results
        return HttpResponse(json.dumps(results), content_type="application/json", status=200)


@csrf_exempt
def follow_user(request):
    """
    This method is used to display the Follow User form  and check if he/she is followed already
    """
    username=request.GET.get('userName')
    followersBoard=[]
    follower = []
    flag=False
    test2=[]
    vcount=0
    try:
        #Getting the list of followers
        followers = Followers.objects.filter(userName=get_user(request))
        follow=followers.values()
        test2=[]
        if not follow:
            flag=True
        for follower1 in follow:
            followe=follower1.values()
            print followe.pop()
            test=followe.pop()
            if not test:
                flag=True
            #Checking for duplication and adding to collection
            if test not in test2:
                test2.append(test)
        #Logic to check if already following or not
        for name in test2:
            print name
            for inner in name:
                print inner
                if username in inner:
                    vcount=vcount+1
    except:
        print "very sorry"
    print vcount
    #Check if already followed
    if vcount==0:
        print "Follow"
        flag=True
    else:
        print "Unfollow"
        flag=False
    return render_to_response("FollowUser.html",{'userName':username,'flag':flag})


@csrf_exempt
def save_follow(request):
    """
    This method is used to save the follower if not already exists and remove the follower if already exists
    """
    #Get the person to follow
    username=request.GET.get('userName')
    #Get the username of the current user
    mainuser=get_user(request)
    #Local variable declarations
    followersBoard=[]
    follower = []
    flag=False
    vcount=0
    try:
        #Getting the list of followers
        followers = Followers.objects.filter(userName=get_user(request))
        follow=followers.values()
        test2=[]
        if not follow:
            flag=True
        for follower1 in follow:
            followe=follower1.values()
            print followe.pop()
            test=followe.pop()
            if not test:
                flag=True
            #Checking for duplication and adding to collection
            if test not in test2:
                test2.append(test)
        print test2
        #Logic to check if already following or not
        for name in test2:
            print name
            for inner in name:
                print inner
                if username in inner:
                    vcount=vcount+1
                    #Getting the list of followers
                    user=Followers.objects.filter(userName=mainuser)
                    #Removing a user if already exists in the followers list
                    for u in user:
                        try:
                            print username
                            boards=Boards.objects.order_by('name').filter(username=inner)
                            for board in boards:
                                #Remove user name from board's list of visible users
                                board.visible_to_users.remove(mainuser.username)
                                board.save()
                            u.followersList.remove(inner)
                            u.save()
                        except:
                            print "Exception caught in removing the follower"
    except:
        print "Exception caught in getting the followers"
    print "out"
    print vcount
    #Add the follower to the follower list if not already exists
    if vcount==0:
        try:
            nameString = username
            if(not nameString):
                nameString = ''
            trimname = nameString.split()
            userInfo = User.objects.get(username=username)
            send_mail("New Follower","You have a new follower \""+mainuser.username+"\" Login to your account http://www.tackshare.com","tackshare@gmail.com",
                      [userInfo.email],fail_silently="false")
            user=Followers.objects.get(userName=mainuser)
            user.followersList.append(trimname)
            user.save()

        except:
            nameString = username
            if(not nameString):
                nameString = ''
            trimname = nameString.split()
            Followers(userName= get_user(request), followersList=trimname).save()
        finally:
            print username
            boards=Boards.objects.order_by('name').filter(username=username,privacy='Public')
            print boards
            for board in boards:
                #Add user name to board's list of visible users
                board.visible_to_users.append(mainuser.username)
                print board.visible_to_users
                board.save()
        print "saved!"
    done="done"
    return render_to_response("FollowUser.html",{'userName':username,'Done':done})

@csrf_exempt
def auto_board_complete(request):
    """
    This method  is used for processing the auto complete option for search boards.
    """
    if request.is_ajax():
        searchString=request.POST["search"]
        search_qs = Boards.objects.filter(Name__startswith=searchString).filter(privacy="Public")
        print search_qs
        results = []
        for r in search_qs:
            results.append(r.name)
        print results
        return HttpResponse(json.dumps(results), content_type="application/json", status=200)

@csrf_exempt
def search_boards(request):
    """
    This method is used to search for all public boards.
    """
    searchString=request.POST["search"]
    print searchString
    #Get all public boards
    board = Boards.objects.filter(name=searchString).filter(privacy="Public")
    if not board:
        searchString=""
        return render_to_response("PrivateBoardAccess.html")
    else:
        tackNames = board[0].tacks
        tacks = TackImages.objects.filter(file_name__in=tackNames)
        if not tacks:
            tacks = ""
        return render_to_response("DisplaySearchBoard.html",{'MEDIA_URL': settings.MEDIA_URL, 'tacks':tacks, 'boardName':searchString})

@csrf_exempt
def confirm_fav(request):
    """
    This method is used to mark a tack as Favorite
    """
    tackName=request.GET.get("tackName")
    boardName=request.GET.get("boardName")
    #Get tack details
    tacks = TackImages.objects.filter(file_name=tackName)
    tack = tacks[0]
    if tack.is_favorite:
        tack.is_favorite=False
    else:
        tack.is_favorite=True
    tack.save()
    return redirect("/displayTack?tackName="+tackName)


@csrf_exempt
@login_required
def edit_tack(request):
    """
    This method is used to edit/update a tack.
    """
    tackName = request.POST.get('tackName')
    img_url = request.POST["tack_url"]
    file_input = request.FILES.get('file')
    board_input = request.POST.get('ex_board')
    tacks = TackImages.objects.filter(file_name=tackName)
    tack = tacks[0]
    tagsString = request.POST.get('tags')
    if(not tagsString):
        tagsString = ''
    tack.tags = tagsString.split()
    tack.board = board_input
    if (file_input):
        tack.tack_file = file_input
    elif img_url:
        r = requests.get(img_url)
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(r.content)
        img_temp.flush()
        parsed_uri=urlparse(img_url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        print domain
        tack.tack_file = File(img_temp)
        tack.file_type="fromurl"
        tack.bookmark = domain
    #Save updated tack
    tack.save()
    return redirect("/displayTack?tackName=" + tack.file_name)

@login_required
@csrf_exempt
def edit_board_privacy(request):
    """
    This method is used to display the Edit Board privacy form.
    """
    boardName = request.GET.get('boardName')
    board = Boards.objects.get(name=boardName)
    return render_to_response("EditBoardPrivacy.html",{'board':board})

@login_required
@csrf_exempt
def change_board_privacy(request):
    """
    This method is used to edit/update a board's privacy.
    """
    boardName = request.POST['boardName']
    boardPrivacy = request.POST["board_privacy"]
    board = Boards.objects.get(name=boardName)
    board.privacy = boardPrivacy
    #Update board privacy
    board.save()
    return redirect("/board?boardName="+boardName)

@csrf_exempt
def view_favorites(request):
    """
    This method is used to display the user's favorite tacks.
    """
    tacks=TackImages.objects.filter(is_favorite=True)
    if not tacks:
        tacks = ""
    return render_to_response("FavoritesHome.html",{'MEDIA_URL': settings.MEDIA_URL,'tacks':tacks})

def display_info_screen(request):
    """
    This method is used to display the Information page.
    """
    return render_to_response("InfoScreen.html")

@csrf_exempt
def search_tags(request):
    """
    This method is used to search tacks by tags.
    """
    tackList=[]
    tacked=[]
    searchString=request.POST["search"]
    print searchString
    board=Boards.objects.filter(privacy="Public")
    if not board:
        board=""
    else:
        for b in board:
            tackList=TackImages.objects.all()
        print tackList
        if not tackList:
            tacked=""
        else:
             for tack in tackList:
                if not tack.tags:
                    print "No tags"
                else:
                    #Get tags
                    print tack.tags
                    for tag in tack.tags:
                        print tag
                        if(searchString==tag):
                            tacked.append(tack)
    if (len(tacked)==0):
        tacked=""
    return render_to_response("DisplaySeachTags.html",{'MEDIA_URL': settings.MEDIA_URL,'boardName':board,'tacks':tacked})
