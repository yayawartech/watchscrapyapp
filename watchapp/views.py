from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core import serializers
from django.template import loader
from watchapp.utils.scraper import Scraper
from datetime import datetime
import time
from django.db import connection
from django.db.models import Count, Sum

from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from watchapp.models import Lot, Auction, AuctionHouse, Job, Setup
import subprocess

# Create your views here.


def login(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            # correct username and password login the user
            auth.login(request, user)
            return redirect('/home')

        else:

            context = {"message": "Invalid Login Credentials"}

    template = loader.get_template('login.html')
    return HttpResponse(template.render(context, request))


def logout(request):
    auth.logout(request)
    template = loader.get_template('login.html')
    context = {"message": "You have been logged out"}
    return HttpResponse(template.render(context, request))


@login_required()
def home(request):
    template = loader.get_template('home.html')
    context = {}
    return HttpResponse(template.render(context, request))


def get_paginationRage(lots):

    big_range = lots.paginator.page_range
    small_number = lots.number-5
    if lots.paginator.page_range[0] > small_number:
        small_number = lots.paginator.page_range[0]
    big_number = lots.number+5
    if big_number < small_number+10:
        big_number = small_number+10

    if lots.paginator.page_range[-1] < big_number:
        big_number = lots.paginator.page_range[-1]

    my_range = range(small_number, big_number)
    if lots.number < 11:
        my_range = range(1, 10)  # return pag

    num_10 = int(lots.number/10)
    min_num = 1
    max_num = 10
    if int(num_10) == 0:
        min_num = 1
    else:
        min_num = min_num*10
        max_num = min_num+10
    if lots.paginator.page_range[-1] < max_num:
        max_num = lots.paginator.page_range[-1]
    print("["+str(num_10)+","+str(min_num)+","+str(max_num)+"]")
    after_range = max_num+1
    if lots.paginator.page_range[-1] <= max_num:
        after_range = -1

    return {
        'before_range': min_num-1,
        'range': range(min_num, max_num),
        'after_range': after_range,
        'count': lots.end_index()-lots.start_index()
    }


@login_required()
def index(request):
    template = loader.get_template('all.html')

    lot_list = Lot.objects.all().prefetch_related(
        "auction").order_by('auction__date').reverse()

    page = request.GET.get('page', 1)

    paginator = Paginator(lot_list, 10)
    try:
        lots = paginator.page(page)
    except PageNotAnInteger:
        lots = paginator.page(1)
    except EmptyPage:
        lots = paginator.page(paginator.num_pages)
    auction_houses = AuctionHouse.objects.all()
    pagination = get_paginationRage(lots)
    context = {
        'auction_houses': auction_houses,
        'lots': lots,
        'pagination_range': pagination
    }

    return HttpResponse(template.render(context, request))


@login_required()
def lot_details(request, lot):
    template = loader.get_template('lot_details.html')

    lot = Lot.objects.filter(pk=lot).prefetch_related("auction").first()
    lot.images = lot.get_images()
    context = {
        'lot': lot,
    }

    return HttpResponse(template.render(context, request))


@login_required()
def advsearch(request):
    lots = []
    search = request.POST.get('search')
    option = request.POST.get('advsearch')
    auction_house = request.POST.get('auction_house')
    title = request.POST.get('title')
    description = request.POST.get('description')
    from_date = to_date = ""
    any_filter = False
    if request.method == 'GET':
        option = request.GET.get('option')
        search = request.GET.get('search')
        auction_house = request.GET.get('auction_house')
        title = request.GET.get('title')
        description = request.GET.get('description')

    url_parameters = ""

    lot_list = Lot.objects
    # ACA FILTRO POR FECHAS
    from_date = None
    to_date = None
    if option == "date":
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        if request.method == 'GET':
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_date')
            print(from_date)
    if from_date and to_date:
        lot_list = Lot.objects.all().prefetch_related(
            "auction").filter(auction__date__range=[from_date, to_date])
        print(lot_list)
        any_filter = True
        url_parameters = url_parameters + "&from_date="+from_date+"&to_date="+to_date
    # ACA FILTRO POR MONEDA
    if option == "currency":
        lot_list = Lot.objects.filter(
            lot_currency__icontains=search).prefetch_related("auction")
        any_filter = True
    # ACA FILTRO POR PRECIO
    if option == "sold_price":
        lot_list = Lot.objects.filter(
            sold_price__icontains=search).prefetch_related("auction")
        any_filter = True
    # ACA FILTRO POR ESTIMADO
    if option == "estimate_min_price":
        lot_list = Lot.objects.filter(
            estimate_min_price__icontains=search).prefetch_related("auction")
        any_filter = True
    if option == "estimate_max_price":
        lot_list = Lot.objects.filter(
            estimate_max_price__icontains=search).prefetch_related("auction")
        any_filter = True
    # ACA FILTRO SOLO POR TITULO
    if title != None and title != '':
        tokens = title.split(" ")
        result = lot_list.filter(title__icontains=tokens[0])
        if len(tokens) > 0:
            for i in range(1, len(tokens)):
                result = result.filter(title__icontains=tokens[i])
        lot_list = result.prefetch_related("auction")
        any_filter = True
        url_parameters = url_parameters + "&title="+title
    # ACA FILTRO SOLO POR DESCRIPCION
    if description != None and description != '':
        tokens = description.split(" ")
        result = lot_list.filter(description__icontains=tokens[0])
        if len(tokens) > 1:
            for i in range(1, len(tokens)):
                result = result.filter(description__icontains=tokens[i])
        lot_list = result.prefetch_related("auction")
        any_filter = True
        url_parameters = url_parameters + "&description="+description
    # if option == "auction_house":
    #    lot_list = Lot.objects.all().prefetch_related("auction").filter(auction__auction_house__name__icontains=search)
    # ACA FILTRO POR DESCRIPCION Y TITULO A LA VEZ
    if search != None and search != '':
        tokens = search.split(" ")
        result = lot_list.filter(search_all__icontains=tokens[0])
        if len(tokens) > 1:
            for i in range(1, len(tokens)):
                result = result.filter(search_all__icontains=tokens[i])
        lot_list = result.prefetch_related("auction")
        any_filter = True
        url_parameters = url_parameters + "&search="+search

    # ACA FILTRO POR CASA DE REMATE
    if auction_house != None and auction_house.isdigit():
        lot_list = lot_list.filter(auction__auction_house_id=auction_house)
        any_filter = True
        url_parameters = url_parameters + "&auction_house="+auction_house
        if auction_house.isdigit():
            auction_house = int(auction_house)
    # SI NO HAY FILTROS
    if not any_filter:
        lot_list = lot_list.all()

    lot_list = lot_list.order_by('auction__date').reverse()
    page = request.GET.get('page', 1)
    # print(page)

    paginator = Paginator(lot_list, 25)
    try:
        lots = paginator.page(page)
    except PageNotAnInteger:
        lots = paginator.page(1)
    except EmptyPage:
        lots = paginator.page(paginator.num_pages)

    pagination = get_paginationRage(lots)
    auction_houses = AuctionHouse.objects.all()
    template = loader.get_template('all.html')
    context = {
        'auction_houses': auction_houses,
        'auction_house': auction_house,
        'lots': lots,
        'search': search,
        'selected_option': option,
        'from_date': from_date,
        'to_date': to_date,
        'title': title,
        'description': description,
        'url_parameters': url_parameters,
        'pagination_range': pagination
    }

    return HttpResponse(template.render(context, request))


@login_required()
def allJobs(request):
    template = loader.get_template('jobs/jobs.html')

    job_list = Job.objects.filter(status__icontains="In Progress").prefetch_related(
        "auction_house").order_by('id')

    page = request.GET.get('page', 1)

    paginator = Paginator(job_list, 100)
    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)

    context = {
        'jobs': jobs,
    }

    return HttpResponse(template.render(context, request))


