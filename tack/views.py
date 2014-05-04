from asyncore import write
import json
from django.contrib.auth.decorators import login_required
from django.core.files.temp import NamedTemporaryFile
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import requests
from tack.models import Users, TackImages, Boards, subscription
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

  #add imprt of content file wrapper
from django.core.files.base import ContentFile
import connect
# Create your views here.


def home(request):
    if request.user.is_authenticated():
        whoami = get_user(request)
        yourBoards = Boards.objects.order_by('Name').filter(username=whoami)[:10]
        if not yourBoards:
            yourBoards = "None"
        otherBoards = Boards.objects.order_by('Name').filter(~Q(username = whoami))
        visibleBoards = []
        for board in otherBoards:
            visibleTo = board.VisibleToUsers
            if str(whoami) in visibleTo:
                visibleBoards.append(board)
        if not visibleBoards:
            visibleBoards = "None"
        return render_to_response("Dashboard.html", {'MEDIA_URL': settings.MEDIA_URL,'yourBoards':yourBoards,'otherBoards':visibleBoards})
        # privateBoards = Boards.objects.order_by('Name').filter(username=get_user(request),Privacy="Private")[:10]
        # publicBoards = Boards.objects.order_by('Name').filter(Privacy="Public")[:10]
        # return render_to_response("Dashboard.html", {'MEDIA_URL': settings.MEDIA_URL,'tackimages':tackimages,'privateBoards':privateBoards,'publicBoards':publicBoards})
    else:
        return render_to_response('Home.html')

@login_required
def logout_user(request):
    logout(request)
    return render_to_response('Home.html')

@login_required
def update_user(request):
    return render_to_response('updateprofile.html', {'firstname':User.get_full_name(request.user),'username':User.get_username(request.user)})

@login_required
@csrf_exempt
def update_user_profile(request):
    if request.POST["password"] == request.POST["passwordAgain"]:
        u = User.objects.get(username__exact=str(get_user(request)))
        u.set_password(request.POST["password"])
        u.save()
        return redirect("/")
    else:
        return render_to_response('updateprofile.html', {'firstname':User.get_full_name(request.user),'username':User.get_username(request.user),'status':"password didn't match"})

@csrf_exempt
def login_user(request):
    user = authenticate(username=request.POST["username"], password=request.POST["password"])
    if user is not None:
        login(request, user)
        return redirect("/")
    else:
        return render_to_response("Home.html", {'status': "Invalid Username or password"})


@csrf_exempt
def register(request):
    if request.POST["password"] == request.POST["passwordAgain"]:
        user = User.objects.create_user(request.POST["username"],request.POST["email"],request.POST["password"])
        user.first_name=request.POST["firstname"]
        user.last_name=request.POST["lastname"]
        user.save()
        subscription(username= request.POST["username"],
                       follow = 'on',
                       addtack = 'on',
                       favorite = 'on').save()
        send_mail("registered","Dude!! Welcome to the Fun World. Login to your account http://www.tackshare.com","tackshare@gmail.com",[request.POST["email"]],fail_silently="false")
        return render_to_response("Home.html", {'status': request.POST["username"]+"!! Registered Successfully! Please Login"})
    else:
        return render_to_response("Home.html", {'status': 'Your passwords didn\'t match'})

@login_required
@csrf_exempt
def createTack(request):
    boards = Boards.objects.filter(username=get_user(request))
    return render_to_response("CreateTack.html",{'user': str(get_user(request)),'boards':boards})

@login_required
@csrf_exempt
def createTackUrl(request):
    boards = Boards.objects.filter(username=get_user(request))
    return render_to_response("CreatetackFromUrl.html",{'user': str(get_user(request)),'boards':boards})

@login_required
@csrf_exempt
def update_dashboard(request):
    Boards(Name=request.POST["board_name"],
           Description=request.POST["board_desc"],
           Privacy=request.POST["board_privacy"],
           username=get_user(request),
           ).save()
    return redirect("/")

@login_required
@csrf_exempt
def saveTack(request):
    if request.POST["new_board"]!="":
        boardName = request.POST["new_board"]
    else:
        boardName = request.POST["ex_board"]
    try:
        im=Image.open(request.FILES["file"])
        tackFileType = "image"
    except IOError:
        tackFileType = "not image"
    TackImages(Filename=request.POST["tack_name"],
               tackFile = request.FILES["file"],
               fileType = tackFileType,
               tags=request.POST["tags"],
               username=get_user(request),
               bookmark=request.POST["tack_url"],
               board=boardName

               ).save()
    board = Boards.objects.get(Name=boardName)
    tack_name = request.POST["tack_name"]
    board.Tacks.append(tack_name)
    board.save()
    tackNames = board.Tacks
    tacks = TackImages.objects.filter(Filename__in=tackNames)
    return redirect("/board?boardName="+boardName)

