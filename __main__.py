import os
import requests
import json
from bs4 import BeautifulSoup

if "DEFINING VARIABLES IN CURRENT NAMESPACE":
    reviewstring = "https://www.rottentomatoes.com/m/{movie}/reviews/?page={page}&type={reviewer_type}&sort="
    reviewpage = reviewstring.format
    CRITIC, TOP_CRITIC, USER = range(3)
    html_param = {}
    tag = {}
    html_param[CRITIC] = ""
    tag[CRITIC] = "critic"
    html_param[TOP_CRITIC] = "top_critics"
    tag[TOP_CRITIC] = "topCritic"
    html_param[USER] = "user"
    tag[USER] = "user"
    MAX_REVIEW_PAGES = range(1)
    bug = {}
    bug[MAX_REVIEW_PAGES] = 51

def exceptionlessRequestsGet(*args, **kwargs):
    r = None 
    while r is None:
        try:
            r = requests.get(*args, **kwargs)
        except (requests.exceptions.TooManyRedirects,
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout
                ) as e:
            print("Found exception: {e}".format(e=e))
    return r

class User:

    def __init__(self, link, name):
        self.link = link
        self.name = name
        if name == "":
            self.name = None

    @staticmethod
    def fromJson(json):
        return User(**json)

    def jsonify(self):
        return {'link':self.link, 'name':self.name}

    def __str__(self):
        return "_{name}_({link})".format(name=self.name, link=self.link)

class Review:

    def __init__(self, user, opinion, time, text, page):
        self.user = user
        self.opinion = opinion
        if opinion == [] or opinion == "":
            self.opinion = None
        self.time = time
        self.text = text
        self.page = page

    @staticmethod
    def fromJson(json):
        return Review(**json)

    def jsonify(self):
        return {'user':self.user.jsonify(), 'opinion':self.opinion, 'time':self.time,
               'text':self.text, 'page':self.page}

    def __str__(self):
        return"[{page}] {user}@{time}: {opinion}\n{text}".format(
                                                                    user = self.user,
                                                                    opinion=self.opinion,
                                                                    time=self.time,
                                                                    text=self.text,
                                                                    page=self.page)
    def __repr__(self):
        return self.__str__()

class Scrapper:

    @staticmethod
    def movie_exists(movie):
        url = reviewpage(movie=movie,reviewer_type=html_param[critic_review], page=1)
        r = requests.get(url)
        return r.status_code != 404

    @staticmethod
    def last_page(movie, reviewer_type):
        page = 0
        for jump in [300,100,25,10,1]:
            code = 0
            while code != 404:
                page += jump
                url = reviewpage(movie=movie,reviewer_type=html_param[reviewer_type], page=page)
                r = requests.get(url)
                code = r.status_code
            page -= jump
        page = min(page, bug[MAX_REVIEW_PAGES])
        return page

    @staticmethod
    def soup_user_review(soup, page):
        reviews = []
        for row_rtr in soup.find_all("div", class_="row review_table_row"):
            user = User(link=row_rtr.a["href"],
                        name=row_rtr.find("a", class_="bold unstyled articleLink").span.contents[-1].strip())
            score = row_rtr.find("div", class_="scoreWrapper").span["class"]
            score = score[0] if len(score) > 0 else score
            time = row_rtr.find("span", class_="fr small subtle").contents[-1]
            text = row_rtr.find("div", class_="user_review").contents[-1].strip()
            review = Review(user, score, time, text, page)
            reviews.append(review)
        return reviews

    @staticmethod
    def soup_critic_review(soup, page):
        reviews = []
        for row_rtr in soup.find_all("div", class_="row review_table_row"):
            user = User(link=row_rtr.a["href"],
                        name=row_rtr.find("a", class_="unstyled bold articleLink").contents[-1].strip())
            fresh = row_rtr.find("div", class_="review_icon icon small fresh")
            rotten = row_rtr.find("div", class_="review_icon icon small rotten")
            assert(fresh or rotten)
            score ="Fresh" if fresh else "Rotten"
            time = row_rtr.find("div", class_="review_date subtle small").contents[-1]
            text  = row_rtr.find("div", class_="the_review").contents[-1].strip()
            review = Review(user, score, time, text, page)
            reviews.append(review)
        return reviews

    @staticmethod
    def soup_all_reviews_by_type(movie, reviewer_type):
        reviews = []
        max_page = Scrapper.last_page(movie, reviewer_type)
        if reviewer_type in [USER]:
            soup_review = Scrapper.soup_user_review
        elif reviewer_type in [TOP_CRITIC,CRITIC]:
            soup_review = Scrapper.soup_critic_review
        else:
            soup_review = None
        for page in range(max_page):
            url = reviewpage(movie=movie, reviewer_type=html_param[reviewer_type], page=page+1)
            print(url )
            r = exceptionlessRequestsGet(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            new_reviews = soup_review(soup=soup, page=page+1)
            reviews += new_reviews
        return reviews

class Filemanager:

    @staticmethod
    def make_filename(movie, tag):
        return "{}.{}.CannedSoup".format(movie,tag)

    @staticmethod
    def reviews_to_jsonfile(reviews, movie, tag):
        filename = Filemanager.make_filename(movie,tag)
        data = list(map(lambda r: r.jsonify(), reviews))
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

    @staticmethod
    def jsonfile_to_reviews(movie, tag):
        filename = Filemanager.make_filename(movie, tag)
        with open(filename, 'r') as infile:
            data = json.load(infile)
        if type(data) is not list:
            data = [data]
        return list(map(lambda j: Review.fromJson(j), data))

def get_reviews(movie, reviewer_type):
    if not os.path.exists(Filemanager.make_filename(movie, tag[reviewer_type])):
        soup = Scrapper.soup_all_reviews_by_type(movie, reviewer_type)
        Filemanager.reviews_to_jsonfile(soup, movie, tag[reviewer_type])
    return Filemanager.jsonfile_to_reviews(movie,tag[reviewer_type])