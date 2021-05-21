from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

import pyshorteners
from pyshorturl import TinyUrlcom

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


@app.route('/')
@app.route('/home')
def index():
    return render_template("urlshort.html")


@app.route('/urlshort', methods=['POST', 'GET'])
def urlshort():
    if request.method == 'POST':
        url = request.form['url']
        reshort = short_links(url)
        reurlshort = Reurlshort(url=url, short=reshort)

        try:
            db.session.add(reurlshort)
            db.session.commit()
            return redirect('/urlshorts')
        except:
            return "ошибка re URLShort!"

    else:
        return render_template("urlshort.html")


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
    app.run(debug=True)