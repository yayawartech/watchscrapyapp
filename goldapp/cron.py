from goldapp.models import *

import requests
from datetime import datetime, date, timedelta
import time
import pytz
import logging
import traceback
import json
from py_bcu.bcu_cotizacion import get_cotizacion


class GoldCron():

    def insert_gold_data(self):
        try:
            rate, ddate = self.get_date_rate()
        except:
            cot = get_cotizacion()
            print(cot)
            rate = cot[0]
            # return
            # gpWeight = GoldPriceWeight.objects.latest('id')
            # rate =  gpWeight.gold_price
            ddate = "2020/01/01"  # gpWeight.last_updated

        metals = self.get_date_ounce_new()

        if metals and rate and ddate:
            goldH = GoldHistory()
            goldH.date = datetime.now()
            goldH.price = metals["Gold"]
            goldH.save()

            gpWeight = GoldPriceWeight.objects.filter(pk=1).first()
            gpWeight.gold_price = rate
            gpWeight.gold_weight = metals["Gold"]
            gpWeight.platinum_weight = metals["Platinum"]
            gpWeight.silver_weight = metals["Silver"]
            gpWeight.last_updated = datetime.now()
            gpWeight.save()
            print("Data Updated Succesfully ", str(datetime.now()))

    def get_date_rate(self):
        i = 0
        while True:
            today = (date.today() - timedelta(days=i)).strftime("%d/%m/%Y")
            rate_resp = self.pull_rate_resp(today)
            rate_data = rate_resp['cotizacionesoutlist']['Cotizaciones']
            i = i+1
            if len(rate_data) > 0:
                return rate_data[0]['TCV'], today
            else:
                print("No data for date: ", today)
        return None

    def get_date_ounce(self):
        ounce_resp = self.pull_ounce_resp()
        precious_metals = ounce_resp["PreciousMetals"]["PM"]
        metals = {}
        for metal in precious_metals:
            if metal["Symbol"] == "AG":
                metals["Silver"] = metal["Bid"]
            if metal["Symbol"] == "AU":
                metals["Gold"] = metal["Bid"]
            if metal["Symbol"] == "PT":
                metals["Platinum"] = metal["Bid"]
        return metals

    def pull_ounce_resp(self):
        response = requests.get('https://proxy.kitco.com/getPM?symbol=AG,AU,PD,PT&type=json',
                                headers={'Accept-Encoding': 'gzip, deflate, br',
                                         'Accept-Language': 'en-US,en;q=0.9',
                                         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                                         'Accept': 'text/plain, /; q=0.01',
                                         'Origin': 'https://www.kitco.com',
                                         'Referer': 'https://www.kitco.com/jewelry/',
                                         'Connection': 'keep-alive'}
                                )
        return response.json()

    def get_date_ounce_new(self):
        au_resp = self.fetch_ounce_data_internal('AU')
        ag_resp = self.fetch_ounce_data_internal('AG')
        pt_resp = self.fetch_ounce_data_internal('PT')
        metals = {}
        metals['Gold'] = au_resp['Bid']
        metals['Silver'] = ag_resp['Bid']
        metals['Platinum'] = pt_resp['Bid']
        return metals

    def fetch_ounce_data_internal(self, symbol):
        timestamp = int(time.time())
        url = "https://kitco-gcdn-prod.stellate.sh/"
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Pragma": "no-cache",
            "Sec-CH-UA": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Brave\";v=\"120\"",
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": "macOS",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Sec-GPC": "1",
            "x-query-id": '{"query":"MetalFragment","variables":{"symbol":"' + symbol + '","currency":"USD","timestamp":' + str(timestamp) + '}}'
        }

        body = '{"query":"fragment MetalFragment on Metal { ID symbol currency name results { ...MetalQuoteFragment } } fragment MetalQuoteFragment on Quote { ID timestamp high low open close ask bid mid originalTime change changePercentage unit } query MetalQuote( $symbol: String! $currency: String! $timestamp: Int ) { GetMetalQuote( symbol: $symbol currency: $currency timestamp: $timestamp ) { ...MetalFragment } }","variables":{"symbol":"' + symbol + '","currency":"USD","timestamp":' + str(
            timestamp) + '}}'

        try:
            response = requests.post(url, headers=headers, data=body)
            response.raise_for_status()  # Raise an exception for non-200 status codes
            print("Response status code:", response.status_code)
            print("=>"+response.text+"<=")
            result = response.json()  # json.loads(response.text)

            if "status" not in result:
                result2 = {"status": True, "Symbol": symbol}
                result = result["data"]["GetMetalQuote"]["results"][0]
                result2["Timestamp"] = result["originalTime"]
                result2["Bid"] = round(float(result["mid"]), 2)
                result = result2

            return result

        except requests.exceptions.RequestException as e:
            return {"status": False, "error": str(e)}

    def pull_rate_resp(self, today):

        data = '{"KeyValuePairs":{"Monedas":[{"Val":"2225","Text":"DLS. USA BILLETE"}],"FechaDesde":"' + \
            today+'","FechaHasta":"'+today+'","Grupo":"2"}}'
        response = requests.get('https://www.bcu.gub.uy/_layouts/BCU.Cotizaciones/handler/CotizacionesHandler.ashx?op=getcotizaciones',
                                data=data,
                                headers={'Connection': 'keep-alive',
                                         'Pragma': 'no-cache',
                                         'Cache-Control': 'no-cache',
                                         'Accept': 'application/json, text/javascript, /; q=0.01',
                                         'X-Requested-With': 'XMLHttpRequest',
                                         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36',
                                         'Content-Type': 'application/json; charset=UTF-8',
                                         'Origin': 'https://www.bcu.gub.uy',
                                         'Sec-Fetch-Site': 'same-origin',
                                         'Sec-Fetch-Mode': 'cors',
                                         'Sec-Fetch-Dest': 'empty',
                                         'Sec-GPC': '1',
                                         'Content-Length': str(len(data)),
                                         'Host': 'www.bcu.gub.uy',
                                         'Origin': 'https://www.bcu.gub.uy',
                                         'Referer': 'https://www.bcu.gub.uy/Estadisticas-e-Indicadores/Paginas/Cotizaciones.aspx',
                                         'Accept-Language': 'en-US,en;q=0.9',
                                         'Cookie': 'WSS_FullScreenMode=false'}
                                )
        # print("\n\n\n->"+response.content+"<-\n\n")
        return response.json()


def gold_data_cron():
    goldCron = GoldCron()
    goldCron.insert_gold_data()