@login_required()
def completedJobs(request):
    template = loader.get_template('jobs/jobs-complete.html')

    job_list = Job.objects.filter(status__icontains="Completed").prefetch_related(
        "auction_house").order_by('id')

    page = request.GET.get('page', 1)

    paginator = Paginator(job_list, 100)
    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)

    context = {
        'jobs': jobs,
    }

    return HttpResponse(template.render(context, request))


@login_required()
def failedJobs(request):
    template = loader.get_template('jobs/jobs-failed.html')

    job_list = Job.objects.filter(status__icontains="Failed").prefetch_related(
        "auction_house").order_by('id')

    page = request.GET.get('page', 1)

    paginator = Paginator(job_list, 100)
    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)

    context = {
        'jobs': jobs,
    }

    return HttpResponse(template.render(context, request))


@login_required()
def addJobs(request):
    template = loader.get_template('jobs/jobs-add.html')
    return HttpResponse(template.render({}, request))


@login_required()
def createJobs(request):
    if request.method == 'POST':
        auction_house = request.POST.get('auction_house')
        urls = request.POST.get('urls')

        auction_house_id = auction_house.split("-")[1]
        auction_house_name = auction_house.split("-")[0]

        input_urls = urls.replace("\r\n", ",")
        cur_time = int(time.time())
        job_name = auction_house_name.upper() + str(cur_time)

        auct = AuctionHouse()
        auct.id = auction_house_id

        job = Job()
        job.name = job_name
        job.auction_house = auct
        job.start_time = datetime.now()
        job.urls = input_urls
        job.status = "In Progress"
        ret = job.save()
        if job.pk:
            scrape = Scraper()
            scrape.scrape(auction_house_name.lower(), input_urls, job.name)

        return redirect('/jobs/')
    else:
        return redirect('jobs/add')


