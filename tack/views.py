from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from tack.models import Users, TackImages, Boards
from django.db.models import Q
from tackshare import settings
from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import connect
# Create your views here.


def home(request):
    if request.user.is_authenticated():
        tackimages = TackImages.objects.filter(username= get_user(request))
        privateBoards = Boards.objects.order_by('Name').filter(username=get_user(request),Privacy="Private")[:10]
        publicBoards = Boards.objects.order_by('Name').filter(Privacy="Public")[:10]
        return render_to_response("Dashboard.html", {'MEDIA_URL': settings.MEDIA_URL,'tackimages':tackimages,'privateBoards':privateBoards,'publicBoards':publicBoards})
    else:
        return render_to_response('home.html')


def logout_user(request):
    logout(request)
    return render_to_response('home.html')


def update_user(request):
    return render_to_response('updateprofile.html', {'firstname':User.get_full_name(request.user),'username':User.get_username(request.user)})

@csrf_exempt
def update_user_profile(request):
    if request.POST["password"] == request.POST["passwordAgain"]:
        u = User.objects.get(username__exact=str(get_user(request)))
        u.set_password(request.POST["password"])
        u.save()
        tackimages = TackImages.objects.filter(username= get_user(request))
        privateBoards = Boards.objects.order_by('Name').filter(username= get_user(request),Privacy="Private")[:10]
        publicBoards = Boards.objects.order_by('Name').filter(Privacy="Public")[:10]
        return render_to_response("Dashboard.html", {'MEDIA_URL': settings.MEDIA_URL,'tackimages':tackimages,'privateBoards':privateBoards,'publicBoards':publicBoards})
    else:
        return render_to_response('updateprofile.html', {'firstname':User.get_full_name(request.user),'username':User.get_username(request.user),'status':"password didn't match"})

@csrf_exempt
def login_user(request):
    user = authenticate(username=request.POST["username"], password=request.POST["password"])
    if user is not None:
        login(request, user)
        tackimages = TackImages.objects.filter(username= get_user(request))
        privateBoards = Boards.objects.order_by('Name').filter(username= get_user(request),Privacy="Private")[:10]
        publicBoards = Boards.objects.order_by('Name').filter(Privacy="Public")[:10]
        return render_to_response("Dashboard.html", {'MEDIA_URL': settings.MEDIA_URL,'tackimages':tackimages,'privateBoards':privateBoards,'publicBoards':publicBoards})
    else:
        return render_to_response("home.html", {'status': "Invalid Username or password"})


@csrf_exempt
def register(request):
    if request.POST["password"] == request.POST["passwordAgain"]:
        user = User.objects.create_user(request.POST["username"],request.POST["email"],request.POST["password"])
        user.first_name=request.POST["firstname"]
        user.last_name=request.POST["lastname"]
        user.save()
        return render_to_response("home.html", {'status': request.POST["username"]+"!! Registered Successfully! Please Login"})
    else:
        return render_to_response("home.html", {'status': 'your passwords didn\'t match'})


@csrf_exempt
def createTack(request):
    boards = Boards.objects.filter(username=get_user(request))
    return render_to_response("CreateTack.html",{'user': str(get_user(request)),'boards':boards})

@csrf_exempt
def update_dashboard(request):
    print "username"+str(get_user(request))
    if 'tack_name' in request.POST:
        TackImages(Filename=request.POST["tack_name"],
                   image=request.FILES["file"],
                   tags=request.POST["tags"],
                   username=get_user(request),
                   bookmark=request.POST["tack_url"],
                   board=request.POST["board"]
                   ).save()
        tackimages = TackImages.objects.filter(username= get_user(request))
        privateBoards = Boards.objects.order_by('Name').filter(username= get_user(request),Privacy="Private")[:10]
        publicBoards = Boards.objects.order_by('Name').filter(Privacy="Public")[:10]
        return render_to_response("Dashboard.html", {'MEDIA_URL': settings.MEDIA_URL,'tackimages':tackimages,'privateBoards':privateBoards,'publicBoards':publicBoards})
    else:
        Boards(Name=request.POST["board_name"],
               Description=request.POST["board_desc"],
               Privacy=request.POST["board_privacy"],
               username=get_user(request),
               ).save()
        privateBoards = Boards.objects.order_by('Name').filter(username= get_user(request),Privacy="Private")[:10]
        publicBoards = Boards.objects.order_by('Name').filter(Privacy="Public")[:10]
        return render_to_response("Dashboard.html", {'MEDIA_URL': settings.MEDIA_URL,'privateBoards':privateBoards,'publicBoards':publicBoards})

@csrf_exempt
def saveTack(request):
    TackImages(Filename=request.POST["tack_name"],
               image=request.FILES["file"],
               tags=request.POST["tags"],
               username=get_user(request),
               bookmark=request.POST["tack_url"],
               board=request.POST["board"]
               ).save()
    board = Boards.objects.filter(Name=request.POST["board"],username=get_user(request))
    board[0].Tacks.append(request.POST["tack_name"])
    privateBoards = Boards.objects.order_by('Name').filter(username= get_user(request),Privacy="Private")[:10]
    publicBoards = Boards.objects.order_by('Name').filter(Privacy="Public")[:10]
    tackimages = TackImages.objects.filter(username= get_user(request))
    return render_to_response("Dashboard.html", {'MEDIA_URL': settings.MEDIA_URL,'privateBoards':privateBoards,'publicBoards':publicBoards,'tacks':tackimages})

@csrf_exempt
def saveBoard(request):
    Boards(Name=request.POST["board_name"],
               Description=request.POST["board_desc"],
               Privacy=request.POST["board_privacy"],
               username=get_user(request),
               ).save()
    return HttpResponse()

def createNewBoard(request):
    tack=TackImages(Filename=request.POST["tack_name"],
               image=request.FILES["file"],
               tags=request.POST["tags"],
               username=get_user(request),
               bookmark=request.POST["tack_url"]
               )
    return render_to_response("CreateNewBoard.html",{'user': str(get_user(request)),'tack':tack})


def createBoard(request):
    return render_to_response("CreateBoard.html",{'user': str(get_user(request))})

def showTacks(request):
    """
    Show tacks for a board
    """
    boardName = request.GET.get('boardName')
    board = Boards.objects.filter(Name=boardName,username=get_user(request))
    #board name must be unique
    tackNames = board[0].Tacks
    tacks = TackImages.objects.filter(Filename__in=tackNames,username= get_user(request))
    return render_to_response("BoardsHome.html",{'MEDIA_URL': settings.MEDIA_URL, 'tacks':tacks})