from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import io
from collections import Counter
import string
import os

app = Flask(__name__, static_folder='frontend/build', static_url_path='/')
CORS(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///articles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def get_word_frequencies(text, max_words=100):
    # Remove punctuation and convert to lowercase
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Split into words
    words = text.split()
    
    # Common stop words without requiring nltk
    stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 
                 "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 
                 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 
                 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
                 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 
                 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 
                 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 
                 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 
                 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 
                 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 
                 'then', 'once'}
    
    words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Get word frequencies
    word_freq = Counter(words)
    
    # Get the top words
    top_words = word_freq.most_common(max_words)
    
    # Convert to format needed for react-wordcloud
    return [{"text": word, "value": count} for word, count in top_words]

def clean_text(text):
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

def scrape_articles():
    url = "https://www.whitehouse.gov/briefing-room/"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    
    article_list = []
    for article in articles:
        h2_tag = article.find('h2')
        if h2_tag and h2_tag.find('a'):
            a_tag = h2_tag.find('a')
            title = a_tag.text.strip()
            link = a_tag['href']
            article_list.append({'title': title, 'link': link})
    
    return article_list

def get_article_content(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    content_section = soup.select_one('#content > article > section')
    
    if not content_section:
        return None
    
    for script_or_style in content_section(['script', 'style']):
        script_or_style.decompose()
    
    text = content_section.get_text(separator=' ', strip=True)
    return clean_text(text)

@app.route('/api/articles', methods=['GET'])
def get_articles():
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return jsonify([{
        'id': article.id,
        'title': article.title,
        'link': article.link,
        'word_frequencies': get_word_frequencies(article.content) if article.content else [],
        'created_at': article.created_at.isoformat()
    } for article in articles])

@app.route('/api/articles/<int:article_id>/download', methods=['GET'])
def download_article(article_id):
    article = Article.query.get_or_404(article_id)
    
    # Create a text file in memory
    file_content = f"Title: {article.title}\n"
    file_content += f"Date: {article.created_at.strftime('%Y-%m-%d')}\n"
    file_content += f"Source: {article.link}\n\n"
    file_content += article.content
    
    # Convert to bytes
    bytes_io = io.BytesIO(file_content.encode('utf-8'))
    
    # Generate safe filename
    safe_title = re.sub(r'[^\w\s-]', '', article.title)
    safe_title = re.sub(r'\s+', '_', safe_title)
    filename = f"{safe_title}_{article.created_at.strftime('%Y%m%d')}.txt"
    
    return send_file(
        bytes_io,
        mimetype='text/plain',
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/refresh', methods=['POST'])
def refresh_articles():
    articles = scrape_articles()
    for article_data in articles[:5]:  # Only process the 5 most recent articles
        existing_article = Article.query.filter_by(link=article_data['link']).first()
        if not existing_article:
            content = get_article_content(article_data['link'])
            if content:
                new_article = Article(
                    title=article_data['title'],
                    link=article_data['link'],
                    content=content
                )
                db.session.add(new_article)
    
    db.session.commit()
    return jsonify({'message': 'Articles refreshed successfully'})

@app.route('/')
def serve():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    # Remove the old database file if it exists
    db_file = 'articles.db'
    if os.path.exists(db_file):
        os.remove(db_file)
    
    with app.app_context():
        db.create_all()
    app.run(debug=True)
