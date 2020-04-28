#########################################
##### Name: Ruiyang Chang           #####
##### Uniqname: ruiyangc            #####
##### SI507 WN20 Final Project      #####
#########################################

import json
import requests
import secrets # file that contains my API key
import sqlite3
import plotly.graph_objs as go
import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

MOVIES_CACHE_FILENAME = "movies_cache.json"
MOVIES_CACHE_DICT = {}

class Movie:
    '''a movie

    Instance Attributes
    -------------------
    id: string
        the id of the movie
    
    title: string
        the title of the movie

    release_date: string
        the release data of the movie

    genre_ids: string
        the string that contains the genres of that movie

    overview: string
        the overview of the movie
    '''
    def __init__(self, id, title, genre_ids, release_date, overview):
        self.id = id
        self.title = title
        self.genre_ids = genre_ids
        self.release_date = release_date
        self.overview = overview

    def info(self):
        '''Returns a string representation of itself
        Parameters
        ----------
        none

        Returns
        -------
        string
            <title> (<release_date>): <overview>
        '''
        #return "<<" + str(self.title) + ">>" + " (" + str(self.release_date) + "): " + str(self.overview)
        # TEST: change the info to be shorter
        return "<<" + str(self.title) + ">>" + " (" + str(self.release_date) + ") " + str(self.genre_ids)

    def toJSON(self):
        '''Returns a json representation of itself
        Parameters
        ----------
        none

        Returns
        -------
        string
            the json formate of the instance
        '''
        return json.dumps(self, default=vars, 
            sort_keys=True, indent=0)

