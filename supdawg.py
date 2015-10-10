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

        for p in q.run():
            self.response.out.write(p.job_title)
            self.response.out.write("<br>")
            self.response.out.write(p.company)
            self.response.out.write("<br>")
            self.response.out.write(p.salary)



class MainPage(webapp2.RequestHandler):
    def get(self):
        

        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class SubmitPage(webapp2.RequestHandler):
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

routes = [
    ('/', MainPage),
    ('/enterjob', SubmitPage),
    ('/old', OldPage),
    ('/query', Query),
]


app = webapp2.WSGIApplication(routes, debug=True)
