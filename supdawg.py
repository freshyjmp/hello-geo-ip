import os
import urllib
import urllib2
import datetime
import webapp2
import jinja2
import json
from google.appengine.api import urlfetch
from google.appengine.ext import db

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Job(db.Model):
    job_title = db.StringProperty()
    company = db.StringProperty()
    start_date = db.DateProperty()
    end_date = db.DateProperty()
    current = db.BooleanProperty()
    salary = db.FloatProperty()
    exempt = db.BooleanProperty()

class OldPage(webapp2.RequestHandler):
    def get(self):
        user_ip = os.environ["REMOTE_ADDR"]
        req = urllib2.Request('https://telize.com/geoip/' + user_ip)
        result = json.load(urllib2.urlopen(req))
        template_values = {
            'user_ip': os.environ["REMOTE_ADDR"],
            'isp': result['isp'],
            'lat': result['latitude'],
            'lon': result['longitude'],
        }
        template = JINJA_ENVIRONMENT.get_template('old_index.html')
        self.response.write(template.render(template_values))

class Query(webapp2.RequestHandler):
    def get(self):
        q = Job.all()
        joblist = []
        for p in q.run():
            self.response.out.write(p.key())
            row = {
              'job_title': p.job_title,
              'company': p.company,
              'salary': p.salary,
              'current': p.current,
              'start_date': p.start_date,
              'exempt': p.exempt 
            }
            joblist.append(row.copy())
        self.response.out.write(joblist)


class MainPage(webapp2.RequestHandler):
    def get(self):
        q = Job.all()
        joblist = []
        for p in q.run():
            row = {
              'key': p.key(),
              'job_title': p.job_title,
              'company': p.company,
              'salary': p.salary,
              'current': p.current,
              'start_date': p.start_date,
              'exempt': p.exempt }
            joblist.append(row.copy())

        template_values = { 'jlist': joblist }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class CreatePage(webapp2.RequestHandler):
    def post(self):
        ex = True
        cur = False
        if self.request.get('exempt') == "Hourly":
            ex = False
        if self.request.get('checkbox') == "checked":
            cur = True

        sdate = datetime.datetime.strptime(self.request.get('start_date'), "%Y-%m-%d")
        sdate = sdate.replace(hour=0, minute=0, second=0, microsecond=0)

        # self.response.out.write( self.request.get('job_title'))
        # self.response.out.write( self.request.get('company'))
        # self.response.out.write( cur)
        # self.response.out.write( self.request.get('salary'))
        # self.response.out.write( ex)

        job = Job(job_title = self.request.get('job_title'),
            company = self.request.get('company'),
            start_date = sdate.date(),
            current = cur,
            salary = float(self.request.get('salary')),
            exempt = ex )
        job.put()

class UpdatePage(webapp2.RequestHandler):
    def get(self):
        get_values = self.request.GET
        key_value = self.request.GET['key']
        k = db.Key(encoded=key_value)
        job = db.get(k)
        if job is None:
            self.response.out.write("No Job Entity found for that ID!")
        else:
            isCurrent = ""
            isSalaried = ""
            isHourly = ""
            if job.current == True:
                isCurrent = "checked"
            else:
                isCurrent = "derp"

            if job.exempt == True:
                isSalaried = "checked"
            else:
                isHourly == "checked"

            template_values = {
              'key' : key_value,
              'job_title': job.job_title,
              'company': job.company,
              'salary': job.salary,
              'current': isCurrent,
              'start_date': job.start_date,
              'exempt_s': isSalaried,
              'exempt_h': isHourly,
            }
            template = JINJA_ENVIRONMENT.get_template('edit.html')
            self.response.write(template.render(template_values))
    
    def post(self):
        ex = True
        cur = False
        if self.request.get('exempt') == "Hourly":
            ex = False
        if self.request.get('checkbox') == "checked":
            cur = True

        sdate = datetime.datetime.strptime(self.request.get('start_date'), "%Y-%m-%d")
        sdate = sdate.replace(hour=0, minute=0, second=0, microsecond=0)

        key_value = self.request.get('key')
        k = db.Key(encoded=key_value)

        job = Job(
            key = k,
            job_title = self.request.get('job_title'),
            company = self.request.get('company'),
            start_date = sdate.date(),
            current = cur,
            salary = float(self.request.get('salary')),
            exempt = ex )
        job.put()


routes = [
    ('/', MainPage),
    ('/createjob', CreatePage),
    ('/updatejob', UpdatePage),
    ('/old', OldPage),
    ('/query', Query),
]


app = webapp2.WSGIApplication(routes, debug=True)
