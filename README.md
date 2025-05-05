# BeautifulSoup4
## Guide d'utilisation du projet Web Scraping - Blog du Modérateur

Ce projet permet de collecter et visualiser des articles du site **Blog du Modérateur** à l'aide de **BeautifulSoup4** pour le scraping et **Streamlit** pour l'interface utilisateur.

### Prérequis

- **Python 3.x**
- **MongoDB** installé et en cours d'exécution sur le port par défaut (27017)
- **MongoDB Compass** (optionnel, pour visualiser directement les données)

### Installation des dépendances

```sh
pip install requests beautifulsoup4 pymongo streamlit pillow
```

### Utilisation

```sh
python beautifulSoup4.py
```

#### 1. Collecte des données

Exécutez d'abord le script de scraping pour collecter les articles :

Ce script va :
- Parcourir les 5 catégories principales du Blog du Modérateur (*Web, Marketing, Social, Tech, Tools*).
- Récupérer les informations de chaque article (*titre, résumé, auteur, date, images, etc.*).
- Vous demander si vous souhaitez enregistrer les données dans MongoDB (répondez "o" pour oui).

> **Remarque :** Le processus prend quelques minutes car le script visite chaque article individuellement.

#### 2. Visualisation des données avec Streamlit

Une fois les données collectées, lancez l'interface utilisateur Streamlit :

```sh
streamlit run streamlit-scrapping.py
```

L'application web s'ouvrira automatiquement dans votre navigateur par défaut.

### Fonctionnalités de l'interface

- Visualisation des articles par catégorie.
- Recherche par mots-clés.
- Filtrage par auteur.
- Affichage des images, résumés et tags.
- Vue détaillée de chaque article.

### Remarques

- Ne lancez pas le scraping trop fréquemment pour respecter le site web.
- Les données sont stockées localement dans MongoDB, aucune sauvegarde n'est nécessaire.
- Si vous rencontrez des erreurs avec MongoDB, vérifiez que le service est bien en cours d'exécution.
- Pour examiner directement les données collectées, vous pouvez utiliser **MongoDB Compass** et vous connecter à la base de données `blog_scraper`, collection `articles`.