def open_cache(file_name):
    ''' Opens the cache file if it exists and loads the content into
    the dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(file_name, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict, file_name):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(file_name,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def get_movie_from_tmdb(year, page_num):
    '''Make a list of movie instances within a year from The Movie Database.
        use recursion to get every page of the results.
    
    Parameters
    ----------
    year: string
        the year user want to search for movie

    page_num: int
        the page number to search JSON
    
    Returns
    -------
    list
        a list of movie instances
    '''
    movie_list = []
    # use API to get JSON response
    baseurl = "https://api.themoviedb.org/3/discover/movie?api_key=" + secrets.TMDB_API_KEY + "&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=true&vote_average.gte=8.5" + "&page=" + str(page_num) + "&year="
    # print(">>>TEST " + baseurl + year) # TEST
    response = requests.get(baseurl + year)
    json = response.json()
    # print(json) # TEST
    # build movie instance for current page result
    result_list = json["results"]
    for result in result_list:
        # print(">>>TEST: title = " + result["title"])
        # get the instance's id, title, release_date, genre_ids, overview
        id = result["id"]
        title = result["title"]
        release_date = result["release_date"]
        # change the list a string (if there are more than one, only get the first gnere of the movie)
        if len(result["genre_ids"]) > 0:
            genre_ids = str(result["genre_ids"][0])
        else:
            genre_ids = "0" # genre not available
        # for id in result["genre_ids"]:
        #    genre_ids = genre_ids + str(id) + ";"
        overview = result["overview"]
        movie = Movie(id=id, title=title, release_date=release_date, genre_ids=genre_ids, overview=overview)
        movie_list.append(movie)
    # print(">>>TEST list countain" + str(len(movie_list)) + "elements") # TEST

    # find the total number of pages of search results
    total_page_num = json["total_pages"]
    # print(">>>TEST Total page = " + str(total_page_num)) # TEST
    # set total page number to 3 to test recursion
    # total_page_num = 3
    # use recursion to get the rest of pages
    if (page_num < total_page_num):
        page_num += 1
        movie_list_rest = get_movie_from_tmdb(year, page_num)
        movie_list.extend(movie_list_rest)
    # TEST INSTANCE!!!!!!!
    # count = 0
    # for movie in movie_list:
    #     count += 1
    #     print(movie.info())
    # print (">>>TEST there are " + str(count) + " elements in movie_list.")
    return movie_list

def prepare_database():
    '''Use API to search for movies recorded 2016-2020 and load data into database
    '''
    # create database for movies
    conn = sqlite3.connect("movies.sqlite")
    cur = conn.cursor()
    # create the Movies table
    create_movies = '''
        CREATE TABLE IF NOT EXISTS "Movies" (
            "Id"        TEXT PRIMARY KEY UNIQUE,
            "Title"  TEXT NOT NULL,
            "GenreId" TEXT,
            "ReleaseData"  TEXT NOT NULL,
            "Overview"    TEXT
        );
    '''
    # create the Genre table
    create_genres = '''
        CREATE TABLE IF NOT EXISTS "Genres" (
            "Id"        TEXT PRIMARY KEY UNIQUE,
            "Name"  TEXT NOT NULL
        );
    '''
    print(">>> Creating Database Movie & Genre Tables")
    cur.execute(create_movies)
    cur.execute(create_genres)
    # insert genres
    # insert_genres = '''
    #     INSERT INTO Genres
    #     VALUES (?, ?)
    # '''
    # genre_list = [
    #     ["28", "Action"],
    #     ["12", "Adventure"],
    #     ["16", "Animation"],
    #     ["35", "Comedy"],
    #     ["80", "Crime"],
    #     ["99", "Documentary"],
    #     ["18", "Drama"],
    #     ["10751", "Family"],
    #     ["14", "Fantasy"],
    #     ["36", "History"],
    #     ["27", "Horror"],
    #     ["10402", "Music"],
    #     ["9648", "Mystery"],
    #     ["10749", "Romance"],
    #     ["878", "Science Fiction"],
    #     ["10770", "TV Movie"],
    #     ["53", "Thriller"],
    #     ["10752", "War"],
    #     ["37", "Western"]
    # ]
    # for genre in genre_list:
    #     cur.execute(insert_genres, genre)
    # insert_undefined = '''
    #     INSERT INTO Genres
    #     VALUES (?, ?)
    # '''
    # undefined = ["0", "Undefined"]
    # cur.execute(insert_undefined, undefined)
    conn.commit()

    # get movies between 2016 to 2020
    year = 2016
    while year <= 2020:
        print(">>> Getting Movies of the year " + str(year) + "...")
        movies_list = []
        # chiech if that year's movies have been cached
        MOVIES_CACHE_DICT = open_cache(MOVIES_CACHE_FILENAME)
        if str(year) in MOVIES_CACHE_DICT.keys():
            print(">>> Using Movies Cache")
            movies_list_json = MOVIES_CACHE_DICT[str(year)]
            # change json formate back to movie instance
            for movie_json in movies_list_json:
                id_start = movie_json.find("id\": \"") + 6
                id_end = movie_json.find("\",", id_start)
                id = movie_json[id_start: id_end]

                title_start = movie_json.find("\"title\": \"") + 10
                title_end = movie_json.find("\"\n", title_start)
                title = movie_json[title_start: title_end]

                genre_ids_start = movie_json.find("\"genre_ids\": \"") + 14
                genre_ids_end = movie_json.find("\"", genre_ids_start)
                genre_ids = movie_json[genre_ids_start: genre_ids_end]

                release_date_start = movie_json.find("\"release_date\": \"") + 17
                release_date_end = movie_json.find("\",", release_date_start)
                release_date = movie_json[release_date_start: release_date_end]

                overview_start = movie_json.find("\"overview\": \"") + 13
                overview_end = movie_json.find("\",", overview_start)
                overview = movie_json[overview_start: overview_end]

                movie = Movie(id=id, title=title, genre_ids=genre_ids, release_date=release_date, overview=overview)
                movies_list.append(movie)
        else:
            print(">>> Fetching...")
            # rerquest and also write cache for movies
            movies_list = get_movie_from_tmdb(str(year), 1)
            # change instance to json formate for caching
            movies_list_json = []
            for movie in movies_list:
                movie_json = movie.toJSON()
                movies_list_json.append(movie_json)
            MOVIES_CACHE_DICT[year] = movies_list_json
            save_cache(MOVIES_CACHE_DICT, MOVIES_CACHE_FILENAME)
            # write movies into database
            insert_movies = '''
                INSERT or REPLACE INTO Movies
                VALUES (?, ?, ?, ?, ?)
            '''
            for movie in movies_list:
                data_list = [movie.id, movie.title, movie.genre_ids, movie.release_date, movie.overview]
                cur.execute(insert_movies, data_list)
            conn.commit()

        # TEST: Print the movie instance
        print("-" *40)
        count = 0
        for movie in movies_list:
            count += 1
            # print(movie.info()) 
        print (">>>TEST there are " + str(count) + " movies in the year " + str(year) + ".")
        print("-" *40)
        year += 1