@login_required
@csrf_exempt
def UrlsaveTack(request):
    if request.POST["new_board"]!="":
        boardname = request.POST["new_board"]
    else:
        boardname = request.POST["ex_board"]
    img_url = request.POST["tack_url"]
    print img_url
    #content = ContentFile(urllib2.urlopen(img_url).read())
    #print content
    r = requests.get(img_url)

    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(r.content)
    img_temp.flush()
    parsed_uri=urlparse(img_url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    print domain
    TackImages(Filename=request.POST["tack_name"],
               image=File(img_temp),
               tags=request.POST["tags"],
               username=get_user(request),
               bookmark=domain,
               board=boardname
               ).save()
    board = Boards.objects.get(Name=boardname,username=get_user(request))
    tack_name = request.POST["tack_name"]
    board.Tacks.append(tack_name)
    board.save()
    return redirect("/")

@login_required
@csrf_exempt
def saveBoard(request):
    response_data = {}
    response_data['result']="failure"
    try:
        Boards(Name=request.POST["board_name"],
                   Description=request.POST["board_desc"],
                   Privacy=request.POST["board_privacy"],
                   username=get_user(request),
                   ).save()
        response_data['result']="success"
    except:
        response_data['result']="failure"
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
def createBoard(request):
    return render_to_response("CreateBoard.html",{'user': str(get_user(request))})

@login_required
def showTacks(request):
    """
    Show tacks for a board
    """
    boardName = request.GET.get('boardName')
    board = Boards.objects.get(Name=boardName)
    #board name must be unique
    tackNames = board.Tacks
    if not board.VisibleToUsers:
        sharedWith="none"
    else:
        sharedWith = board.VisibleToUsers
    tacks = TackImages.objects.filter(Filename__in=tackNames)
    if not tacks:
        tacks = ""
    return render_to_response("BoardsHome.html",{'MEDIA_URL': settings.MEDIA_URL, 'tacks':tacks, 'boardName':boardName,'sharedWith':sharedWith})

@login_required
def displayTack(request):
    tackName = request.GET.get('tackName')
    tacks = TackImages.objects.filter(Filename=tackName)
    tack = tacks[0]

    #boards and tags Added by Sindhu. boards are needed for the Edit tack.
    # Also, transform the tags before sending it to Edit Tack.
    boards = Boards.objects.filter(username=get_user(request))
    tags = ''.join(tack.tags)
    return render_to_response("DisplayTack.html",{'MEDIA_URL': settings.MEDIA_URL, 'tack':tack, 'boards' : boards, 'tags' : tags})


@login_required
def shareBoard(request):
    boardName = request.GET.get('boardName')
    board = Boards.objects.get(Name=boardName)
    if not board.VisibleToUsers:
        sharedWith="none"
    else:
        sharedWith = board.VisibleToUsers
    return render_to_response("ShareBoard.html",{'boardName':boardName,'sharedWith':sharedWith})

@login_required
@csrf_exempt
def unShareBoard(request):
    boardName = request.GET.get('boardName')
    userName = request.GET.get('userName')
    board = Boards.objects.get(Name=boardName)
    board.VisibleToUsers.remove(userName)
    board.save()
    sharedWith = board.VisibleToUsers
    return render_to_response("ShareBoard.html",{'boardName':boardName,'sharedWith':sharedWith})

@login_required
@csrf_exempt
def shareWithUser(request):
    shareWith = request.POST['search']
    boardName = request.POST['boardName']
    board = Boards.objects.get(Name=boardName)
    board.VisibleToUsers.append(shareWith)
    board.save()
    tackNames = board.Tacks
    tacks = TackImages.objects.filter(Filename__in=tackNames)
    return redirect("/board?boardName="+boardName)

@login_required
def manageemail(request):
    subsc = subscription.objects.filter(username=get_user(request))
    print subsc.values()
    return render_to_response("ManageEmail.html",{'subscriptions':subsc})

@csrf_exempt
@login_required
def savesubscription(request):
    subsc=subscription.objects.filter(username = get_user(request)).update(
        follow=request.POST['onoffswitch1'],
        addtack=request.POST['onoffswitch2'],
        favorite=request.POST['onoffswitch3'])
    return redirect("/")

@csrf_exempt
@login_required
def createTackInBoard(request):
    return render_to_response("CreateTackInBoard.html",{'user': str(get_user(request)),'boardName':request.GET.get('boardName')})

@csrf_exempt
def searchUsers(request):
    searchString=request.POST["search"]
    print searchString
    userResults=User.objects.filter(username=searchString)
    if(len(userResults)>0):
        userName=User.get_username(userResults[0])
        publicBoards = Boards.objects.order_by('Name').filter(Privacy="Public")[:10]
        return render_to_response("DisplaySearchUser.html",{'userResult':userResults,'publicBoards':publicBoards,'userName':userName})

@csrf_exempt
def autocompleteModel(request):
   # search_qs = User.objects.filter(username__startswith=request.REQUEST['search'])
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
def FollowUser(request):
    userName=request.GET.get('userName')
    print userName
    return render_to_response("FollowUser.html",{'userName':userName})

@csrf_exempt
def AutoBoardComplete(request):
    if request.is_ajax():
        searchString=request.POST["search"]
        search_qs = Boards.objects.filter(Name__startswith=searchString).filter(Privacy="Public")
        print search_qs
        results = []
        for r in search_qs:
            results.append(r.Name)
        print results
        return HttpResponse(json.dumps(results), content_type="application/json", status=200)

@csrf_exempt
def searchBoards(request):
    searchString=request.POST["search"]
    print searchString
    board = Boards.objects.filter(Name=searchString).filter(Privacy="Public")
    if not board:
        searchString=""
        return render_to_response("PrivateBoardAccess.html")
    else:
        tackNames = board.Tacks
        tacks = TackImages.objects.filter(Filename__in=tackNames)
        if not tacks:
            tacks = ""
        return render_to_response("DisplaySearchBoard.html",{'MEDIA_URL': settings.MEDIA_URL, 'tacks':tacks, 'boardName':searchString})

@csrf_exempt
def confirmFav(request):
    tackName=request.GET.get("tackName")
    boardName=request.GET.get("boardName")
    print tackName
    print boardName
    tacks = TackImages.objects.filter(Filename=tackName)
    tack = tacks[0]
    if(tack.isFavorite):
        tack.isFavorite=False
    else:
        tack.isFavorite=True
    tack.save()
    print "Marked Favourite"
    print tack.fileType
    boards = Boards.objects.filter(username=get_user(request))
    tags = ''.join(tack.tags)
    return render_to_response("DisplayTack.html",{'MEDIA_URL': settings.MEDIA_URL, 'tack':tack, 'boards' : boards, 'tags' : tags})


@csrf_exempt
@login_required
def editTack(request):
    tackName = request.POST.get('tackName')
    img_url = request.POST["tack_url"]
    file_input = request.FILES.get('file')
    board_input = request.POST.get('ex_board')

#    print >>sys.stderr, str(tackName)


    tacks = TackImages.objects.filter(Filename=tackName)
    tack = tacks[0]
    tagsString = request.POST.get('tags')
    if(not tagsString):
        tagsString = ''
    tack.tags = tagsString.split()

    tack.board = board_input


    #Check if file input is given, then use it. Otherwise, check the url. If both are provided, file input gets precedence.
    if (file_input):
        tack.tackFile = file_input
    elif img_url:
        r = requests.get(img_url)
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(r.content)
        img_temp.flush()
        parsed_uri=urlparse(img_url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        print domain
        tack.tackFile = File(img_temp)
        tack.bookmark = domain


    tack.save()
    return redirect("/displayTack?tackName=" + tack.Filename)


@login_required
@csrf_exempt
def videoTest(request):
    return render_to_response("VideoTest.html",{'MEDIA_URL': settings.MEDIA_URL})

@login_required
@csrf_exempt
def displayVideo (request):
    try:
        im=Image.open(request.FILES["file"])
        p = "image"
    except IOError:
        p = "not image"
    return render_to_response("VideoTest2.html",{"p":p})

@login_required
@csrf_exempt
def editBoardPrivacy(request):
    boardName = request.GET.get('boardName')
    board = Boards.objects.get(Name=boardName)
    return render_to_response("EditBoardPrivacy.html",{'board':board})

@login_required
@csrf_exempt
def changeBoardPrivacy(request):
    boardName = request.POST['boardName']
    boardPrivacy = request.POST["board_privacy"]
    board = Boards.objects.get(Name=boardName)
    board.Privacy = boardPrivacy
    board.save()
    return redirect("/board?boardName="+boardName)

def sidebarTest(request):
    return render_to_response("SidebarTest.html")

@csrf_exempt
def viewFavorites(request):
    tacks=TackImages.objects.filter(isFavorite=True)
    if not tacks:
        tacks=""
    return render_to_response("FavoritesHome.html",{'tacks':tacks})
