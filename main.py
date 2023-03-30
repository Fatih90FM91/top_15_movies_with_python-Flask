from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


# app = Flask(__name__)
# app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
# Bootstrap(app)


movie_original_title = []
movie_year = []
movie_titles_years = []


# print(movie_json['results']['original_title'])

# for item in movie_json['results']:
#     print(item['original_title'])

app = Flask(__name__)
with app.app_context():
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new-books-collection.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SECRET_KEY'] = 'i love it'
    Bootstrap(app)
    db = SQLAlchemy(app)

    # db.create_all()

    # db.init_app(app)

app.app_context().push()


#CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Movie {self.title} id:{self.id}>'

db.drop_all() # BIG Chance for solution....
db.create_all()

######Edit Rating and Review class####

class MovieForm(FlaskForm):
    review = StringField(label='Your new Review', validators=[DataRequired()])
    rating = StringField(label='Your Rating', validators=[DataRequired()])

    submit = SubmitField(label='submit')


######MOVIE title class####

class MovieTitleForm(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired()])

    submit = SubmitField(label='submit')



new_movie = Movie(
        title="Phone Booth",
        year=2002,
        description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
        rating=7.3,
        ranking=1,
        review="My favourite character was the caller.",
        img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    )
if db.session.query(Movie).filter_by(title='Phone Booth').count() < 1:
        db.session.add(new_movie)
        db.session.commit()


@app.route("/")
def home():


    all_movies = db.session.query(Movie).order_by(Movie.rating.desc()).all()
    # print(all_movies.description) db.session.query(Movie).all()
    result = [items.rating for items in all_movies]
    print(result)

    # query = db.session.query(Movie).order_by(Movie.rating.desc()).all()
    # print(query['rating'])
    # query.order_by(Movie.y_index.desc())  # desc


    return render_template("index.html", movies=all_movies)


@app.route("/edit/<id>", methods=['GET', 'POST'])
def edit(id):

    form = MovieForm()

    if form.validate_on_submit():

        movie_to_update = Movie.query.get(id)
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()

        return redirect('/')


    return render_template("edit.html", form=form)


@app.route('/<id>')
def delete(id):

    movie_to_delete = Movie.query.get(id)
    db.session.delete(movie_to_delete)
    db.session.commit()

    return redirect('/')


@app.route('/add', methods=['GET', 'POST'])
def add():

    form = MovieTitleForm()
    if form.validate_on_submit():
       print(form.title.data)

       response = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key=aeb7738957e59aa0e2b3a9dd75e57423&query={form.title.data}')

       # print(response.json())
       movie_json = response.json()

       movie_title = [item['original_title'] for item in movie_json['results']]
       movie_year = [item['release_date'] for item in movie_json['results']]

       movie_titles_years = movie_json['results']
       print(movie_titles_years)

       print(movie_title)
       print(movie_year)




       return render_template("select.html", movie_details=movie_titles_years )


    return render_template("add.html", form=form)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def select(id):
    #https://api.themoviedb.org/3/movie/{movie_id}?api_key=<<api_key>>&language=en-US
    print(id)
    if id:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{id}?api_key=aeb7738957e59aa0e2b3a9dd75e57423')
        movie_json = response.json()
        # movie_titles_years = movie_json['results']
        print(movie_json)

        new_movie = Movie(
            title=f"{movie_json['original_title']}",
            year=2002,
            description=f"{movie_json['overview']}",
            rating=6.7,
            ranking=10,
            review="My favourite character was the caller.",
            img_url=f"https://image.tmdb.org/t/p/w500/{movie_json['poster_path']}"
        )
        if db.session.query(Movie).filter_by(title=f"{movie_json['original_title']}").count() < 1:
            db.session.add(new_movie)
            db.session.commit()

        all_movies = db.session.query(Movie).all()
        # print(all_movies.description)
        result = [items for items in all_movies]
        print(result)

        form = MovieForm()

        if form.validate_on_submit():
            movie_to_update = Movie.query.filter_by(title=f"{movie_json['original_title']}").first()
            movie_to_update.rating = form.rating.data
            movie_to_update.review = form.review.data
            db.session.commit()

            return redirect('/')



        return render_template("edit.html", form=form)










    return render_template("/select.html")










if __name__ == '__main__':
    app.run(debug=True)