def count_genre(year_chart):
    '''Use Plotly to create bar chart for the movie distribution of the year user enters

    Parameters
    ----------
    year_chart: string
        The year to count movie genre
    
    Returns
    -------
    dict
        a dict, key = genres, value = number of movies
    '''
    # inite genre dict
    genre_count_dict = {    
        "Action": 0,
        "Adventure": 0,
        "Animation": 0,
        "Comedy": 0,
        "Crime": 0,
        "Documentary": 0,
        "Drama": 0,
        "Family": 0,
        "Fantasy": 0,
        "History": 0,
        "Horror": 0,
        "Music": 0,
        "Mystery": 0,
        "Romance": 0,
        "Science Fiction": 0,
        "TV Movie": 0,
        "Thriller": 0,
        "War": 0,
        "Western": 0,
        "Undefined": 0
    }
    # access movies of that year from database
    conn = sqlite3.connect("movies.sqlite")
    cur = conn.cursor()
    # learn from stackoverflow.com/questions/3105249/python-sqlite-parameter-substitution-with-wildcards-in-like
    cur.execute("SELECT Movies.Id, Title, ReleaseData, GenreId, Name FROM Movies JOIN Genres ON Movies.GenreId=Genres.Id WHERE ReleaseData like ?", ('%'+str(year_chart)+'%',))
    # TEST query and join
    # for row in cur:
    #     print(row)
    # count genre

    for row in cur:
        # print(">>>TEST movie genre is: " + row[4])
        # print(">>> TEST genre number is: " + str(genre_count_dict[row[4]]))
        genre_count_dict[row[4]] = genre_count_dict[row[4]] + 1

    # xvals = []
    # yvals = []
    # movie_count = 0
    # for genre in genre_count_dict:
    #     # print(">>>TEST Genre " + str(genre) + ": " + str(genre_count_dict[genre]))
    #     xvals.append(genre)
    #     yvals.append(genre_count_dict[genre])
    #     movie_count += genre_count_dict[genre]
    
    # data_canada = px.data.gapminder().query("country == 'Canada'")
    # fig = px.bar(data_canada, x='year', y='pop')

    # data = px.data.gapminder()
    # data_canada = data[data.country == 'Canada']
    # fig = px.bar(data_canada, x='year', y='pop',
    #             hover_data=['lifeExp', 'gdpPercap'], color='lifeExp',
    #             labels={'pop':'population of Canada'}, height=400)

    # bar_data = go.Bar(x=xvals, y=yvals)
    # basic_layout = go.Layout(title="Movie Distribution in the Year " + str(year_chart) + " (" + str(movie_count) + " Movies Iíncluded)")
    # fig = go.Figure(data=bar_data, layout=basic_layout)

    # fig = px.bar(x=xvals, y=yvals, 
    #         title="Movie Distribution in the Year " + str(year_chart) + " (" + str(movie_count) + " Movies Included)",
    #         labels={'y':'Number of Movies', 'x':"Movie Genres"}, height=600, width=800)

    # print(">>> Opening Chart in Broswer...")
    # fig.show()
    conn.close()

    return genre_count_dict


###########################################################
#                   Dash Interface
###########################################################

# learning from https://dash.plotly.com/layout & https://dash.plotly.com/basic-callbacks
    
# initial Dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'white': '#FFFFFF'
}

# prepare the database
prepare_database()

# call funciton to get bar chart of the year 2020
genre_count_dict = count_genre(str(2020))
# xvals, yvals and movie_count will be used for generating bar charts
xvals = []
yvals = []
movie_count = 0
for genre in genre_count_dict:
    xvals.append(genre)
    yvals.append(genre_count_dict[genre])
    movie_count += genre_count_dict[genre]
# # Test
# print(">>>TEST")
# print(xvals)
# print(yvals)
# print(">> TEST movie_count = " + str(movie_count))

