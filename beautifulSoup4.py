import requests
from bs4 import BeautifulSoup
import pymongo
from datetime import datetime
import time

def scrape_article_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        h1 = soup.find('h1', class_='entry-title')
        article_title = h1.text.strip() if h1 else "Titre non trouvé"
        
        summary = ""
        article_hat = soup.find('div', class_='article-hat')
        if article_hat:
            summary_p = article_hat.find('p')
            if summary_p:
                summary = summary_p.text.strip()
                print(f"Résumé: {summary[:50]}...")
        
        author = "Auteur non spécifié"
        publish_date = ""
        publish_datetime = ""
        
        meta_info = soup.find('div', class_='meta-info')
        if meta_info:
            byline = meta_info.find('span', class_='byline')
            if byline and byline.find('a'):
                author = byline.find('a').text.strip()
                print(f"Auteur: {author}")
                
            posted_on = meta_info.find('span', class_='posted-on')
            if posted_on:
                time_tag = posted_on.find('time')
                if time_tag:
                    publish_date = time_tag.text.strip()
                    publish_datetime = time_tag.get('datetime', '')
                    print(f"Date de publication: {publish_date}")
        
        images = []
        figures = soup.find_all('figure')
        
        for i, figure in enumerate(figures):
            image_data = {}
            
            img_tag = figure.find('img')
            if img_tag:
                image_url = img_tag.get('data-lazy-src') or img_tag.get('src')
                if image_url:
                    image_data['url'] = image_url
                    image_data['alt'] = img_tag.get('alt', '')
                    
                    width = img_tag.get('width')
                    height = img_tag.get('height')
                    if width and height:
                        image_data['dimensions'] = f"{width}x{height}"
            
            a_tag = figure.find('a', class_='lightbox')
            if a_tag:
                image_data['full_size_url'] = a_tag.get('href')
            
            figcaption = figure.find('figcaption')
            if figcaption:
                image_data['caption'] = figcaption.text.strip()
            
            if image_data:
                print(f"Image {i+1} trouvée" + (f": {image_data.get('caption', '')[:30]}..." if 'caption' in image_data else ""))
                images.append(image_data)
        
        main_category = ""
        tags = []
        article_terms = soup.find('div', class_='article-terms')
        
        if article_terms:
            cats_list = article_terms.find('div', class_='cats-list')
            if cats_list:
                cat_span = cats_list.find('span', class_='cat')
                if cat_span and cat_span.has_attr('data-cat'):
                    main_category = cat_span['data-cat']
                    print(f"Catégorie principale: {main_category}")
                    
            tags_list = article_terms.find('ul', class_='tags-list')
            if tags_list:
                tag_links = tags_list.find_all('a', class_='post-tags')
                
                for tag in tag_links:
                    tag_name = tag.text.strip()
                    tag_url = tag.get('href')
                    tag_id = tag.get('data-tag')
                    
                    print(f"Tag: {tag_name} (ID: {tag_id})")
                    
                    tags.append({
                        'name': tag_name,
                        'url': tag_url,
                        'data_tag': tag_id
                    })
        
        return {
            'detailed_title': article_title,
            'summary': summary,
            'author': author,
            'publish_date': publish_date,
            'publish_datetime': publish_datetime,
            'main_category': main_category,
            'tags': tags,
            'images': images
        }
        
    except Exception as e:
        print(f"Erreur lors du scraping de l'article {url}: {e}")
        return {
            'detailed_title': "Erreur de récupération", 
            'summary': "",
            'author': "",
            'publish_date': "",
            'publish_datetime': "",
            'main_category': "", 
            'tags': [],
            'images': []
        }
    
def scrape_category_articles(category_url, category_name):
    try:
        print(f"\nScraping catégorie: {category_name} ({category_url})")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(category_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = soup.find_all('article', class_='post')
        data = []
        
        print(f"Nombre d'articles trouvés dans la catégorie {category_name}: {len(articles)}")
        
        for article in articles:
            header = article.find('header', class_='entry-header')
            if not header:
                continue
                
            link_tag = header.find('a')
            if not link_tag:
                continue
                
            link = link_tag.get('href')
            h3 = link_tag.find('h3', class_='entry-title')
            if not h3:
                continue
                
            title = h3.text.strip()
            
            thumbnail_url = None
            thumbnail_div = article.find('div', class_='post-thumbnail')
            if thumbnail_div:
                img_tag = thumbnail_div.find('img')
                if img_tag:
                    thumbnail_url = img_tag.get('data-lazy-src') or img_tag.get('src')
            
            print(f"Article trouvé: {title}")
            if thumbnail_url:
                print(f"Thumbnail: {thumbnail_url}")
            
            print(f"Récupération des détails de l'article: {link}")
            
            article_details = scrape_article_content(link)
            
            time.sleep(1)
            
            data.append({
                'list_title': title,
                'link': link,
                'thumbnail': thumbnail_url,
                'page_title': article_details['detailed_title'],
                'summary': article_details['summary'],
                'author': article_details['author'],
                'publish_date': article_details['publish_date'],
                'publish_datetime': article_details['publish_datetime'],
                'main_category': category_name, 
                'category_url': category_url, 
                'tags': article_details['tags'],
                'images': article_details['images'],
                'date_scraped': datetime.now()
            })
        
        print(f"Nb articles dans catégorie {category_name}: {len(data)}")
        return data
    
    except Exception as e:
        print(f"Erreur {category_name}: {e}")
        return []

def scrape_all_categories():
    categories = [
        {"name": "Web", "url": "https://www.blogdumoderateur.com/web/"},
        {"name": "Marketing", "url": "https://www.blogdumoderateur.com/marketing/"},
        {"name": "Social", "url": "https://www.blogdumoderateur.com/social/"},
        {"name": "Tech", "url": "https://www.blogdumoderateur.com/tech/"},
        {"name": "Tools", "url": "https://www.blogdumoderateur.com/tools/"}
    ]
    
    all_articles = []
    
    for category in categories:
        print(f"\n{'='*60}")
        print(f"CATÉGORIE: {category['name'].upper()}")
        print(f"{'='*60}")
        
        category_articles = scrape_category_articles(category["url"], category["name"])
        all_articles.extend(category_articles)
        
        print(f"Pause de 2 secondes avant la prochaine catégorie...")
        time.sleep(2)
    
    return all_articles

def store_in_mongodb(data):
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["blog_scraper"]
        collection = db["articles"]
        
        if data:
            for article in data:
                existing = collection.find_one({"link": article['link']})
                
                if existing:
                    collection.update_one(
                        {"_id": existing['_id']},
                        {"$set": article}
                    )
                    print({article['list_title']})
                else:
                    collection.insert_one(article)
                    print({article['list_title']})
            
            print(f"{len(data)} articles")
        else:
            print("no data")
            
    except Exception as e:
        print(f"{e}")

if __name__ == "__main__":
    start_time = datetime.now()
    article_data = scrape_all_categories()
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\ {duration.total_seconds()} secondes")
    print(f"total: {len(article_data)}")
    
    category_counts = {}
    for article in article_data:
        category = article['main_category']
        if category in category_counts:
            category_counts[category] += 1
        else:
            category_counts[category] = 1
    
    print("\nRésumé catégorie:")
    for category, count in category_counts.items():
        print(f"- {category}: {count} articles")
    
    save_to_db = input("\nSauvegarder les données dans MongoDB? (o/n): ")
    if save_to_db.lower() == 'o':
        store_in_mongodb(article_data)
        print("Données sauvegardées")
    else:
        print("Les données pas sauvegardées")