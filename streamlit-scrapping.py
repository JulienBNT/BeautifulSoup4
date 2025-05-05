import streamlit as st
import pymongo
from datetime import datetime
import pandas as pd
import requests
from io import BytesIO
from PIL import Image
import locale
import re
import hashlib


def generate_article_key(article):
    unique_string = f"{article.get('link', '')}-{article.get('list_title', '')}"
    hash_object = hashlib.md5(unique_string.encode())
    return f"btn_{hash_object.hexdigest()[:10]}"

try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR')
    except:
        pass 

st.set_page_config(
    page_title="Explorateur d'articles - Blog du Modérateur",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_database():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    return client["blog_scraper"]

@st.cache_data(ttl=60)  
def get_articles():
    db = get_database()
    collection = db["articles"]
    articles = list(collection.find({}))
    return articles

@st.cache_data
def display_image(url):
    if not url:
        return None
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        st.warning(f"Impossible de charger l'image: {e}")
        return None

st.title("📚 Explorateur d'articles du Blog du Modérateur")
st.markdown("Découvrez tous les articles scrapés par catégories.")

articles = get_articles()

if not articles:
    st.error("Aucun article trouvé dans la base de données. Veuillez d'abord exécuter le scraping.")
    st.stop()

st.sidebar.header("Statistiques")
st.sidebar.write(f"📊 Nombre total d'articles: {len(articles)}")

categories = {}
for article in articles:
    category = article.get('main_category', 'Non catégorisé')
    if category in categories:
        categories[category] += 1
    else:
        categories[category] = 1

st.sidebar.subheader("Catégories disponibles")
for cat, count in categories.items():
    st.sidebar.write(f"- {cat}: {count} articles")

st.sidebar.header("Filtres")

selected_category = st.sidebar.selectbox(
    "Sélectionner une catégorie",
    ["Toutes les catégories"] + list(categories.keys())
)

search_query = st.sidebar.text_input("Rechercher des articles", "")

all_authors = set()
for article in articles:
    if 'author' in article and article['author']:
        all_authors.add(article['author'])

selected_author = st.sidebar.selectbox(
    "Filtrer par auteur",
    ["Tous les auteurs"] + sorted(list(all_authors))
)

filtered_articles = articles
if selected_category != "Toutes les catégories":
    filtered_articles = [a for a in filtered_articles if a.get('main_category') == selected_category]

if selected_author != "Tous les auteurs":
    filtered_articles = [a for a in filtered_articles if a.get('author') == selected_author]

if search_query:
    search_terms = search_query.lower().split()
    temp_articles = []
    for article in filtered_articles:
        article_text = (
            f"{article.get('page_title', '')} {article.get('list_title', '')} "
            f"{article.get('summary', '')} {article.get('author', '')}"
        ).lower()
        
        if 'tags' in article and article['tags']:
            for tag in article['tags']:
                if 'name' in tag:
                    article_text += f" {tag['name'].lower()}"
        
        if any(term in article_text for term in search_terms):
            temp_articles.append(article)
    filtered_articles = temp_articles

st.write(f"### {len(filtered_articles)} articles correspondent à vos critères")

if not filtered_articles:
    st.warning("Aucun article ne correspond aux critères de recherche.")
else:
    if selected_category == "Toutes les catégories":
        articles_by_cat = {}
        for article in filtered_articles:
            cat = article.get('main_category', 'Non catégorisé')
            if cat not in articles_by_cat:
                articles_by_cat[cat] = []
            articles_by_cat[cat].append(article)
        
        for cat, cat_articles in articles_by_cat.items():
            with st.expander(f"{cat} ({len(cat_articles)} articles)", expanded=True):
                for article in cat_articles:
                    with st.container():
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            if 'thumbnail' in article and article['thumbnail']:
                                st.image(article['thumbnail'], use_column_width=True)
                            elif 'images' in article and article['images'] and len(article['images']) > 0:
                                img_url = article['images'][0].get('url')
                                if img_url:
                                    st.image(img_url, use_column_width=True)
                        
                        with col2:
                            st.markdown(f"### [{article.get('page_title', article.get('list_title', 'Sans titre'))}]({article.get('link', '#')})")
                            
                            st.write(f"**Auteur:** {article.get('author', 'Non spécifié')}")
                            st.write(f"**Date de publication:** {article.get('publish_date', 'Non spécifiée')}")
                            
                            if 'summary' in article and article['summary']:
                                st.write(f"**Résumé:** {article['summary']}")
                            
                            if 'tags' in article and article['tags']:
                                tags = [tag.get('name', '') for tag in article['tags'] if 'name' in tag]
                                if tags:
                                    st.write(f"**Tags:** {', '.join(tags)}")
                        
                        if st.button(f"Voir plus de détails", key=generate_article_key(article)):
                            with st.container():
                                st.markdown("### 📄 Détails complets de l'article")
                                st.markdown("---")
                                st.write("## Informations complètes")
                                st.write(f"**Titre complet:** {article.get('page_title', 'Non spécifié')}")
                                st.write(f"**Titre dans la liste:** {article.get('list_title', 'Non spécifié')}")
                                st.write(f"**URL de l'article:** {article.get('link', 'Non spécifiée')}")
                                
                                if 'images' in article and article['images']:
                                    st.write("### Images")
                                    for i, img in enumerate(article['images']):
                                        cols = st.columns([1, 2])
                                        with cols[0]:
                                            img_url = img.get('url', '')
                                            if img_url:
                                                st.image(img_url, width=200)
                                        with cols[1]:
                                            st.write(f"**Légende:** {img.get('caption', 'Pas de légende')}")
                                            st.write(f"**Description:** {img.get('alt', 'Pas de description')}")
                                            if 'dimensions' in img:
                                                st.write(f"**Dimensions:** {img['dimensions']}")
                                            if 'full_size_url' in img:
                                                st.write(f"[Voir en taille réelle]({img['full_size_url']})")
                        
                        st.markdown("---")
    else:
        for article in filtered_articles:
            with st.container():
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if 'thumbnail' in article and article['thumbnail']:
                        st.image(article['thumbnail'], use_column_width=True)
                    elif 'images' in article and article['images'] and len(article['images']) > 0:
                        img_url = article['images'][0].get('url')
                        if img_url:
                            st.image(img_url, use_column_width=True)
                
                with col2:
                    st.markdown(f"### [{article.get('page_title', article.get('list_title', 'Sans titre'))}]({article.get('link', '#')})")
                    
                    st.write(f"**Auteur:** {article.get('author', 'Non spécifié')}")
                    st.write(f"**Date de publication:** {article.get('publish_date', 'Non spécifiée')}")
                    
                    if 'summary' in article and article['summary']:
                        st.write(f"**Résumé:** {article['summary']}")
                    
                    if 'tags' in article and article['tags']:
                        tags = [tag.get('name', '') for tag in article['tags'] if 'name' in tag]
                        if tags:
                            st.write(f"**Tags:** {', '.join(tags)}")
                
                if st.button(f"Voir plus de détails", key=generate_article_key(article)):
                    with st.container():
                        st.markdown("### 📄 Détails complets de l'article")
                        st.markdown("---")
                        st.write("## Informations complètes")
                        st.write(f"**Titre complet:** {article.get('page_title', 'Non spécifié')}")
                        st.write(f"**Titre dans la liste:** {article.get('list_title', 'Non spécifié')}")
                        st.write(f"**URL de l'article:** {article.get('link', 'Non spécifiée')}")
                        
                        if 'images' in article and article['images']:
                            st.write("### Images")
                            for i, img in enumerate(article['images']):
                                cols = st.columns([1, 2])
                                with cols[0]:
                                    img_url = img.get('url', '')
                                    if img_url:
                                        st.image(img_url, width=200)
                                with cols[1]:
                                    st.write(f"**Légende:** {img.get('caption', 'Pas de légende')}")
                                    st.write(f"**Description:** {img.get('alt', 'Pas de description')}")
                                    if 'dimensions' in img:
                                        st.write(f"**Dimensions:** {img['dimensions']}")
                                    if 'full_size_url' in img:
                                        st.write(f"[Voir en taille réelle]({img['full_size_url']})")
                
                st.markdown("---")

st.sidebar.markdown("---")
st.sidebar.info("""
**À propos de cette application**

Cette application affiche les articles scrapés du Blog du Modérateur.
Données collectées avec BeautifulSoup4 et stockées dans MongoDB.
Correspond au TP 
""")