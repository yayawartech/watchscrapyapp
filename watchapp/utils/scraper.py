import os
import subprocess
from WatchInfo.settings import DEBUG
from watchapp.models import Job


class Scraper():

    def scrape(self, spider, all_urls, job):
        cwd = os.getcwd()
        try:
            PARENT_DIR = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            os.chdir(os.path.join(PARENT_DIR, "../watchscrapy"))
            subprocess.Popen(['touch', f'../scrapylogs/{spider}.txt'])
            if DEBUG:
                command = [
                    'scrapy', 'crawl', f'{spider}Spider',
                    '-a', f'job={job}',
                    '-a', f'url={all_urls}',
                    '--loglevel=WARNING',
                    '--logfile=../scrapylogs/' + f'{spider}.txt'
                ]
            else:
                command = [
                    '/home/ubuntu/watchscrapyapp/venv/bin/scrapy', 'crawl', f'{spider}Spider',
                    '-a', f'job={job}',
                    '-a', f'url={all_urls}',
                    '--loglevel=WARNING',
                    '--logfile=../scrapylogs/' + f'{spider}.txt'
                ]

            proc = subprocess.Popen(command)

            jobT = Job.objects.filter(name=job).first()
            jobT.process = proc.pid
            jobT.save()
        except subprocess.CalledProcessError as cperr:
            print("Subprocess Error while scraping: " + str(cperr))
        finally:
            os.chdir(cwd)