@login_required()
def setup(request):
    setup_obj = Setup.objects.first()
    chromedriver = ""
    if setup_obj:
        chromedriver = setup_obj.chromedriver

    if request.method == 'POST':
        chromedriver = request.POST.get("chromedriver")

        if setup_obj:
            setup = Setup(pk=1)
        else:
            setup = Setup()
        setup.chromedriver = chromedriver
        setup.save()

    template = loader.get_template('setup/setup.html')
    context = {
        'chromedriver': chromedriver,
    }

    return HttpResponse(template.render(context, request))


@login_required()
def job_details(request, job):
    template = loader.get_template('jobs/job-details.html')

    job = Job.objects.filter(pk=job).prefetch_related("auction_house").first()
    lot_counts = []
    urls = job.urls
    for url in urls.split(","):
        counts = {}
        lot = Lot.objects.all().prefetch_related(
            "auction").filter(auction__url=url.strip())
        # MB - fix where the URL was not processed
        try:
            counts["actual_lots"] = lot[0].auction.actual_lots
            counts["fetched_lots"] = lot.count()
            counts["auction"] = lot[0].auction.name
            counts["house"] = lot[0].auction.auction_house.name
            counts["url"] = url
        except IndexError:
            counts["actual_lots"] = 0
            counts["fetched_lots"] = 0
            counts["auction"] = 'Error Processing URL'
            counts["house"] = 'Error Processing URL'
            counts["url"] = url

        lot_counts.append(counts)

    context = {
        'lots': lot_counts,
        'job': job.name
    }

    return HttpResponse(template.render(context, request))


@login_required()
def job_progress_details(request, job):
    template = loader.get_template('jobs/job-details-progress.html')
    job = Job.objects.filter(pk=job).prefetch_related("auction_house").first()
    urls = job.urls.split(",")
    total_count = len(urls)

    with connection.cursor() as cursor:
        sql = '''
                SELECT
                wa.id,
                wa.name,
                wa.url,
                wa.actual_lots,
                ifnull(wld.lots_processed,0) as processed_lots,
                round(ifnull(wld.lots_processed*1.0,0) / wa.actual_lots * 100.0,2) as percentage
                FROM watchapp_auction wa LEFT JOIN
                (
                SELECT
                auction_id,
                job,
                COUNT(*) as lots_processed
                FROM watchapp_lot wl WHERE wl.job = '%s' 
                GROUP BY auction_id, job
                ) wld ON wa.id = wld.auction_id 
                WHERE wa.job = '%s'
        ''' % (job.name, job.name)
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        auctions = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

        total_lots = 0
        processed_lots = 0
        for auc in auctions:
            total_lots = total_lots + auc['actual_lots']
            processed_lots = processed_lots + auc['processed_lots']

        lots_percentage = 0
        if processed_lots > 0 and total_lots > 0:
            lots_percentage = round(processed_lots*1.0 / total_lots * 100, 2)

    processed_count = len(auctions)
    context = {
        'auctions': auctions,
        'total_n': total_count,
        'processed_n': processed_count,
        'job': job,
        'total_lots': total_lots,
        'processed_lots': processed_lots,
        'lots_percentage': lots_percentage
    }

    return HttpResponse(template.render(context, request))


