from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from datetime import datetime
import json
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from goldapp.cron import GoldCron
from .models import *

from django.contrib.auth.decorators import login_required

from django.db import connection


@login_required
def home(request):
    template = loader.get_template('gold/home.html')

    # goldCron = GoldCron()
    # goldCron.insert_gold_data()

    gold_price_weight = GoldPriceWeight.objects.all().first()
    # Load Carat Information
    carat_gold = CaratInformation.objects.filter(key_type='gold')
    carat_silver = CaratInformation.objects.filter(key_type='silver')

    # Load Configuration
    config = Configuration.objects.all().first()

    # Load Configuration grams data
    grams_data = calculate_grams(config, gold_price_weight)

    context = {
        'carat_gold': carat_gold,
        'carat_silver': carat_silver,
        'gold_price_weight': gold_price_weight,
        'config': config,
        'grams_data': grams_data
    }
    return HttpResponse(template.render(context, request))


def fetchNow(request):
    goldCron = GoldCron()
    goldCron.insert_gold_data()
    gpw = GoldPriceWeight.objects.all().first()
    results = {}
    results['gold_price'] = gpw.gold_price
    results['gold_weight'] = gpw.gold_weight
    results['platinum_weight'] = gpw.platinum_weight
    results['silver_weight'] = gpw.silver_weight
    results['last_updated'] = gpw.last_updated.strftime(
        "%b %d, %Y, %-H:%-M %p")
    return HttpResponse(json.dumps(results), content_type='application/json')


def update_configuration(request):
    if request.method == "POST":
        config = Configuration.objects.all().first()
        if not config:
            config = Configuration()

        gold_c = request.POST.get('gold_c')
        platinum_c = request.POST.get('platinum_c')
        silver_c = request.POST.get('silver_c')
        gold_sp = request.POST.get('gold_sp')
        platinum_sp = request.POST.get('platinum_sp')
        silver_sp = request.POST.get('silver_sp')
        platinum_bp = request.POST.get('platinum_bp')

        config.gold_c = gold_c
        config.platinum_c = platinum_c
        config.silver_c = silver_c
        config.gold_sp = gold_sp
        config.silver_sp = silver_sp
        config.platinum_sp = platinum_sp
        config.platinum_bp = platinum_bp
        print(config)
        config.save()

        return redirect('/gold')


def calculate_grams(config, gold_price_weight):

    calc_data = []
    kilos = []

    # Calculating Kilos with 32.15
    gold_k = round(gold_price_weight.gold_weight * 32.15, 2)
    silver_k = round(gold_price_weight.silver_weight * 32.15, 2)
    platinum_k = round(gold_price_weight.platinum_weight * 32.15, 2)
    kilos.append(gold_k)
    kilos.append(platinum_k)
    kilos.append(silver_k)
    calc_data.append(kilos)

    purity = []
    # Calculating Purity
    gold_purity = round(gold_k * (config.gold_sp/100), 2)
    platinum_purity = round(platinum_k * (config.platinum_sp/100), 2)
    silver_purity = round(silver_k * (config.silver_sp/100), 2)
    purity.append(gold_purity)
    purity.append(platinum_purity)
    purity.append(silver_purity)
    calc_data.append(purity)

    comission = []
    # Calculating Comission
    gold_comission = round(gold_purity * (1-(config.gold_c/100)), 2)
    platinum_comission = round(
        platinum_purity * (1 - (config.platinum_c/100)), 2)
    silver_comission = round(silver_purity * (1-(config.silver_c/100)), 2)
    comission.append(gold_comission)
    comission.append(platinum_comission)
    comission.append(silver_comission)
    calc_data.append(comission)

    grams = []
    # Calculating Grams
    for i in comission:
        grams.append(round(i/1000, 2))

    calc_data.append(grams)

    return calc_data


def myajaxview(request, percentage, goldgram):
    percentage = float(percentage)
    goldgram = float(goldgram)
    coins_pre = Coin.objects.all()
    coins = []
    for old_coin in coins_pre:
        new_coin = {}
        new_coin["id"] = old_coin.pk
        new_coin["name"] = old_coin.name
        new_coin["weight"] = round(old_coin.pure_gold / old_coin.factor, 2)
        new_coin["pure_gold"] = round(old_coin.pure_gold, 3)
        new_coin["price"] = round(
            old_coin.pure_gold * goldgram * (1-(percentage/100)), 1)
        coins.append(new_coin)

    return HttpResponse(json.dumps(coins), content_type='application/json')


