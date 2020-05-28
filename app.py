from flask import Flask                     # Use Flask Web Framework to visualise the content
from redis import Redis, RedisError         # Redis is used for the visits counter
import datetime                             # Used to show the actual time
import os                                   # Used for the env variable (name)
import socket                               # Needed to evaluate your hostname
from prometheus_flask_exporter import PrometheusMetrics, Gauge

# Connect to the Redis Database
# This is not successful (and not needed) at the beginning of the tutorial
redis = Redis(
    host=os.getenv("REDIS_ADDR", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    socket_connect_timeout=2,
    socket_timeout=2
)

# The follwing lines are needed to create a Flask application. We won't dive deeper here.
# If you want to know more, head over to https://pythonhow.com/how-a-flask-app-works/
app = Flask(__name__)

metrics = PrometheusMetrics(app)
g = Gauge("visit_counter", "Our custom visit counter")

@app.route("/")
def hello():
    # The visits counter will increase the db value everytime it is called
    try:
        visits = redis.incr("counter")
        g.set(float(visits))
    # Instead of throwing an error, we will show the string below when we cannot connect to redis
    # so the program does not termintate when redis is not available
    except RedisError as error:
        app.logger.warning(error)
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    # get the actual time
    now = datetime.datetime.now()
    # format the time in Year-Month-Day Hour:Minute:Seconds
    t_now = now.strftime("%Y-%m-%d %H:%M:%S")

    # This is the HTML you see when the app is running and you open the web page
    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> {hostname}<br/>" \
           "<b>Actual time:</b> {t_now}<br/>" \
           "<b>Visits:</b> {visits}<br/>"

    # Allocate the right values to the respective variables
    return html.format(
        name=os.getenv("NAME", "world"),
        hostname=socket.gethostname(),
        visits=visits,
        t_now=t_now
    )

# This is the application entry point
if __name__ == "__main__":
    # here we are going to run the the application, listen on every IP address of the host and
    # port 8088
    app.run(host='0.0.0.0', port=8088)