@login_required()
def job_kill(request, job):
    jobD = Job.objects.filter(pk=job).first()
    print(job)
    subprocess.Popen(['kill -9 '+str(jobD.process)], shell=True)
    jobD.delete()
    return redirect('/jobs/')


@login_required()
def job_run(request, job):

    jobD = Job.objects.filter(pk=job).prefetch_related("auction_house").first()
    subprocess.Popen(['kill -9 '+str(jobD.process)], shell=True)

    cur_time = int(time.time())
    job_name = jobD.auction_house.name.upper() + str(cur_time)

    jobD.name = job_name
    jobD.start_time = datetime.now()
    jobD.end_time = None
    jobD.status = "In Progress"
    jobD.save()

    scrape = Scraper()
    scrape.scrape(jobD.auction_house.name.lower(), jobD.urls, job_name)

    return redirect('/jobs/')


@login_required()
def houses(request):
    template = loader.get_template('houses/auction_houses.html')
    all_house_info = []
    lots = Lot.objects.values(
        'auction__auction_house', 'auction__auction_house__name').annotate(Count('lot_number'))
    lot_info = {}
    for lot in lots:
        lot_info[lot['auction__auction_house']] = lot['lot_number__count']

    auc_houses = AuctionHouse.objects.values('name', 'pk').annotate(
        Count('auction__name'), Sum('auction__actual_lots'))
    for auc_house in auc_houses:
        auc_house_info = {}
        auc_house_info["id"] = auc_house["pk"]
        auc_house_info["name"] = auc_house["name"]
        auc_house_info["total_auctions"] = auc_house["auction__name__count"]
        auc_house_info["actual_lots"] = auc_house["auction__actual_lots__sum"]
        auc_house_info["processed_lots"] = lot_info.get(auc_house["pk"])
        all_house_info.append(auc_house_info)

    context = {
        'houses': all_house_info,
    }

    return HttpResponse(template.render(context, request))


@login_required()
def house_details(request, house):
    template = loader.get_template('houses/auction.html')

    auctions_list = Auction.objects.filter(auction_house=house).annotate(
        Count('lot')).order_by('date').reverse()
    auction_house = AuctionHouse.objects.filter(pk=house).first()
    page = request.GET.get('page', 1)

    paginator = Paginator(auctions_list, 225)
    try:
        auctions = paginator.page(page)
    except PageNotAnInteger:
        auctions = paginator.page(1)
    except EmptyPage:
        auctions = paginator.page(paginator.num_pages)

    context = {
        'auctions': auctions,
        'auction_house': auction_house.name
    }

    return HttpResponse(template.render(context, request))


@login_required()
def auction_run(request, auction):

    auction = Auction.objects.filter(
        pk=auction).prefetch_related('auction_house').first()
    url = auction.url

    cur_time = int(time.time())
    job_name = auction.auction_house.name.upper() + str(cur_time)

    job = Job()
    job.name = job_name
    job.auction_house = auction.auction_house
    job.start_time = datetime.now()
    job.urls = url
    job.status = "In Progress"
    ret = job.save()
    if job.pk:
        scrape = Scraper()
        scrape.scrape(auction.auction_house.name.lower(), url, job.name)
    return redirect('/jobs/')


@login_required()
def rolex_year(request):
    template = loader.get_template('rolex_year.html')
    context = {}
    return HttpResponse(template.render(context, request))
