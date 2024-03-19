import os
import subprocess
from watchapp.models import Job


class Scraper():

    def scrape(self, spider, all_urls, job):
        cwd = os.getcwd()
        try:
            PARENT_DIR = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            os.chdir(os.path.join(PARENT_DIR, "../watchscrapy"))
            # subprocess.Popen(["echo ""> ../scrapylogs/"+spider+'.txt'],shell=True)
            subprocess.Popen(
                ['touch ../scrapylogs/'+spider+'.txt'], shell=True)
            # proc = subprocess.Popen(['/watches_wwww/watchscrapyenv/bin/scrapy crawl ' + spider+'Spider -a job='+ job +' -a url='+ all_urls +' --loglevel=WARNING --logfile=../scrapylogs/'+ spider+'.txt'],shell=True)
            proc = subprocess.Popen(['scrapy crawl ' + spider+'Spider -a job=' + job + ' -a url=' +
                                    all_urls + ' --loglevel=WARNING --logfile=../scrapylogs/' + spider+'.txt'], shell=True)
            jobT = Job.objects.filter(name=job).first()
            jobT.process = proc.pid
            jobT.save()
        except subprocess.CalledProcessError as cperr:
            print("Subprocess Error while scraping" + str(cperr))
        finally:
            os.chdir(cwd)

# scrapy = Scraper()
# scrapy.scrape('antiquorum')
