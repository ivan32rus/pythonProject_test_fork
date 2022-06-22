from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

import pyshorteners
from pyshorturl import TinyUrlcom

import requests

from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span, ZipkinAttrs, Kind, zipkin_client_span
from py_zipkin.request_helpers import create_http_headers
from py_zipkin.encoding import Encoding


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://test:111@db/testdb'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Reurlshort(db.Model):
    __tablename__ = 'urlshort'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False, unique=True)
    short = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Reurlshort %r>' % self.id


def short_links(link_s):
    s = pyshorteners.Shortener(timeout=5)

    try:
        return s.tinyurl.short(link_s)
    except:
        return "error"


def default_handler(encoded_span):
    body = encoded_span

    # decoded = _V1ThriftDecoder.decode_spans(encoded_span)
    app.logger.debug("body %s", body)

    # return requests.post(
    #     "http://zipkin:9411/api/v1/spans",
    #     data=body,
    #     headers={'Content-Type': 'application/x-thrift'},
    # )

    return requests.post(
        "http://51.250.105.11:9411/api/v2/spans",
        data=body,
        headers={'Content-Type': 'application/json'},
    )


@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

#@app.route('/')
#@app.route('/home')
#def index():
#    return render_template("urlshort.html")


#@zipkin_client_span(service_name='web', span_name='web_01')
#def call_api_02():
#    headers = create_http_headers()
#    requests.get('http://51.250.105.11:5000/', headers=headers)
#    return 'OK'


@app.route('/')
@app.route('/home')
def index():
    with zipkin_span(
        service_name='web',
        span_name='web_01',
        transport_handler=default_handler,
        port=5000,
        sample_rate=100,
        encoding=Encoding.V2_JSON
    ):
        urlshorts()
        urlshort()
        #call_api_02()
    #return 'OK', 200
    return render_template("urlshort.html")


@zipkin_client_span(service_name='web', span_name='urlshort')
@app.route('/urlshort', methods=['POST', 'GET'])
def urlshort():
    if request.method == 'POST':
        url = request.form['url']
        reshort = short_links(url)
        reurlshort = Reurlshort(url=url, short=reshort)

        try:
            db.session.add(reurlshort)
            db.session.commit()
            headers = create_http_headers()
            requests.get('http://51.250.105.11:5000/urlshort', headers=headers)

            return redirect('/urlshorts')
        except:
            return "ошибка re URLShort!"

    else:
        return render_template("urlshort.html")


@zipkin_client_span(service_name='web', span_name='urlshorts')
@app.route('/urlshorts')
def urlshorts():
    articles = Reurlshort.query.order_by(Reurlshort.id.desc()).all()
    return render_template("urlshorts.html", articles=articles)


@app.route('/urlshorts/<int:id>')
def urlshort_detail(id):
    article = Reurlshort.query.get(id)
    return render_template("urlshort_detail.html", article=article)


@app.route('/urlshorts/<int:id>/del')
def urlshort_delete(id):
    article = Reurlshort.query.get_or_404(id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/urlshorts')
    except:
        return "При ссылки возникла ошибка!"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', threaded=True)