def gold_data(request, carat, goldgram, percentage=0):
    config = Configuration.objects.all().first()
    percentage = [0, 5, 10, 15, percentage]
    value = CaratInformation.objects.filter(key=carat).first().value

    rate = GoldPriceWeight.objects.all().first().gold_price
    # calculation
    results = {}
    for p in range(len(percentage)):
        usdollar = round(float(goldgram) * value *
                         (1-float(percentage[p])/100), 2)
        usd = round(usdollar * rate)
        results[p] = [usd, usdollar]

    value24k = float(goldgram)
    res24k = round(float(goldgram) * rate)
    results['24k'] = [res24k, value24k]
    return HttpResponse(json.dumps(results), content_type='application/json')


def platinum_data(request, platinumgram, percentage=0):
    config = Configuration.objects.all().first()
    percentage = [0, 5, 10, 15, percentage]
    platinum_bp = config.platinum_bp

    rate = GoldPriceWeight.objects.all().first().gold_price
    # calculation
    results = {}
    for p in range(len(percentage)):
        usdollar = round(float(platinumgram) * (platinum_bp/100)
                         * (1-float(percentage[p])/100), 2)
        usd = round(usdollar * rate)
        results[p] = [usd, usdollar]

    value1000 = float(platinumgram)
    res1000 = round(float(platinumgram) * rate)
    results['1000'] = [res1000, value1000]
    results['platinum_bp'] = round((platinum_bp/100) * 1000)
    return HttpResponse(json.dumps(results), content_type='application/json')


def silver_data(request, carat, silvergram, percentage=0):
    config = Configuration.objects.all().first()
    percentage = [0, 5, 10, 15, percentage]
    value = CaratInformation.objects.filter(key=carat).first().value

    rate = GoldPriceWeight.objects.all().first().gold_price
    # calculation
    results = {}
    for p in range(len(percentage)):
        usdollar = round(float(silvergram) * value *
                         (1-float(percentage[p])/100), 2)
        usd = round(usdollar * rate)
        results[p] = [usd, usdollar]

    value999 = float(silvergram)
    res999 = round(float(silvergram) * rate)
    results['999'] = [res999, value999]
    return HttpResponse(json.dumps(results), content_type='application/json')


def chart_data(request, val):
    if val == 'last3days':
        label = "Last 3 Days"
        query = '''select DATE_FORMAT(date,"%Y-%m-%d"), price as Price from goldapp_goldhistory  WHERE date >= DATE_ADD(CURDATE(), INTERVAL -3 DAY) order by date  desc;'''

    if val == "last15days":
        label = "Last 15 Days"
        query = '''select DATE_FORMAT(date,"%Y-%m-%d") as "dateN",AVG(price) as Price from goldapp_goldhistory group by DATE_FORMAT(date,"%Y-%m-%d" ) order by dateN desc limit 15;'''

    if val == "last12months":
        label = "Last 12 Months"
        query = '''SELECT concat(YEAR(date),"-",MONTH(date)) as monthyear, AVG(price) FROM goldapp_goldhistory GROUP BY monthyear order by monthyear desc limit 15;'''
    if val == "last10years":
        label = "Last 10 Years"
        query = '''select DATE_FORMAT(date,"%Y") as "year",AVG(price) as Price from goldapp_goldhistory group by DATE_FORMAT( date,"%Y") order by year desc limit 10;'''

    # calculation
    results = {}
    data = []
    # Load Chart data
    cursor = connection.cursor()

    # gold_data = cursor.execute(query)
    cursor.execute(query)
    gold_data = cursor.fetchall()

    for gold in gold_data:
        res = []
        res_date = gold[0]
        res.append(str(res_date))
        res.append(gold[1])
        data.append(res)
    data.reverse()
    results["data"] = data
    results["label"] = label
    cursor.close()
    return HttpResponse(json.dumps(results), content_type='application/json')


def test(request):
    template = loader.get_template('gold/test.html')
    return HttpResponse(template.render({}, request))