# create the interface
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    # main H1
    html.H1(
        children='SI507 WN2020 Final Project',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'padding-top': 30
        }
    ),
    # H3
    html.H3(
        children='Movie Genre Distribution of the Year',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    # interface discription
     html.Div(children='Try different year and see the movie genre distributions.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    # dropdown menu for user to select year
    html.Div(
        dcc.Dropdown(
            id="year_dropdown", 
            options=[
                {'label': '2016', 'value': '2016'},
                {'label': '2017', 'value': '2017'},
                {'label': '2018', 'value': '2018'},
                {'label': '2019', 'value': '2019'},
                {'label': '2020', 'value': '2020'},
            ],
            value=2020,
        ),
        style={'display':'blocl', 'width':'10%', 'margin-left':'45%','padding-top': 30, 'padding-bottom': 10
    }),
    # indicate which year user are choosing
    html.Div(id='dropdown_test',
        style={
        'textAlign': 'center',
        'color': colors['text'], 'padding-top': 60,
        'font-size': '24px'
    }),
    # bar chart TEST
    # dcc.Graph(
    #     id='example-graph-2',
    #     figure={
    #         'data': [
    #             {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
    #             {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
    #         ],
    #         'layout': {
    #             'plot_bgcolor': colors['background'],
    #             'paper_bgcolor': colors['background'],
    #             'font': {
    #                 'color': colors['text']}
    #             }
    #         }, style={
    #             'display':'blocl', 'width':'50%', 'margin-left':'25%', 'padding-bottom': 30
    # }),
    # movie bar chart
    dcc.Graph(
        id="year_bar",
        figure={
            'data': [
                {'x': xvals, 'y': yvals, 'type': 'bar', "xaxis": "Genres", "yaxis": "Number of Movies"}
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']},
                "xaxis1": {
                    'title':'Movie Genres',
                    "gridcolor": colors['text']
                },
                "yaxis1": {
                    'title':'Number of Movies',
                    "gridcolor": colors['text'],
                }
            }
        }, style={
                'display':'blocl', 'width':'60%', 'margin-left':'20%', 'padding-bottom': 30
    }),

    html.Div(children='Ruiyang Chang (ruiyangc@umich.edu)', style={
        'textAlign': 'center',
        'color': colors['text'], 'padding-bottom': 120
    })
])

@app.callback(
    [dash.dependencies.Output('dropdown_test', 'children'),
    dash.dependencies.Output('year_bar', 'figure')],
    [dash.dependencies.Input('year_dropdown', 'value')]
)

# def update_text(value):
#     '''Update the text base on dropdown menu input
    
#     Parameters
#     ----------
#     value: string
#         The year input
    
#     Returns
#     -------
#     String
#         Text information
#     '''
#     # call funciton to get bar chart of the year 2020
#     genre_count_dict = count_genre(str(value))
#     # xvals, yvals and movie_count will be used for generating bar charts
#     movie_count = 0
#     for genre in genre_count_dict:
#         movie_count += genre_count_dict[genre]
#     return 'You have selected the year {}, with {} movies included.'.format(value, movie_count)

def update_chart(value):
    '''Update the text and bar chart base on dropdown menu input
    
    Parameters
    ----------
    value: string
        The year input

    Returns
    -------
    [children, figure]
    '''
    # call funciton to get bar chart of the year 2020
    genre_count_dict = count_genre(str(value))
    # xvals, yvals and movie_count will be used for generating bar charts
    xvals = []
    yvals = []
    movie_count = 0
    for genre in genre_count_dict:
        xvals.append(genre)
        yvals.append(genre_count_dict[genre])
        movie_count += genre_count_dict[genre]
    children = 'You have selected the year {}, with {} movies included.'.format(value, movie_count)
    figure = {
        'data': [{'x': xvals, 'y': yvals, 'type': 'bar', "xaxis": "Genres", "yaxis": "Number of Movies"}],
        'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {'color': colors['text']},
                'transition': {'duration': 500},
                "xaxis1": {
                    'title':'Movie Genres',
                    "gridcolor": colors['text']
                },
                "yaxis1": {
                    'title':'Number of Movies',
                    "gridcolor": colors['text'],
                }
            } 
        }
    return [children, figure]

if __name__ == "__main__":
    app.run_server(debug=True)
    
    

