from flask import Flask
from flask_ask import Ask, statement, question, session
import unidecode
from lxml import html
import requests


app = Flask(__name__)
ask = Ask(app, "/damage_report")

# def get_headlines():
#     user_pass_dict = {
#         'user': 'USERNAME',
#         'passwd': 'PASSWORD',
#         'api_type': 'json'
#     }
#     sess = requests.Session()
#     sess.headers.update({'User-Agent':'I am testing Alexa'})
#     sess.post('http://www.reddit.com/api/login', data=user_pass_dict)
#     time.sleep(1)
#     url = 'https://reddit.com/r/worldnews/.json?limit=10'
#     html = sess.get(url)
#     data = json.loads(html.content.decode('utf-8'))
#     titles = [unidecode.unidecode(listing['data']['title']) for listing in data['data']['children']]
#     titles = ', , , , ,'.join([i for i in titles])
#     return titles

def get_headlines():
    base_url = "https://whatthefuckjusthappenedtoday.com"
    #get most recent page
    article_url = get_most_recent_article_url(base_url)
    article_page = requests.get(article_url)
    article_tree = html.fromstring(article_page.content)
    bold_text, non_bold_text, source = get_article_text(article_tree)
    reg_text = remove_empty_string(non_bold_text)
    articles = get_article_full_text(bold_text, reg_text, source)
    return articles


def get_article_full_text(bold_text, reg_text, source):
    articles = """"""
    for item in range(len(bold_text)):
        full_text = "<p>"+source[item] + " Reports " + bold_text[item] + reg_text[item] + ".</p>"
        articles += full_text.replace("(", "") + """<break time="2.25s"/>"""
    return articles


def remove_empty_string(non_bold_text):
    reg_text = []
    for item in non_bold_text:
        if len(item) > 4:
            reg_text.append(item)
    return reg_text


def get_article_text(article_tree):
    bold_text = article_tree.xpath('//article/p/strong/text()')
    non_bold_text = article_tree.xpath('//div/main/div[2]/article/p/text()')
    source = article_tree.xpath('//p/a/text()')
    return bold_text, non_bold_text, source


def get_most_recent_article_url(base_url):
    page = requests.get(base_url)
    print(page.status_code)
    main_tree = html.fromstring(page.content)
    article_date_url = main_tree.xpath('//h2/a/@href')[0]
    # create link to most recent page and grab content
    article_url = base_url + article_date_url
    return article_url


@app.route('/')
def  homepage():
    return "hi there, how ya doing?"

@ask.launch
def start_skill():
    welcome_message = """<speak>
    Run full scan?
     </speak>"""
    return question(welcome_message)

@ask.intent("YesIntent")
def share_headlines():
    headlines = get_headlines()
    headline_msg = """<speak>
     {}
</speak>""".format(headlines)
    return statement(headline_msg)

@ask.intent("NoIntent")
def no_intent():
    bye_text = "Ok... good bye"
    return statement(bye_text)

if __name__ == '__main__':
    app.run(debug=True)
