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
  #add imprt of content file wrapper
from django.core.files.base import ContentFile
import connect
# Create your views here.


def home(request):
    if request.user.is_authenticated():
        tackimages = TackImages.objects.filter(username= get_user(request))
        privateBoards = Boards.objects.order_by('Name').filter(username=get_user(request),Privacy="Private")[:10]
        publicBoards = Boards.objects.order_by('Name').filter(Privacy="Public")[:10]
        return render_to_response("Dashboard.html", {'MEDIA_URL': settings.MEDIA_URL,'tackimages':tackimages,'privateBoards':privateBoards,'publicBoards':publicBoards})
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
        return render_to_response("Home.html", {'status': 'your passwords didn\'t match'})

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
        if 'board_name' in request.POST:
            Boards(Name=request.POST["board_name"],
                   Description=request.POST["board_desc"],
                   Privacy=request.POST["board_privacy"],
                   username=get_user(request),
                   ).save()
    privateBoards = Boards.objects.order_by('Name').filter(username= get_user(request),Privacy="Private")[:10]
    publicBoards = Boards.objects.order_by('Name').filter(Privacy="Public")[:10]
    #return render_to_response("Dashboard.html", {'MEDIA_URL': settings.MEDIA_URL,'privateBoards':privateBoards,'publicBoards':publicBoards})
    return redirect("/")
@login_required
@csrf_exempt
def saveTack(request):
    if request.POST["new_board"]!="":
        boardname = request.POST["new_board"]
    else:
        boardname = request.POST["ex_board"]
    TackImages(Filename=request.POST["tack_name"],
               image=request.FILES["file"],
               tags=request.POST["tags"],
               username=get_user(request),
               bookmark=request.POST["tack_url"],
               board=boardname
               ).save()
    board = Boards.objects.get(Name=boardname,username=get_user(request))
    tack_name = request.POST["tack_name"]
    board.Tacks.append(tack_name)
    board.save()
    privateBoards = Boards.objects.order_by('Name').filter(username= get_user(request),Privacy="Private")[:10]
    publicBoards = Boards.objects.order_by('Name').filter(Privacy="Public")[:10]
    tackimages = TackImages.objects.filter(username= get_user(request))
    return render_to_response("Dashboard.html", {'MEDIA_URL': settings.MEDIA_URL,'privateBoards':privateBoards,'publicBoards':publicBoards,'tacks':tackimages})
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
    privateBoards = Boards.objects.order_by('Name').filter(username= get_user(request),Privacy="Private")[:10]
    publicBoards = Boards.objects.order_by('Name').filter(Privacy="Public")[:10]
    tackimages = TackImages.objects.filter(username= get_user(request))
    return render_to_response("Dashboard.html", {'MEDIA_URL': settings.MEDIA_URL,'privateBoards':privateBoards,'publicBoards':publicBoards,'tacks':tackimages})

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
def createNewBoard(request):
    tack=TackImages(Filename=request.POST["tack_name"],
               image=request.FILES["file"],
               tags=request.POST["tags"],
               username=get_user(request),
               bookmark=request.POST["tack_url"]
               )
    return render_to_response("CreateNewBoard.html",{'user': str(get_user(request)),'tack':tack})

@login_required
def createBoard(request):
    return render_to_response("CreateBoard.html",{'user': str(get_user(request))})
@login_required
def showTacks(request):
    """
    Show tacks for a board
    """
    boardName = request.GET.get('boardName')
    board = Boards.objects.filter(Name=boardName)
    #board name must be unique
    tackNames = board[0].Tacks
    tacks = TackImages.objects.filter(Filename__in=tackNames)
    return render_to_response("BoardsHome.html",{'MEDIA_URL': settings.MEDIA_URL, 'tacks':tacks, 'boardName':boardName})
@login_required
def displayTack(request):
    tackName = request.GET.get('tackName')
    tacks = TackImages.objects.filter(Filename=tackName)
    tack = tacks[0]
    return render_to_response("DisplayTack.html",{'MEDIA_URL': settings.MEDIA_URL, 'tack':tack})
@login_required
def shareBoard(request):
    boardName = request.GET.get('boardName')
    return render_to_response("ShareBoard.html",{'boardName':boardName})
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



