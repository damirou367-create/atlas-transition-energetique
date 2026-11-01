"""
Streamlit_app.py — Version complémentaire du tableau de bord Trends
(Énergies renouvelables et GES), construite avec Pandas / NumPy / Streamlit,
conformément à la démarche officielle du projet Trends.

Cette version ne remplace pas le tableau de bord HTML natif (qui reste le
livrable principal, pour les raisons expliquées dans le rapport de stage :
portabilité, aucune installation requise côté utilisateur final). Elle
démontre la maîtrise de la stack officiellement recommandée, sur 9 onglets :
transition, corrélation, projection, simulateur d'objectif, CO2 & GES,
comparaison de pays, cluster socio-économique, tests statistiques et carte.

Thème visuel : harmonisé sur la palette Gaea officielle (voir
.streamlit/config.toml et le bloc CSS ci-dessous), transmise par le
coordinateur de projet pour homogénéiser les différents tableaux de bord.

Lancement : streamlit run streamlit_app.py
Prérequis : pip install -r requirements.txt
"""

import streamlit as st
import pandas as pd
import numpy as np
import math
import re
import os
import datetime
import plotly.graph_objects as go
import plotly.express as px


FICHIER_BASE = "data/clean/base_energie_ges_owid.csv"

PAYS_COMPARAISON = [
    "France", "Germany", "United States", "China",
    "India", "Denmark", "Brazil",
]

NOMS_FR = {
    "Afghanistan": "Afghanistan", "Albania": "Albanie", "Algeria": "Algérie",
    "Angola": "Angola", "Antarctica": "Antarctique", "Antigua and Barbuda": "Antigua-et-Barbuda",
    "Argentina": "Argentine", "Armenia": "Arménie", "Aruba": "Aruba",
    "Australia": "Australie", "Austria": "Autriche", "Azerbaijan": "Azerbaïdjan",
    "Bahamas": "Bahamas", "Bahrain": "Bahreïn", "Bangladesh": "Bangladesh",
    "Barbados": "Barbade", "Belarus": "Biélorussie", "Belgium": "Belgique",
    "Belize": "Belize", "Benin": "Bénin", "Bermuda": "Bermudes",
    "Bhutan": "Bhoutan", "Bolivia": "Bolivie", "Bosnia and Herzegovina": "Bosnie-Herzégovine",
    "Botswana": "Botswana", "Brazil": "Brésil", "British Virgin Islands": "Îles Vierges britanniques",
    "Brunei": "Brunei", "Bulgaria": "Bulgarie", "Burkina Faso": "Burkina Faso",
    "Burundi": "Burundi", "Cambodia": "Cambodge", "Cameroon": "Cameroun",
    "Canada": "Canada", "Cape Verde": "Cap-Vert", "Central African Republic": "République centrafricaine",
    "Chad": "Tchad", "Chile": "Chili", "China": "Chine",
    "Colombia": "Colombie", "Comoros": "Comores", "Congo": "Congo",
    "Cook Islands": "Îles Cook", "Costa Rica": "Costa Rica", "Cote d'Ivoire": "Côte d'Ivoire",
    "Croatia": "Croatie", "Cuba": "Cuba", "Curacao": "Curaçao",
    "Cyprus": "Chypre", "Czechia": "Tchéquie", "Democratic Republic of Congo": "République démocratique du Congo",
    "Denmark": "Danemark", "Djibouti": "Djibouti", "Dominica": "Dominique",
    "Dominican Republic": "République dominicaine", "East Timor": "Timor oriental", "Ecuador": "Équateur",
    "Egypt": "Égypte", "El Salvador": "Salvador", "Equatorial Guinea": "Guinée équatoriale",
    "Eritrea": "Érythrée", "Estonia": "Estonie", "Eswatini": "Eswatini",
    "Ethiopia": "Éthiopie", "Faroe Islands": "Îles Féroé", "Fiji": "Fidji",
    "Finland": "Finlande", "France": "France", "French Polynesia": "Polynésie française",
    "Gabon": "Gabon", "Gambia": "Gambie", "Georgia": "Géorgie",
    "Germany": "Allemagne", "Ghana": "Ghana", "Greece": "Grèce",
    "Greenland": "Groenland", "Grenada": "Grenade", "Guatemala": "Guatemala",
    "Guinea": "Guinée", "Guinea-Bissau": "Guinée-Bissau", "Guyana": "Guyana",
    "Haiti": "Haïti", "Honduras": "Honduras", "Hong Kong": "Hong Kong",
    "Hungary": "Hongrie", "Iceland": "Islande", "India": "Inde",
    "Indonesia": "Indonésie", "Iran": "Iran", "Iraq": "Irak",
    "Ireland": "Irlande", "Israel": "Israël", "Italy": "Italie",
    "Jamaica": "Jamaïque", "Japan": "Japon", "Jordan": "Jordanie",
    "Kazakhstan": "Kazakhstan", "Kenya": "Kenya", "Kiribati": "Kiribati",
    "Kuwait": "Koweït", "Kyrgyzstan": "Kirghizistan", "Laos": "Laos",
    "Latvia": "Lettonie", "Lebanon": "Liban", "Lesotho": "Lesotho",
    "Liberia": "Libéria", "Libya": "Libye", "Lithuania": "Lituanie",
    "Luxembourg": "Luxembourg", "Macao": "Macao", "Madagascar": "Madagascar",
    "Malawi": "Malawi", "Malaysia": "Malaisie", "Maldives": "Maldives",
    "Mali": "Mali", "Malta": "Malte", "Mauritania": "Mauritanie",
    "Mauritius": "Maurice", "Mexico": "Mexique", "Micronesia (country)": "Micronésie",
    "Moldova": "Moldavie", "Mongolia": "Mongolie", "Montenegro": "Monténégro",
    "Montserrat": "Montserrat", "Morocco": "Maroc", "Mozambique": "Mozambique",
    "Myanmar": "Myanmar", "Namibia": "Namibie", "Nauru": "Nauru",
    "Nepal": "Népal", "Netherlands": "Pays-Bas", "New Caledonia": "Nouvelle-Calédonie",
    "New Zealand": "Nouvelle-Zélande", "Nicaragua": "Nicaragua", "Niger": "Niger",
    "Nigeria": "Nigeria", "Niue": "Niue", "North Korea": "Corée du Nord",
    "North Macedonia": "Macédoine du Nord", "Norway": "Norvège", "Oman": "Oman",
    "Pakistan": "Pakistan", "Palestine": "Palestine", "Panama": "Panama",
    "Papua New Guinea": "Papouasie-Nouvelle-Guinée", "Paraguay": "Paraguay", "Peru": "Pérou",
    "Philippines": "Philippines", "Poland": "Pologne", "Portugal": "Portugal",
    "Qatar": "Qatar", "Romania": "Roumanie", "Russia": "Russie",
    "Rwanda": "Rwanda", "Saint Helena": "Sainte-Hélène", "Saint Kitts and Nevis": "Saint-Christophe-et-Niévès",
    "Saint Lucia": "Sainte-Lucie", "Saint Pierre and Miquelon": "Saint-Pierre-et-Miquelon",
    "Saint Vincent and the Grenadines": "Saint-Vincent-et-les-Grenadines", "Samoa": "Samoa",
    "Sao Tome and Principe": "Sao Tomé-et-Principe", "Saudi Arabia": "Arabie saoudite", "Senegal": "Sénégal",
    "Serbia": "Serbie", "Seychelles": "Seychelles", "Sierra Leone": "Sierra Leone",
    "Singapore": "Singapour", "Slovakia": "Slovaquie", "Slovenia": "Slovénie",
    "Solomon Islands": "Îles Salomon", "Somalia": "Somalie", "South Africa": "Afrique du Sud",
    "South Korea": "Corée du Sud", "South Sudan": "Soudan du Sud", "Spain": "Espagne",
    "Sri Lanka": "Sri Lanka", "Sudan": "Soudan", "Suriname": "Suriname",
    "Sweden": "Suède", "Switzerland": "Suisse", "Syria": "Syrie",
    "Taiwan": "Taïwan", "Tajikistan": "Tadjikistan", "Tanzania": "Tanzanie",
    "Thailand": "Thaïlande", "Togo": "Togo", "Tonga": "Tonga",
    "Trinidad and Tobago": "Trinité-et-Tobago", "Tunisia": "Tunisie", "Turkey": "Turquie",
    "Turkmenistan": "Turkménistan", "Turks and Caicos Islands": "Îles Turques-et-Caïques", "Tuvalu": "Tuvalu",
    "Uganda": "Ouganda", "Ukraine": "Ukraine", "United Arab Emirates": "Émirats arabes unis",
    "United Kingdom": "Royaume-Uni", "United States": "États-Unis", "Uruguay": "Uruguay",
    "Uzbekistan": "Ouzbékistan", "Vanuatu": "Vanuatu", "Venezuela": "Venezuela",
    "Vietnam": "Vietnam", "Yemen": "Yémen", "Zambia": "Zambie", "Zimbabwe": "Zimbabwe",
}

# Formes avec article, pour des phrases grammaticalement correctes
# ("le Danemark", "l'Allemagne", "des États-Unis"...) dans les
# paragraphes narratifs générés automatiquement.
ARTICLE_PAYS = {
    "France": ("la France", "de la France"),
    "Germany": ("l'Allemagne", "de l'Allemagne"),
    "United States": ("les États-Unis", "des États-Unis"),
    "China": ("la Chine", "de la Chine"),
    "India": ("l'Inde", "de l'Inde"),
    "Denmark": ("le Danemark", "du Danemark"),
    "Brazil": ("le Brésil", "du Brésil"),
}


def avec_article(pays):
    return ARTICLE_PAYS.get(pays, (NOMS_FR.get(pays, pays), NOMS_FR.get(pays, pays)))[0]


def de_pays(pays):
    return ARTICLE_PAYS.get(pays, (NOMS_FR.get(pays, pays), "de " + NOMS_FR.get(pays, pays)))[1]


def avec_article_maj(pays):
    """Comme avec_article, mais avec la première lettre en majuscule
    (sans écraser la majuscule du nom propre, contrairement à .capitalize())."""
    s = avec_article(pays)
    return s[0].upper() + s[1:]

# Dictionnaire pays -> continent, identique à celui du tableau de bord natif
# (app.py), pour que le sélecteur de continent donne les mêmes résultats.
CONTINENTS = {
    "Afghanistan": "Asie", "Albania": "Europe", "Algeria": "Afrique",
    "Angola": "Afrique", "Antarctica": "Autre", "Antigua and Barbuda": "Amérique du Nord",
    "Argentina": "Amérique du Sud", "Armenia": "Asie", "Aruba": "Amérique du Nord",
    "Australia": "Océanie", "Austria": "Europe", "Azerbaijan": "Asie",
    "Bahamas": "Amérique du Nord", "Bahrain": "Asie", "Bangladesh": "Asie",
    "Barbados": "Amérique du Nord", "Belarus": "Europe", "Belgium": "Europe",
    "Belize": "Amérique du Nord", "Benin": "Afrique", "Bermuda": "Amérique du Nord",
    "Bhutan": "Asie", "Bolivia": "Amérique du Sud", "Bosnia and Herzegovina": "Europe",
    "Botswana": "Afrique", "Brazil": "Amérique du Sud", "British Virgin Islands": "Amérique du Nord",
    "Brunei": "Asie", "Bulgaria": "Europe", "Burkina Faso": "Afrique",
    "Burundi": "Afrique", "Cambodia": "Asie", "Cameroon": "Afrique",
    "Canada": "Amérique du Nord", "Cape Verde": "Afrique", "Central African Republic": "Afrique",
    "Chad": "Afrique", "Chile": "Amérique du Sud", "China": "Asie",
    "Colombia": "Amérique du Sud", "Comoros": "Afrique", "Congo": "Afrique",
    "Cook Islands": "Océanie", "Costa Rica": "Amérique du Nord", "Cote d'Ivoire": "Afrique",
    "Croatia": "Europe", "Cuba": "Amérique du Nord", "Curacao": "Amérique du Nord",
    "Cyprus": "Europe", "Czechia": "Europe", "Democratic Republic of Congo": "Afrique",
    "Denmark": "Europe", "Djibouti": "Afrique", "Dominica": "Amérique du Nord",
    "Dominican Republic": "Amérique du Nord", "East Timor": "Asie", "Ecuador": "Amérique du Sud",
    "Egypt": "Afrique", "El Salvador": "Amérique du Nord", "Equatorial Guinea": "Afrique",
    "Eritrea": "Afrique", "Estonia": "Europe", "Eswatini": "Afrique",
    "Ethiopia": "Afrique", "Faroe Islands": "Europe", "Fiji": "Océanie",
    "Finland": "Europe", "France": "Europe", "French Polynesia": "Océanie",
    "Gabon": "Afrique", "Gambia": "Afrique", "Georgia": "Asie",
    "Germany": "Europe", "Ghana": "Afrique", "Greece": "Europe",
    "Greenland": "Amérique du Nord", "Grenada": "Amérique du Nord", "Guatemala": "Amérique du Nord",
    "Guinea": "Afrique", "Guinea-Bissau": "Afrique", "Guyana": "Amérique du Sud",
    "Haiti": "Amérique du Nord", "Honduras": "Amérique du Nord", "Hong Kong": "Asie",
    "Hungary": "Europe", "Iceland": "Europe", "India": "Asie",
    "Indonesia": "Asie", "Iran": "Asie", "Iraq": "Asie",
    "Ireland": "Europe", "Israel": "Asie", "Italy": "Europe",
    "Jamaica": "Amérique du Nord", "Japan": "Asie", "Jordan": "Asie",
    "Kazakhstan": "Asie", "Kenya": "Afrique", "Kiribati": "Océanie",
    "Kuwait": "Asie", "Kyrgyzstan": "Asie", "Laos": "Asie",
    "Latvia": "Europe", "Lebanon": "Asie", "Lesotho": "Afrique",
    "Liberia": "Afrique", "Libya": "Afrique", "Lithuania": "Europe",
    "Luxembourg": "Europe", "Macao": "Asie", "Madagascar": "Afrique",
    "Malawi": "Afrique", "Malaysia": "Asie", "Maldives": "Asie",
    "Mali": "Afrique", "Malta": "Europe", "Mauritania": "Afrique",
    "Mauritius": "Afrique", "Mexico": "Amérique du Nord", "Micronesia (country)": "Océanie",
    "Moldova": "Europe", "Mongolia": "Asie", "Montenegro": "Europe",
    "Montserrat": "Amérique du Nord", "Morocco": "Afrique", "Mozambique": "Afrique",
    "Myanmar": "Asie", "Namibia": "Afrique", "Nauru": "Océanie",
    "Nepal": "Asie", "Netherlands": "Europe", "New Caledonia": "Océanie",
    "New Zealand": "Océanie", "Nicaragua": "Amérique du Nord", "Niger": "Afrique",
    "Nigeria": "Afrique", "Niue": "Océanie", "North Korea": "Asie",
    "North Macedonia": "Europe", "Norway": "Europe", "Oman": "Asie",
    "Pakistan": "Asie", "Palestine": "Asie", "Panama": "Amérique du Nord",
    "Papua New Guinea": "Océanie", "Paraguay": "Amérique du Sud", "Peru": "Amérique du Sud",
    "Philippines": "Asie", "Poland": "Europe", "Portugal": "Europe",
    "Qatar": "Asie", "Romania": "Europe", "Russia": "Europe",
    "Rwanda": "Afrique", "Saint Helena": "Afrique", "Saint Kitts and Nevis": "Amérique du Nord",
    "Saint Lucia": "Amérique du Nord", "Saint Pierre and Miquelon": "Amérique du Nord",
    "Saint Vincent and the Grenadines": "Amérique du Nord", "Samoa": "Océanie",
    "Sao Tome and Principe": "Afrique", "Saudi Arabia": "Asie", "Senegal": "Afrique",
    "Serbia": "Europe", "Seychelles": "Afrique", "Sierra Leone": "Afrique",
    "Singapore": "Asie", "Slovakia": "Europe", "Slovenia": "Europe",
    "Solomon Islands": "Océanie", "Somalia": "Afrique", "South Africa": "Afrique",
    "South Korea": "Asie", "South Sudan": "Afrique", "Spain": "Europe",
    "Sri Lanka": "Asie", "Sudan": "Afrique", "Suriname": "Amérique du Sud",
    "Sweden": "Europe", "Switzerland": "Europe", "Syria": "Asie",
    "Taiwan": "Asie", "Tajikistan": "Asie", "Tanzania": "Afrique",
    "Thailand": "Asie", "Togo": "Afrique", "Tonga": "Océanie",
    "Trinidad and Tobago": "Amérique du Nord", "Tunisia": "Afrique", "Turkey": "Asie",
    "Turkmenistan": "Asie", "Turks and Caicos Islands": "Amérique du Nord", "Tuvalu": "Océanie",
    "Uganda": "Afrique", "Ukraine": "Europe", "United Arab Emirates": "Asie",
    "United Kingdom": "Europe", "United States": "Amérique du Nord", "Uruguay": "Amérique du Sud",
    "Uzbekistan": "Asie", "Vanuatu": "Océanie", "Venezuela": "Amérique du Sud",
    "Vietnam": "Asie", "Yemen": "Asie", "Zambia": "Afrique", "Zimbabwe": "Afrique",
}

CONTINENTS_DISPONIBLES = ["Afrique", "Amérique du Nord", "Amérique du Sud", "Asie", "Europe", "Océanie"]

def continent_de(pays):
    return CONTINENTS.get(pays, "Autre")


# ------------------------------------------------------------
# Chargement des données (mis en cache par Streamlit : ne relit
# le fichier qu'une seule fois, même si l'utilisateur change les filtres)
# ------------------------------------------------------------
FICHIER_PIB = "data/clean/pib_par_habitant.csv"

@st.cache_data(show_spinner="Chargement de la base de données (206 pays, 1990-2024)…")
def charger_donnees(chemin=FICHIER_BASE):
    df = pd.read_csv(chemin)
    df["annee"] = pd.to_numeric(df["annee"], errors="coerce")
    for col in ["part_renouvelables_dans_electricite", "intensite_carbone_electricite",
                "co2_par_habitant", "production_totale_electricite"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["annee", "pays"])

    # Fusion du PIB par habitant (PPA, Banque mondiale), préparé au
    # préalable par preparer_pib_habitant.py -- absent silencieusement si
    # le fichier n'existe pas encore, comme pour le tableau de bord natif.
    try:
        df_pib = pd.read_csv(FICHIER_PIB)
        df_pib["annee"] = pd.to_numeric(df_pib["annee"], errors="coerce")
        df_pib["pib_par_habitant"] = pd.to_numeric(df_pib["pib_par_habitant"], errors="coerce")
        df = df.merge(df_pib[["code_iso", "annee", "pib_par_habitant"]], on=["code_iso", "annee"], how="left")
    except FileNotFoundError:
        df["pib_par_habitant"] = np.nan

    return df


COULEURS_CLUSTER = ["#8D1C42", "#2f80ed", "#4d6519", "#b45309", "#3d346b", "#2A9D8F", "#D4A017", "#7a1f3d"]


def _kmeans_plus_plus_init_np(X, k, graine=42):
    rng = np.random.RandomState(graine)
    n = X.shape[0]
    centres = [X[rng.randint(n)]]
    for _ in range(1, k):
        distances = np.min(np.array([np.sum((X - c) ** 2, axis=1) for c in centres]), axis=0)
        total = distances.sum()
        if total == 0:
            centres.append(X[rng.randint(n)])
            continue
        probabilites = distances / total
        idx = rng.choice(n, p=probabilites)
        centres.append(X[idx])
    return np.array(centres)


def _kmeans_np(X, k, iterations_max=100, graine=42):
    """Algorithme des k-moyennes (Lloyd), initialisation k-means++ --
    même méthodologie que la version pure Python du tableau de bord
    natif (voir app.py), pour rester cohérent entre les deux versions."""
    n = X.shape[0]
    k_reel = min(k, max(1, n - 1))
    centres = _kmeans_plus_plus_init_np(X, k_reel, graine)
    affectations = np.full(n, -1)

    for _ in range(iterations_max):
        distances = np.sqrt(((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2))
        nouvelles_affectations = distances.argmin(axis=1)
        if np.array_equal(nouvelles_affectations, affectations):
            break
        affectations = nouvelles_affectations
        for i in range(k_reel):
            membres = X[affectations == i]
            if len(membres) > 0:
                centres[i] = membres.mean(axis=0)

    distances_finales = np.sqrt(((X - centres[affectations]) ** 2).sum(axis=1))
    inertie = float((distances_finales ** 2).sum())
    return affectations, centres, inertie


def _choisir_k_optimal_np(X, k_min=2, k_max=8, graine=42):
    """Méthode du coude, automatisée géométriquement (voir app.py pour
    le détail de la logique, identique ici)."""
    n = X.shape[0]
    inerties = {}
    for k in range(k_min, min(k_max, n - 1) + 1):
        _, _, inertie = _kmeans_np(X, k, graine=graine)
        inerties[k] = inertie

    ks = sorted(inerties.keys())
    if len(ks) < 3:
        return (ks[0] if ks else k_min), inerties

    inertie_min, inertie_max = min(inerties.values()), max(inerties.values())
    k_span = ks[-1] - ks[0]

    def normaliser(k, inertie):
        x = (k - ks[0]) / k_span if k_span else 0
        y = (inertie - inertie_min) / (inertie_max - inertie_min) if inertie_max != inertie_min else 0
        return x, y

    x1, y1 = normaliser(ks[0], inerties[ks[0]])
    x2, y2 = normaliser(ks[-1], inerties[ks[-1]])
    denominateur = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

    meilleure_distance, k_optimal = -1, ks[0]
    for k in ks:
        x0, y0 = normaliser(k, inerties[k])
        numerateur = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        d = numerateur / denominateur if denominateur else 0
        if d > meilleure_distance:
            meilleure_distance, k_optimal = d, k

    return k_optimal, inerties


@st.cache_data(show_spinner="Calcul du cluster socio-économique (PIB / renouvelables / intensité carbone)…")
def _silhouette_moyenne_np(X, affectations, k):
    """Score de silhouette moyen (voir app.py pour la définition
    détaillée) -- implémentation numpy vectorisée, même méthodologie."""
    n = X.shape[0]
    if k < 2 or n < 3:
        return None
    diff = X[:, None, :] - X[None, :, :]
    dist_matrix = np.sqrt((diff ** 2).sum(axis=2))

    scores = np.zeros(n)
    for i in range(n):
        cluster_i = affectations[i]
        meme_masque = affectations == cluster_i
        meme_masque[i] = False
        if not meme_masque.any():
            scores[i] = 0.0
            continue
        a_i = dist_matrix[i, meme_masque].mean()
        b_i = None
        for c in range(k):
            if c == cluster_i:
                continue
            autre_masque = affectations == c
            if not autre_masque.any():
                continue
            d_moy = dist_matrix[i, autre_masque].mean()
            if b_i is None or d_moy < b_i:
                b_i = d_moy
        if b_i is None:
            scores[i] = 0.0
            continue
        denom = max(a_i, b_i)
        scores[i] = (b_i - a_i) / denom if denom > 0 else 0.0
    return float(scores.mean())


def _classification_hierarchique_np(X):
    """CAH (liaison moyenne) -- même méthodologie que la version Python
    native du tableau de bord natif (voir app.py), implémentée en numpy
    pour cette version Streamlit plutôt que via scipy, afin de garder les
    deux versions cohérentes entre elles."""
    n = X.shape[0]
    clusters = {i: [i] for i in range(n)}
    actifs = list(range(n))
    prochain_id = n
    fusions = []
    dist_points = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(axis=2))

    def distance_clusters(a, b):
        return dist_points[np.ix_(clusters[a], clusters[b])].mean()

    while len(actifs) > 1:
        meilleure = None
        for idx_a in range(len(actifs)):
            for idx_b in range(idx_a + 1, len(actifs)):
                a, b = actifs[idx_a], actifs[idx_b]
                dist = distance_clusters(a, b)
                if meilleure is None or dist < meilleure[2]:
                    meilleure = (a, b, dist)
        a, b, dist = meilleure
        nouveau_id = prochain_id
        prochain_id += 1
        clusters[nouveau_id] = clusters[a] + clusters[b]
        fusions.append((a, b, dist, len(clusters[nouveau_id])))
        actifs.remove(a)
        actifs.remove(b)
        actifs.append(nouveau_id)

    return fusions


def _construire_arbre_dendrogramme(fusions, n_feuilles):
    noeuds = {i: {"gauche": None, "droite": None, "hauteur": 0.0, "indice": i} for i in range(n_feuilles)}
    for i, (a, b, dist, _taille) in enumerate(fusions):
        noeuds[n_feuilles + i] = {"gauche": noeuds[a], "droite": noeuds[b], "hauteur": dist}
    racine = noeuds[n_feuilles + len(fusions) - 1]

    position = {"x": 0}

    def positionner(noeud):
        if noeud["gauche"] is None:
            noeud["x"] = position["x"]
            position["x"] += 1
            return noeud["x"]
        x_g = positionner(noeud["gauche"])
        x_d = positionner(noeud["droite"])
        noeud["x"] = (x_g + x_d) / 2
        return noeud["x"]

    positionner(racine)
    return racine


@st.cache_data(show_spinner="Classification hiérarchique (CAH)…")
def calculer_dendrogramme(_points):
    """Sous-échantillonne à 80 pays si la base en compte plus, pour
    rester lisible (même choix que la référence R : la CAH est
    coûteuse -- O(n³) -- et un dendrogramme à plusieurs centaines de
    feuilles n'est de toute façon pas lisible)."""
    n = _points.shape[0]
    if n > 80:
        rng = np.random.RandomState(42)
        indices = rng.choice(n, 80, replace=False)
        points_dendro = _points[indices]
        sous_echantillonne = True
    else:
        points_dendro = _points
        sous_echantillonne = False
    fusions = _classification_hierarchique_np(points_dendro)
    racine = _construire_arbre_dendrogramme(fusions, len(points_dendro))

    # indice de chaque feuille dans le jeu complet (pour afficher le nom du pays au survol)
    def _indicer(noeud):
        if noeud["gauche"] is None:
            noeud["indice_pays"] = int(indices[noeud["indice"]]) if sous_echantillonne else noeud["indice"]
            return
        _indicer(noeud["gauche"])
        _indicer(noeud["droite"])
    _indicer(racine)
    hauteur_max = max((f[2] for f in fusions), default=1.0)
    return racine, hauteur_max, sous_echantillonne, fusions


def _identifier_groupes_dendrogramme(racine, hauteur_coupe):
    """Découpe l'arbre CAH à la hauteur de coupe donnée : tout sous-arbre
    entièrement situé sous ce seuil forme un groupe. Retourne un
    dictionnaire {position x de la feuille : numéro de groupe}, pour
    colorer le dendrogramme selon les mêmes groupes que ceux obtenus à ce
    niveau de coupe (indépendamment du k-means, qui peut donner une
    partition légèrement différente sur les mêmes données)."""
    groupe_par_feuille = {}
    compteur = {"n": 0}

    def collecter_feuilles(noeud, groupe):
        if noeud["gauche"] is None:
            groupe_par_feuille[noeud["x"]] = groupe
            return
        collecter_feuilles(noeud["gauche"], groupe)
        collecter_feuilles(noeud["droite"], groupe)

    def parcourir(noeud):
        if noeud["gauche"] is None:
            groupe_par_feuille[noeud["x"]] = compteur["n"]
            compteur["n"] += 1
            return
        if noeud["hauteur"] <= hauteur_coupe:
            collecter_feuilles(noeud, compteur["n"])
            compteur["n"] += 1
        else:
            parcourir(noeud["gauche"])
            parcourir(noeud["droite"])

    parcourir(racine)
    return groupe_par_feuille


def graphique_dendrogramme(racine, sous_echantillonne, hauteur_coupe=None, groupe_par_feuille=None,
                           noms_pays=None, groupes_kmeans=None):
    """Dendrogramme de la CAH. Les groupes obtenus en coupant l'arbre à la
    ligne pointillée sont repérés par des lettres (A, B, C...) et des
    bandes de fond, dans des tons neutres : ce ne sont pas les groupes du
    k-means. Sous l'arbre, une rangée de carrés donne le groupe k-means de
    chaque pays, avec les mêmes couleurs que le nuage ACP et le tableau,
    pour comparer les deux méthodes d'un coup d'œil."""
    couleur_branche = "#5f6f52"
    couleur_haut = "#c2baa9"
    segments = {couleur_branche: ([], []), couleur_haut: ([], [])}

    def dessiner(noeud):
        if noeud["gauche"] is None:
            return
        y_fusion = noeud["hauteur"]
        sous_coupe = hauteur_coupe is None or y_fusion <= hauteur_coupe
        couleur = couleur_branche if sous_coupe else couleur_haut
        hx, hy = segments[couleur]
        hx.extend([noeud["gauche"]["x"], noeud["droite"]["x"], None])
        hy.extend([y_fusion, y_fusion, None])
        for enfant in (noeud["gauche"], noeud["droite"]):
            # un pays seul sous la coupe forme un groupe : sa branche reste visible
            couleur_enfant = couleur_branche if (sous_coupe or enfant["gauche"] is None) else couleur_haut
            vx, vy = segments[couleur_enfant]
            vx.extend([enfant["x"], enfant["x"], None])
            vy.extend([enfant["hauteur"], y_fusion, None])
        dessiner(noeud["gauche"])
        dessiner(noeud["droite"])

    dessiner(racine)

    feuilles = []

    def _collecter(noeud):
        if noeud["gauche"] is None:
            feuilles.append(noeud)
            return
        _collecter(noeud["gauche"])
        _collecter(noeud["droite"])
    _collecter(racine)

    def _nom(feuille):
        if noms_pays is None or "indice_pays" not in feuille:
            return "Pays"
        return noms_pays[feuille["indice_pays"]]

    hauteur_max = racine["hauteur"] or 1.0
    y_bande = -hauteur_max * 0.07
    fig = go.Figure()

    # Groupes de la CAH : bandes de fond alternées et lettres
    if hauteur_coupe is not None and groupe_par_feuille is not None:
        positions = {}
        for f in feuilles:
            positions.setdefault(groupe_par_feuille.get(f["x"], 0), []).append(f)
        groupes_ordonnes = sorted(positions.values(), key=lambda membres: min(m["x"] for m in membres))
        for i, membres in enumerate(groupes_ordonnes):
            x_min, x_max = min(m["x"] for m in membres), max(m["x"] for m in membres)
            fig.add_vrect(
                x0=x_min - 0.5, x1=x_max + 0.5, layer="below", line_width=0,
                fillcolor="rgba(107,142,35,0.13)" if i % 2 == 0 else "rgba(212,160,23,0.12)",
            )
            lettre = chr(ord("A") + i)
            detail = _nom(membres[0]) if len(membres) == 1 else f"{len(membres)} pays"
            fig.add_annotation(
                x=(x_min + x_max) / 2, y=hauteur_coupe, yshift=14 + (i % 2) * 18,
                text=f"<b>{lettre}</b> · {detail}", showarrow=False,
                font=dict(size=12, color="#4d6519"), bgcolor="rgba(255,255,255,0.85)",
                bordercolor="rgba(77,101,25,0.25)", borderpad=3,
            )

    for couleur, (x_vals, y_vals) in segments.items():
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals, mode="lines", line=dict(color=couleur, width=1.6),
            hoverinfo="skip", showlegend=False,
        ))

    # Rangée de carrés : groupe k-means de chaque pays (mêmes couleurs que le nuage)
    if groupes_kmeans is not None:
        groupes_vus = sorted({int(groupes_kmeans[f["indice_pays"]]) for f in feuilles if "indice_pays" in f})
        for g in groupes_vus:
            membres = [f for f in feuilles if "indice_pays" in f and int(groupes_kmeans[f["indice_pays"]]) == g]
            fig.add_trace(go.Scatter(
                x=[m["x"] for m in membres], y=[y_bande] * len(membres), mode="markers",
                marker=dict(symbol="square", size=10, color=COULEURS_CLUSTER[g % len(COULEURS_CLUSTER)],
                            line=dict(width=1, color="white")),
                name=f"Groupe {g + 1}", legendgroup=f"g{g}",
                text=[_nom(m) for m in membres],
                hovertemplate="%{text}<br>Groupe " + str(g + 1) + " (k-means)<extra></extra>",
            ))
    else:
        fig.add_trace(go.Scatter(
            x=[f["x"] for f in feuilles], y=[0] * len(feuilles), mode="markers",
            marker=dict(size=9, color="rgba(0,0,0,0)"),
            text=[_nom(f) for f in feuilles], hovertemplate="%{text}<extra></extra>", showlegend=False,
        ))

    if hauteur_coupe is not None:
        fig.add_hline(y=hauteur_coupe, line_dash="dash", line_color=GAEA_CORP["accent_rouge"], line_width=1.5)
    fig = theme_plotly(fig, hauteur=480, titre_x=None, titre_y="Distance de fusion",
                       legende=groupes_kmeans is not None)
    fig.update_layout(hovermode="closest", legend=dict(title=dict(text="Groupe k-means (carrés) : ")))
    fig.update_xaxes(showticklabels=False, showline=False, ticks="")
    fig.update_yaxes(range=[y_bande * 1.9, hauteur_max * 1.08])
    return fig


# Libellés des trois variables du cluster, et la façon de décrire un pays
# qui a une valeur haute ou basse sur chacune (pour interpréter les axes).
VARIABLES_ACP = {
    "log_pib": {"libelle": "PIB/habitant (log)", "haut": "pays riches", "bas": "pays moins riches",
                "nom": "richesse (PIB par habitant)", "nom_article": "la richesse (PIB par habitant)"},
    "part_renouvelables_dans_electricite": {"libelle": "Renouvelables (%)", "haut": "électricité renouvelable",
                                            "bas": "électricité peu renouvelable",
                                            "nom": "part de renouvelables", "nom_article": "la part de renouvelables"},
    "intensite_carbone_electricite": {"libelle": "Intensité carbone", "haut": "électricité carbonée",
                                      "bas": "électricité décarbonée", "nom": "intensité carbone",
                                      "nom_article": "l'intensité carbone"},
}


def acp_complete_np(X, variables):
    """Sorties complètes de l'ACP, avec la même décomposition que
    acp_projection_np (donc les mêmes axes et les mêmes signes) : valeurs
    propres, part de variance de chaque axe et corrélations
    variables/axes. Les variables étant centrées-réduites, la corrélation
    d'une variable avec un axe vaut vecteur propre x racine(valeur propre)."""
    cov = np.cov(X, rowvar=False)
    valeurs_propres, vecteurs_propres = np.linalg.eigh(cov)
    ordre = np.argsort(valeurs_propres)[::-1]
    valeurs_propres = valeurs_propres[ordre]
    vecteurs_propres = vecteurs_propres[:, ordre]
    total = valeurs_propres.sum()
    return {
        "variables": list(variables),
        "valeurs_propres": valeurs_propres,
        "pourcentages": valeurs_propres / total * 100 if total else valeurs_propres * 0,
        "correlations": vecteurs_propres * np.sqrt(np.clip(valeurs_propres, 0, None)),
    }


def graphique_eboulis(acp):
    pourcentages = acp["pourcentages"]
    axes = [f"Dim {i + 1}" for i in range(len(pourcentages))]
    couleurs = [GAEA_CORP["accent_dark"] if i < 2 else "#c2baa9" for i in range(len(pourcentages))]
    fig = go.Figure(go.Bar(
        x=axes, y=pourcentages, marker_color=couleurs,
        text=[fmt_fr(v, suffixe=" %") for v in pourcentages], textposition="outside",
        hovertemplate="%{x} : %{y:.1f} % de la variance<extra></extra>",
    ))
    fig = theme_plotly(fig, hauteur=340, titre_y="Part de la variance (%)", legende=False)
    fig.update_yaxes(range=[0, max(pourcentages) * 1.2])
    return fig


def graphique_cercle_correlations(acp):
    correlations = acp["correlations"]
    pourcentages = acp["pourcentages"]
    fig = go.Figure()
    angles = np.linspace(0, 2 * np.pi, 200)
    fig.add_trace(go.Scatter(x=np.cos(angles), y=np.sin(angles), mode="lines",
                             line=dict(color="rgba(46,43,38,0.35)", width=1.2), hoverinfo="skip", showlegend=False))
    fig.add_hline(y=0, line_color="rgba(46,43,38,0.2)", line_width=1)
    fig.add_vline(x=0, line_color="rgba(46,43,38,0.2)", line_width=1)
    couleurs = [GAEA_CORP["brown"], GAEA_CORP["accent_dark"], GAEA_CORP["accent_rouge"]]
    for j, variable in enumerate(acp["variables"]):
        x, y = float(correlations[j, 0]), float(correlations[j, 1])
        couleur = couleurs[j % len(couleurs)]
        fig.add_annotation(x=x, y=y, ax=0, ay=0, xref="x", yref="y", axref="x", ayref="y",
                           showarrow=True, arrowhead=3, arrowsize=1.2, arrowwidth=2.4, arrowcolor=couleur, text="")
        if abs(x) > abs(y):
            # flèche plutôt horizontale : étiquette au-dessus, côté intérieur du cercle
            # à droite au-dessus de la flèche, à gauche en dessous : jamais de chevauchement au centre
            position = dict(xanchor="right" if x >= 0 else "left", yanchor="bottom" if x >= 0 else "top",
                            yshift=8 if x >= 0 else -8)
        else:
            position = dict(xanchor="left" if x >= 0 else "right", yanchor="bottom" if y >= 0 else "top",
                            xshift=6 if x >= 0 else -6)
        fig.add_annotation(
            x=x, y=y, text=f"<b>{VARIABLES_ACP[variable]['libelle']}</b>", showarrow=False,
            font=dict(size=12, color=couleur), **position,
        )
    fig = theme_plotly(
        fig, hauteur=380, legende=False,
        titre_x=fr(f"Dim 1 ({pourcentages[0]:.1f} %)"), titre_y=fr(f"Dim 2 ({pourcentages[1]:.1f} %)"),
    )
    fig.update_layout(hovermode="closest")
    fig.update_xaxes(range=[-1.7, 1.7], zeroline=False, showgrid=False, constrain="domain")
    fig.update_yaxes(range=[-1.25, 1.25], zeroline=False, showgrid=False, scaleanchor="x", scaleratio=1,
                     constrain="domain")
    return fig


def _cote_axe(acp, k, signe):
    """Description du côté positif (signe=+1) ou négatif (-1) de l'axe k.
    On préfère une variable fortement corrélée dans le même sens que ce
    côté (« électricité carbonée » plutôt que « peu renouvelable ») ;
    sinon, la variable la plus corrélée à l'axe, lue en bas."""
    correlations = acp["correlations"][:, k]
    candidates = [j for j in range(len(correlations))
                  if abs(correlations[j]) >= 0.5 and (correlations[j] > 0) == (signe > 0)]
    if candidates:
        j = max(candidates, key=lambda i: abs(correlations[i]))
        return VARIABLES_ACP[acp["variables"][j]]["haut"]
    j = int(np.argmax(np.abs(correlations)))
    haut = (correlations[j] > 0) == (signe > 0)
    return VARIABLES_ACP[acp["variables"][j]]["haut" if haut else "bas"]


def texte_interpretation_acp(acp):
    lignes = []
    for k, (cote_plus, cote_moins) in enumerate([("→", "←"), ("↑", "↓")]):
        correlations = acp["correlations"][:, k]
        if np.max(np.abs(correlations)) < 0.5:
            continue
        fortes = sorted(
            [(acp["variables"][j], float(correlations[j])) for j in range(len(correlations))
             if abs(correlations[j]) >= 0.5],
            key=lambda t: -abs(t[1]),
        )
        detail = " et ".join(f"{VARIABLES_ACP[v]['nom_article']} (r = {r:+.2f})" for v, r in fortes)
        lignes.append(
            f"<b>Dim {k + 1}</b> ({fmt_fr(acp['pourcentages'][k])} %) : "
            f"{cote_moins} <b>{_cote_axe(acp, k, -1)}</b> &nbsp;·&nbsp; {cote_plus} <b>{_cote_axe(acp, k, +1)}</b>"
            f"<br><span style='opacity:0.8'>Axe porté par {detail}.</span>"
        )

    # Lien entre les deux dimensions : corrélation de la variable de Dim 2 avec Dim 1
    j_dim2 = int(np.argmax(np.abs(acp["correlations"][:, 1])))
    r_croise = float(acp["correlations"][j_dim2, 0])
    cumul = acp["pourcentages"][0] + acp["pourcentages"][1]
    nom_lien = VARIABLES_ACP[acp["variables"][j_dim2]]["nom_article"]
    nom_lien = nom_lien[0].upper() + nom_lien[1:]
    if abs(r_croise) < 0.3:
        lien = (f"{nom_lien} n'est presque pas liée au type d'électricité "
                f"(r = {r_croise:+.2f} avec Dim 1) : <b>être riche ne rend pas, à lui seul, l'électricité plus verte</b>.")
    else:
        lien = (f"{nom_lien} est aussi liée au type d'électricité "
                f"(r = {r_croise:+.2f} avec Dim 1).")
    lignes.append(f"À eux deux, ces axes résument <b>{fmt_fr(cumul)} %</b> de l'information. {lien}")
    return "<br><br>".join(lignes)


def acp_projection_np(X):
    """Projette les points (déjà centrés-réduits) sur leurs deux
    premières composantes principales, via la décomposition en valeurs
    propres de numpy (np.linalg.eigh, adaptée aux matrices symétriques
    comme la matrice de covariance) -- même principe que la version
    Python native du tableau de bord natif (méthode de Jacobi dans
    app.py), ici via l'algèbre linéaire de numpy plutôt que réimplémentée
    à la main, puisque cette version s'appuie déjà largement sur numpy."""
    cov = np.cov(X, rowvar=False)
    valeurs_propres, vecteurs_propres = np.linalg.eigh(cov)
    ordre = np.argsort(valeurs_propres)[::-1]
    valeurs_propres = valeurs_propres[ordre]
    vecteurs_propres = vecteurs_propres[:, ordre]
    total = valeurs_propres.sum()
    variance = [
        float(valeurs_propres[0] / total * 100) if total else 0.0,
        float(valeurs_propres[1] / total * 100) if total else 0.0,
    ]
    projection = X @ vecteurs_propres[:, :2]
    return projection[:, 0], projection[:, 1], variance


def _hauteur_coupe_np(fusions, k):
    """Hauteur (à mi-chemin entre deux fusions consécutives) à laquelle
    couper le dendrogramme pour obtenir exactement k groupes -- même
    logique que app.py."""
    n_feuilles = len(fusions) + 1
    if not fusions or k >= n_feuilles:
        return 0.0
    if k <= 1:
        return fusions[-1][2]
    index = n_feuilles - k
    hauteur_apres = fusions[index][2] if index < len(fusions) else fusions[-1][2]
    hauteur_avant = fusions[index - 1][2] if index - 1 >= 0 else 0.0
    return (hauteur_apres + hauteur_avant) / 2


@st.cache_data(show_spinner="Recalcul du clustering pour ce nombre de groupes…")
def clustering_pour_k(_points, k):
    affectations, _centres, _inertie = _kmeans_np(_points, k, graine=42)
    silhouette = _silhouette_moyenne_np(_points, affectations, k)
    return affectations, silhouette


def executer_clustering_socio_energetique(_df):
    """Même méthodologie que le tableau de bord natif (voir app.py) :
    PIB par habitant (PPA) en échelle logarithmique -- sa distribution
    très asymétrique écraserait sinon la distance calculée face aux deux
    autres indicateurs --, part des renouvelables et intensité carbone de
    l'électricité, à la dernière année disponible par pays où les trois
    indicateurs sont renseignés simultanément. Variables centrées-réduites
    avant clustering ; nombre de groupes choisi par la méthode du coude.
    """
    d = _df[["pays", "annee", "pib_par_habitant", "part_renouvelables_dans_electricite",
             "intensite_carbone_electricite"]].dropna()
    d = d[d["pib_par_habitant"] > 0]
    if len(d) < 6:
        return None

    d = d.sort_values("annee").groupby("pays", as_index=False).last()
    d["log_pib"] = np.log(d["pib_par_habitant"])

    variables = ["log_pib", "part_renouvelables_dans_electricite", "intensite_carbone_electricite"]
    X = d[variables].to_numpy(dtype=float)
    moyennes = X.mean(axis=0)
    ecarts = X.std(axis=0, ddof=1)
    ecarts[ecarts == 0] = 1.0
    X_std = (X - moyennes) / ecarts

    k_optimal, inerties = _choisir_k_optimal_np(X_std)
    affectations, _centres, _inertie = _kmeans_np(X_std, k_optimal, graine=42)
    silhouette = _silhouette_moyenne_np(X_std, affectations, k_optimal)

    d = d.reset_index(drop=True)
    d["groupe"] = affectations

    return {
        "jeu": d, "k_optimal": k_optimal, "inerties": inerties, "nb_pays": len(d),
        "silhouette": silhouette, "points": X_std,
    }


def graphique_cluster_coude(resultat):
    inerties = resultat["inerties"]
    k_optimal = resultat["k_optimal"]
    ks = sorted(inerties.keys())
    valeurs = [inerties[k] for k in ks]
    couleurs = [GAEA_CORP["accent_rouge"] if k == k_optimal else GAEA_CORP["accent"] for k in ks]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ks, y=valeurs, mode="lines+markers",
        line=dict(color=GAEA_CORP["accent"], width=2),
        marker=dict(size=[12 if k == k_optimal else 7 for k in ks], color=couleurs),
        hovertemplate="k = %{x}<br>Inertie = %{y:.1f}<extra></extra>",
    ))
    fig = theme_plotly(fig, hauteur=380, titre_x="Nombre de groupes (k)", titre_y="Inertie", legende=False)
    return fig


def graphique_cluster_nuage_acp(jeu, dim1, dim2, variance, affectations, k, acp=None):
    """Nuage de points projeté sur les deux premières composantes
    principales (ACP) plutôt que sur deux variables brutes -- exploite
    les trois variables combinées (PIB, renouvelables, intensité) au
    lieu de deux seulement."""
    d = jeu.copy()
    d["pays_fr"] = d["pays"].map(NOMS_FR).fillna(d["pays"])
    d["Dim1"] = dim1
    d["Dim2"] = dim2
    d["Groupe"] = "Groupe " + (pd.Series(affectations, index=d.index) + 1).astype(str)
    couleurs_map = {f"Groupe {i+1}": COULEURS_CLUSTER[i % len(COULEURS_CLUSTER)] for i in range(k)}

    fig = px.scatter(
        d, x="Dim1", y="Dim2",
        color="Groupe", color_discrete_map=couleurs_map,
        category_orders={"Groupe": [f"Groupe {i+1}" for i in range(k)]},
        hover_name="pays_fr",
        hover_data={
            "Dim1": False, "Dim2": False, "Groupe": False,
            "pib_par_habitant": ":.0f", "part_renouvelables_dans_electricite": ":.1f",
            "intensite_carbone_electricite": ":.0f",
        },
    )
    fig.update_traces(marker=dict(size=10, opacity=0.75, line=dict(width=1, color="white")))
    fig = theme_plotly(
        fig, hauteur=520,
        titre_x=fr(f"Dim 1 ({variance[0]:.1f} % de variance)"),
        titre_y=fr(f"Dim 2 ({variance[1]:.1f} % de variance)"),
    )
    if acp is not None:
        # bande vide en haut et en bas : les étiquettes des coins ne cachent aucun pays
        y_min, y_max = float(np.min(dim2)), float(np.max(dim2))
        marge = (y_max - y_min) * 0.14
        fig.update_yaxes(range=[y_min - marge, y_max + marge])
        # profil de chaque coin du plan, déduit des corrélations de l'ACP
        for sx, sy, xa, ya in [(-1, 1, "left", "top"), (1, 1, "right", "top"),
                               (-1, -1, "left", "bottom"), (1, -1, "right", "bottom")]:
            fig.add_annotation(
                xref="x domain", yref="y domain", x=0.01 if sx < 0 else 0.99, y=0.98 if sy > 0 else 0.02,
                xanchor=xa, yanchor=ya, showarrow=False,
                text=f"<i>{_cote_axe(acp, 1, sy).capitalize()} · {_cote_axe(acp, 0, sx)}</i>",
                font=dict(size=11, color="rgba(46,43,38,0.6)"), bgcolor="rgba(255,255,255,0.45)", borderpad=4,
            )
    return fig


@st.cache_data(show_spinner="Classement des 5 premiers producteurs par continent…")
def calculer_top5_par_continent(_df):
    """
    Sélectionne, pour chaque continent, les 5 pays ayant la plus forte
    production totale d'électricité (dernière année disponible par pays)
    -- reproduit exactement calculer_top5_par_continent() du tableau de
    bord natif (app.py), pour donner les mêmes résultats.
    """
    if "production_totale_electricite" not in _df.columns:
        return {c: [] for c in CONTINENTS_DISPONIBLES + ["Monde"]}

    dernieres_lignes = (
        _df.sort_values("annee")
        .dropna(subset=["production_totale_electricite"])
        .groupby("pays", as_index=False)
        .last()
    )
    dernieres_lignes["continent"] = dernieres_lignes["pays"].map(continent_de)

    resultat = {}
    for continent in CONTINENTS_DISPONIBLES:
        sous = dernieres_lignes[dernieres_lignes["continent"] == continent]
        top5 = sous.sort_values("production_totale_electricite", ascending=False).head(5)
        resultat[continent] = top5["pays"].tolist()

    top5_monde = dernieres_lignes.sort_values("production_totale_electricite", ascending=False).head(5)
    resultat["Monde"] = top5_monde["pays"].tolist()
    return resultat



@st.cache_data(show_spinner="Préparation de la carte animée (206 pays × 35 années)…")
def preparer_donnees_carte_animee(_df, col_indicateur):
    """Prépare les données pour la carte choroplèthe animée (toutes années,
    206 pays) -- mis en cache car recalculé sinon à chaque interaction dans
    la barre latérale, même pour un onglet différent de la Carte."""
    donnees = _df[
        _df[col_indicateur].notna() & _df["code_iso"].notna() & _df["annee"].notna()
    ][["pays", "code_iso", "annee", col_indicateur]].copy()
    donnees["annee"] = donnees["annee"].astype(int)
    return donnees.sort_values("annee")


def regression_numpy(annees, valeurs):
    """
    Régression linéaire simple via numpy.polyfit (degré 1), équivalent
    à la fonction calculer_regression() du tableau de bord natif, mais
    ici en s'appuyant sur NumPy plutôt que sur une implémentation manuelle
    — pour rester cohérent avec la stack Pandas/NumPy demandée.
    Retourne (pente, ordonnée, r2) ou (None, None, None) si non calculable.
    """
    masque = ~(np.isnan(annees) | np.isnan(valeurs))
    x, y = annees[masque], valeurs[masque]
    if len(x) < 3:
        return None, None, None

    pente, ordonnee = np.polyfit(x, y, deg=1)
    y_predit = pente * x + ordonnee
    ss_res = np.sum((y - y_predit) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else None
    return pente, ordonnee, r2


def regression_logistique_numpy(annees, valeurs, plafond=100.0):
    """Courbe en S bornée par un plafond (100 % pour une part), même méthode
    que ajuster_courbe(mode="logistique") du tableau de bord natif : on
    linéarise par la transformation logit z = ln(v / (plafond - v)), puis on
    ajuste une droite sur z avec numpy.polyfit. Le R² est recalculé sur
    l'échelle d'origine pour rester lisible. Retourne (pente, ordonnée, r2)."""
    masque = ~(np.isnan(annees) | np.isnan(valeurs))
    x, y = annees[masque], valeurs[masque]
    if len(x) < 3:
        return None, None, None
    y_borne = np.clip(y, 0.5, plafond - 0.5)
    z = np.log(y_borne / (plafond - y_borne))
    pente, ordonnee = np.polyfit(x, z, deg=1)
    y_predit = predire_modele("logistique", pente, ordonnee, x, plafond)
    ss_res = np.sum((y - y_predit) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else None
    return pente, ordonnee, r2


def predire_modele(mode, pente, ordonnee, annees, plafond=100.0):
    """Valeurs prédites par la droite ou par la courbe en S."""
    annees = np.asarray(annees, dtype=float)
    if mode == "logistique":
        z = np.clip(pente * annees + ordonnee, -700, 700)
        return plafond / (1 + np.exp(-z))
    return pente * annees + ordonnee


def backtest_numpy(annees, valeurs, n_annees_test=5, mode="lineaire"):
    """Équivalent NumPy de valider_regression_backtest() (voir app.py) : on
    ajuste le modèle sans les n dernières années, puis on mesure l'erreur
    moyenne de prédiction sur ces années masquées."""
    ordre = np.argsort(annees)
    annees, valeurs = annees[ordre], valeurs[ordre]
    masque = ~(np.isnan(annees) | np.isnan(valeurs))
    annees, valeurs = annees[masque], valeurs[masque]

    if len(annees) < n_annees_test + 3:
        return None

    a_train, v_train = annees[:-n_annees_test], valeurs[:-n_annees_test]
    a_test, v_test = annees[-n_annees_test:], valeurs[-n_annees_test:]

    ajuster = regression_logistique_numpy if mode == "logistique" else regression_numpy
    pente, ordonnee, _ = ajuster(a_train, v_train)
    if pente is None:
        return None

    v_predit = predire_modele(mode, pente, ordonnee, a_test)
    mae = np.mean(np.abs(v_predit - v_test))
    return {"mae": mae, "n_test": len(a_test)}


def beta_fraction_continue(a, b, x):
    """Fraction continue utilisée pour approximer la fonction bêta incomplète
    (reprise à l'identique de app.py, pour une p-valeur cohérente entre les
    deux versions du tableau de bord, sans dépendance à SciPy)."""
    max_iter = 200
    eps = 3e-14
    fpmin = 1e-300

    qab = a + b
    qap = a + 1
    qam = a - 1
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d

    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c

        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break

    return h


def beta_incomplete_reguliere(x, a, b):
    """Fonction bêta incomplète régularisée I_x(a,b), sans SciPy."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    log_bt = (
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log(1.0 - x)
    )
    bt = math.exp(log_bt)
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * beta_fraction_continue(a, b, x) / a
    else:
        return 1.0 - bt * beta_fraction_continue(b, a, 1.0 - x) / b


def p_valeur_bilaterale(t, ddl):
    """P-valeur bilatérale pour un test t, à partir de la loi de Student."""
    if ddl is None or ddl <= 0:
        return None
    x = ddl / (ddl + t * t)
    ib = beta_incomplete_reguliere(x, ddl / 2.0, 0.5)
    return ib  # déjà bilatérale par construction (symétrie de la loi de Student)


def student_t_cdf(t, ddl):
    """Fonction de répartition de la loi de Student à ddl degrés de liberté
    (reprise à l'identique de app.py)."""
    if ddl is None or ddl <= 0:
        return None
    x = ddl / (ddl + t * t)
    ib = beta_incomplete_reguliere(x, ddl / 2.0, 0.5)
    if t >= 0:
        return 1.0 - 0.5 * ib
    else:
        return 0.5 * ib


def p_valeur_unilaterale(t, ddl):
    """P-valeur unilatérale (test orienté H1 : différence > 0), identique
    à la logique du test 3 natif (app.py)."""
    cdf = student_t_cdf(t, ddl)
    if cdf is None:
        return None
    return 1.0 - cdf


def test_apparie_numpy(valeurs_debut, valeurs_fin):
    """
    Test t apparié orienté (H1 : la valeur a augmenté), identique à
    test_evolution_part_renouvelables() du tableau de bord natif (app.py).
    Retourne (t, ddl, p_unilaterale) ou (None, None, None).
    """
    diff = np.asarray(valeurs_fin, dtype=float) - np.asarray(valeurs_debut, dtype=float)
    diff = diff[~np.isnan(diff)]
    n = len(diff)
    if n < 2:
        return None, None, None
    moyenne_diff = np.mean(diff)
    ecart_type_diff = np.std(diff, ddof=1)
    if ecart_type_diff == 0:
        return None, None, None
    t = moyenne_diff / (ecart_type_diff / np.sqrt(n))
    ddl = n - 1
    p = p_valeur_unilaterale(t, ddl)
    return t, ddl, p


def welch_ttest_numpy(groupe1, groupe2):
    """
    Test t de Welch, orienté (H1 : moyenne groupe1 < moyenne groupe2),
    identique à test_comparaison_groupes_renouvelables() du tableau de
    bord natif (app.py) : teste si les pays à forte part de renouvelables
    (groupe1) ont une intensité carbone significativement plus faible.
    Retourne (t, ddl_approx, p_unilaterale) ou (None, None, None).
    """
    n1, n2 = len(groupe1), len(groupe2)
    if n1 < 2 or n2 < 2:
        return None, None, None
    m1, m2 = np.mean(groupe1), np.mean(groupe2)
    v1, v2 = np.var(groupe1, ddof=1), np.var(groupe2, ddof=1)
    se = np.sqrt(v1 / n1 + v2 / n2)
    if se == 0:
        return None, None, None
    t = (m1 - m2) / se
    ddl = (v1 / n1 + v2 / n2) ** 2 / (
        (v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1)
    )
    cdf = student_t_cdf(t, ddl)
    p = cdf if cdf is not None else None  # test orienté : H1 = m1 < m2
    return t, ddl, p


def correlation_pearson_avec_p(x, y):
    """
    Corrélation de Pearson avec test de significativité (H0 : r = 0),
    cohérent avec la p-valeur bilatérale déjà utilisée ailleurs dans
    cette application (fonction beta incomplète régularisée, sans SciPy).
    Retourne (r, n, t, ddl, p) ou (None, ...) si non calculable.
    """
    n = len(x)
    if n < 3:
        return None, n, None, None, None
    r = np.corrcoef(x, y)[0, 1]
    if abs(r) >= 1.0:
        return r, n, None, n - 2, 0.0
    ddl = n - 2
    t = r * np.sqrt(ddl / (1 - r ** 2))
    p = p_valeur_bilaterale(t, ddl)
    return r, n, t, ddl, p


@st.cache_data(show_spinner="Analyse de décalage temporel (décalage renouvelables / intensité carbone)…")
def calculer_precedence_temporelle(_df):
    """Analyse de décalage temporel par corrélation croisée décalée,
    entre la variation annuelle (Δ) de la part des renouvelables et celle
    de l'intensité carbone de l'électricité, groupée sur l'ensemble des
    206 pays de la base plutôt que pays par pays : avec seulement une
    trentaine de points par pays après le passage aux variations
    annuelles, une analyse pays par pays serait trop bruitée pour être
    fiable -- même logique que l'extension du backtest à 206 pays du
    tableau de bord natif.

    Travaille sur les VARIATIONS annuelles (Δ), et non sur les niveaux,
    pour éviter la corrélation fallacieuse entre deux séries qui
    partagent simplement une tendance de long terme (renouvelables en
    hausse quasi continue, intensité carbone en baisse quasi continue sur
    1990-2024).

    Pour chaque décalage k (-5 à +5 ans), calcule la corrélation entre
    Δrenouvelables à l'année t et Δintensité carbone à l'année t+k,
    poolée sur tous les pays et toutes les années disponibles.
    """
    lags = list(range(-5, 6))
    d = _df[["pays", "annee", "part_renouvelables_dans_electricite", "intensite_carbone_electricite"]].dropna()
    d = d.sort_values(["pays", "annee"]).reset_index(drop=True)
    d["annee_prec"] = d.groupby("pays")["annee"].shift(1)
    d["renouv_prec"] = d.groupby("pays")["part_renouvelables_dans_electricite"].shift(1)
    d["intensite_prec"] = d.groupby("pays")["intensite_carbone_electricite"].shift(1)
    d = d[d["annee"] - d["annee_prec"] == 1].copy()
    d["delta_renouv"] = d["part_renouvelables_dans_electricite"] - d["renouv_prec"]
    d["delta_intensite"] = d["intensite_carbone_electricite"] - d["intensite_prec"]
    deltas = d[["pays", "annee", "delta_renouv", "delta_intensite"]].reset_index(drop=True)

    par_lag = {}
    for k in lags:
        decale = deltas[["pays", "annee", "delta_intensite"]].copy()
        decale["annee"] = decale["annee"] - k
        decale = decale.rename(columns={"delta_intensite": "delta_intensite_decale"})
        fusion = deltas.merge(decale, on=["pays", "annee"], how="inner")
        n = len(fusion)
        if n < 30:
            par_lag[k] = {"r": None, "n": n, "p": None}
            continue
        r, n_reel, _t, _ddl, p = correlation_pearson_avec_p(
            fusion["delta_renouv"].to_numpy(dtype=float),
            fusion["delta_intensite_decale"].to_numpy(dtype=float),
        )
        par_lag[k] = {"r": r, "n": n_reel, "p": p}

    lag_optimal, r_optimal = None, None
    for k, res in par_lag.items():
        if res["r"] is None:
            continue
        if r_optimal is None or res["r"] < r_optimal:
            r_optimal, lag_optimal = res["r"], k

    return {"par_lag": par_lag, "lag_optimal": lag_optimal, "resultat_optimal": par_lag.get(lag_optimal)}


def _qualifier_force_r(r):
    abs_r = abs(r)
    if abs_r >= 0.5:
        return "lien fort"
    elif abs_r >= 0.3:
        return "lien modéré"
    elif abs_r >= 0.1:
        return "lien faible"
    else:
        return "lien quasi nul"


def _conclusion_par_lag(k, info, lag_optimal):
    """Phrase de conclusion propre à ce décalage, affichée au survol de
    la barre correspondante -- rappelle que la significativité (p-valeur)
    et la force du lien (r) sont deux choses différentes : avec un
    échantillon aussi grand (plusieurs milliers de paires), même un r
    très faible ressort comme statistiquement significatif."""
    r, n, p = info.get("r"), info.get("n"), info.get("p")
    if r is None:
        return f"Décalage {k:+d} an(s)<br>Pas assez de données (n < 30)"

    force = _qualifier_force_r(r)
    significatif = p is not None and p < 0.05
    ligne1 = fr(f"Décalage {k:+d} an(s) : r = {r:.3f} ({force})")
    ligne2 = f"n = {n:,}".replace(",", " ") + f" · p {'< 0,05 (significatif)' if significatif else '≥ 0,05 (non significatif)'}"

    lignes = [ligne1, ligne2]
    if significatif and abs(r) < 0.1:
        lignes.append("Échantillon très grand : même un lien faible ressort significatif ici,")
        lignes.append("ce n'est pas un lien fort en pratique")
    if k == lag_optimal:
        lignes.append("→ décalage le plus corrélé de tous ceux testés")

    return "<br>".join(lignes)


def graphique_precedence_temporelle(resultat):
    par_lag = resultat["par_lag"]
    lag_optimal = resultat["lag_optimal"]
    lags = sorted(par_lag.keys())
    valeurs_r = [par_lag[k]["r"] for k in lags]
    couleurs = [GAEA_CORP["accent_rouge"] if k == lag_optimal else GAEA_CORP["accent"] for k in lags]
    textes = [f"{r:.2f}".replace("-0.00", "0.00").replace(".", ",") if r is not None else "n/d" for r in valeurs_r]
    valeurs_affichees = [r if r is not None else 0 for r in valeurs_r]
    conclusions = [_conclusion_par_lag(k, par_lag[k], lag_optimal) for k in lags]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[str(k) if k <= 0 else f"+{k}" for k in lags],
        y=valeurs_affichees,
        marker=dict(color=couleurs),
        text=textes,
        textposition="outside",
        customdata=conclusions,
        hovertemplate="%{customdata}<extra></extra>",
    ))
    fig.add_hline(y=0, line_width=1, line_color="#999999")
    fig = theme_plotly(fig, hauteur=420, titre_x="Décalage (années)", titre_y="Corrélation r")
    fig.update_layout(showlegend=False)
    return fig


def texte_precedence_temporelle(resultat):
    par_lag = resultat["par_lag"]
    lag_optimal = resultat["lag_optimal"]
    opt = resultat["resultat_optimal"]
    r0_info = par_lag.get(0, {})
    r0 = r0_info.get("r")

    if lag_optimal is None or opt is None or opt["r"] is None:
        return "Les données disponibles ne permettent pas de dégager un décalage temporel fiable."

    if lag_optimal > 0:
        lecture = (f"le lien le plus fort apparaît avec <b>{lag_optimal} an(s) de décalage</b> : la baisse de "
                   "l'intensité carbone suit la hausse des renouvelables.")
    elif lag_optimal < 0:
        lecture = (f"le lien le plus fort apparaît à {lag_optimal} an(s), ce qui serait contre-intuitif : "
                   "probablement un artefact statistique.")
    else:
        lecture = "le lien le plus fort reste <b>la même année</b> : l'effet est surtout immédiat."

    r0_texte = fmt_fr(r0, decimales=2) if r0 is not None else "n/d"
    return (
        f"Sur les variations annuelles, r = {r0_texte} sans décalage ; {lecture} "
        "<i>Les deux indicateurs sont en partie liés mécaniquement : signal indicatif, pas une preuve de "
        "causalité.</i>"
    )


def classer_pays_typologie(row):
    """
    Reproduit exactement la logique de classement du tableau de bord natif
    (fonction de calcul de la typologie des pays dans app.py), appliquée
    ici ligne par ligne sur un DataFrame Pandas via .apply().
    """
    renouv = row.get("part_renouvelables_dans_electricite")
    fossile = row.get("part_fossiles_dans_electricite")
    intensite = row.get("intensite_carbone_electricite")
    co2_total = row.get("emissions_co2")
    prod_renouv = row.get("electricite_renouvelable")
    hausse = row.get("hausse_renouvelables_depuis_2000")

    if pd.notna(renouv) and pd.notna(intensite) and renouv >= 70 and intensite <= 200:
        return "Très renouvelable et peu carboné"
    if pd.notna(fossile) and pd.notna(intensite) and fossile >= 70 and intensite >= 500:
        return "Mix fossile et carboné"
    if pd.notna(hausse) and hausse >= 25:
        return "Transition rapide"
    if pd.notna(co2_total) and pd.notna(prod_renouv) and co2_total >= 500 and prod_renouv >= 100:
        return "Grand émetteur avec forte production renouvelable"
    return "Profil intermédiaire"


# ==============================================================
# INTERFACE STREAMLIT
# ==============================================================

st.set_page_config(page_title="Trends — Énergies renouvelables | gaea21", layout="wide", page_icon=":material/eco:")

# ---------------------------------------------------------------
# Décourage la traduction automatique du navigateur : certains
# navigateurs (Chrome notamment) traduisent le texte affiché en
# cachette, ce qui modifie le DOM en dehors du contrôle de React (le
# moteur de rendu de Streamlit) et provoque des erreurs "removeChild"
# aléatoires (le nœud que React essaie de retirer a déjà été déplacé
# par la traduction). Un premier essai avait inséré la balise
# <meta name="google" content="notranslate"> via st.markdown, mais
# celle-ci atterrit dans le <body> -- Chrome ne regarde cette balise
# que dans le <head>, au moment du chargement initial de la page, donc
# cette version n'avait aucun effet réel. On la réinjecte donc dans le
# vrai <head> du document PARENT via st.iframe (même mécanisme
# que pour la PWA ci-dessous), en ajoutant aussi l'attribut
# translate="no" sur <html> pour Firefox/Safari. Cela reste un
# "best-effort" : si le souci persiste malgré tout, désactiver
# manuellement la traduction du navigateur pour cette page (icône de
# traduction dans la barre d'adresse) reste le moyen le plus fiable.
# ---------------------------------------------------------------
st.iframe(
    """
    <script>
    (function() {
        // Bloc technique sans contenu : on le sort de la page pour qu'il ne laisse ni trait ni marge.
        const bloc = window.frameElement.closest('.stElementContainer');
        Object.assign(bloc.style, { position: 'absolute', height: '0', overflow: 'hidden' });
        // Sur Streamlit Community Cloud, l'application est elle-même dans un cadre : window.top
        // est alors la page visitée, et window.parent le document de l'application.
        [window.parent.document, window.top.document].forEach(function (doc) {
            doc.documentElement.setAttribute('translate', 'no');
            if (!doc.querySelector('meta[name="google"]')) {
                const meta = doc.createElement('meta');
                meta.name = 'google';
                meta.content = 'notranslate';
                doc.head.appendChild(meta);
            }
        });
    })();
    </script>
    """,
    height=1,
)

# ---------------------------------------------------------------
# PWA (Progressive Web App) : rend le dashboard "installable" sur
# l'écran d'accueil d'un téléphone ou d'un ordinateur (icône, plein
# écran, sans barre de navigateur), sans passer par un store
# d'applications. Streamlit ne permet pas de modifier le <head> du
# document directement (st.markdown insère dans le <body>) : on passe
# donc par st.iframe, qui exécute un vrai <script> dans une
# iframe, pour aller injecter le lien vers le manifeste et enregistrer
# le service worker dans le document PARENT (celui de la page
# Streamlit elle-même). Nécessite que les fichiers manifest.json,
# sw.js, icon-192.png et icon-512.png soient placés dans un dossier
# static/ à la racine du projet, avec [server]\nenableStaticServing =
# true ajouté à .streamlit/config.toml (voir la documentation Streamlit
# pour le service de fichiers statiques).
st.iframe(
    """
    <script>
    (function() {
        // Bloc technique sans contenu : on le sort de la page pour qu'il ne laisse ni trait ni marge.
        const bloc = window.frameElement.closest('.stElementContainer');
        Object.assign(bloc.style, { position: 'absolute', height: '0', overflow: 'hidden' });
        const doc = window.parent.document;
        const sommet = window.top.document;

        // C'est le manifeste de la page visitée qui décide du nom et de l'icône à
        // l'installation : sur le Cloud, on y remplace celui de Streamlit par le nôtre.
        let lien = sommet.querySelector('link[rel="manifest"]');
        if (!lien) {
            lien = sommet.createElement('link');
            lien.rel = 'manifest';
            sommet.head.appendChild(lien);
        }
        lien.href = new URL('app/static/manifest.json', window.parent.location.href).href;

        if (!sommet.querySelector('meta[name="theme-color"]')) {
            const meta = sommet.createElement('meta');
            meta.name = 'theme-color';
            meta.content = '#6b8e23';
            sommet.head.appendChild(meta);
        }

        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('app/static/sw.js').catch(function(err) {
                console.log('Service worker non enregistré :', err);
            });
        }
    })();
    </script>
    """,
    height=1,
)

# ---------------------------------------------------------------
# Traduction de "Select all" (menu déroulant du multiselect) :
# depuis Streamlit 1.55, le multiselect propose une option "Select all"
# codée en dur dans le composant, sans paramètre exposé côté Python
# pour la traduire ou la désactiver (vérifié dans la documentation et
# le forum officiel Streamlit -- une question identique y est restée
# sans réponse). Contournement "best-effort" : un MutationObserver
# traque le texte dans le document PARENT et le remplace dès qu'il
# apparaît, y compris dans le menu déroulant qui se construit
# dynamiquement à l'ouverture. Si une future version de Streamlit
# change ce texte ou sa structure interne, ce correctif cessera
# silencieusement de s'appliquer (sans erreur), sans rien casser.
# ---------------------------------------------------------------
st.iframe(
    """
    <script>
    (function() {
        // Bloc technique sans contenu : on le sort de la page pour qu'il ne laisse ni trait ni marge.
        const bloc = window.frameElement.closest('.stElementContainer');
        Object.assign(bloc.style, { position: 'absolute', height: '0', overflow: 'hidden' });
        const doc = window.parent.document;
        const TRADUCTIONS = { "Select all": "Tout sélectionner" };

        function traduireNoeudTexte(noeud) {
            const texte = noeud.nodeValue.trim();
            if (TRADUCTIONS[texte]) {
                noeud.nodeValue = noeud.nodeValue.replace(texte, TRADUCTIONS[texte]);
            }
        }

        function traduireDans(racine) {
            if (racine.nodeType === 3) {
                traduireNoeudTexte(racine);
                return;
            }
            if (racine.nodeType !== 1) return;
            const marcheur = doc.createTreeWalker(racine, NodeFilter.SHOW_TEXT, null);
            let noeud;
            while ((noeud = marcheur.nextNode())) {
                traduireNoeudTexte(noeud);
            }
        }

        traduireDans(doc.body);

        const observateur = new MutationObserver(function(mutations) {
            for (const mutation of mutations) {
                for (const noeud of mutation.addedNodes) {
                    traduireDans(noeud);
                }
            }
        });
        observateur.observe(doc.body, { childList: true, subtree: true });
    })();
    </script>
    """,
    height=1,
)

# ---------------------------------------------------------------
# Thème visuel Gaea (palette transmise par le coordinateur de
# projet, reprise à l'identique de son script tutoriel, étapes 5
# et 7 -- pour harmoniser l'apparence entre les différents
# tableaux de bord de l'équipe). Voir aussi .streamlit/config.toml
# pour le thème Streamlit natif (couleurs de fond/texte).
# ---------------------------------------------------------------
GAEA_CORP = {
    "bg":      "#f5f0e6",
    "panel":   "#e7dfcf",
    "text":    "#2e2b26",
    "accent":  "#6b8e23",
    "accent2": "#8f9779",
    "brown":   "#8b6b4a",
    "accent_dark": "#4d6519",
    "accent_rouge": "#7a1f3d",
    "card_bg": "#ffffff",
}

# Palette catégorielle Gaea, dérivée cette fois des 4 couleurs déjà
# utilisées pour les cartes KPI de cette version Streamlit (vert, marron,
# bordeaux, violet -- voir cartes_kpi() plus haut), complétée par 3
# teintes du même esprit (orange, doré, sarcelle) pour atteindre les 7
# couleurs nécessaires aux graphiques multi-pays. Assure une cohérence
# visuelle totale entre les cartes KPI et les courbes de chaque onglet.
GAEA_PALETTE = [
    GAEA_CORP["accent_rouge"],  # bordeaux -- comme les cartes "Objectif" / statistiques de test
    "#B45309",                  # orange
    GAEA_CORP["accent_dark"],   # vert -- comme les cartes "Valeur actuelle" / données réelles
    "#3D346B",                  # violet -- comme les cartes p-valeur
    GAEA_CORP["brown"],         # marron -- comme les cartes "Rythme historique" / projections
    "#D4A017",                  # doré
    "#2A9D8F",                  # sarcelle
]

# Rotation de couleurs "pleines" Gaea pour les cartes KPI et les
# graphiques à une seule série (mix, typologie) -- distinctes de la
# palette catégorielle multi-pays ci-dessus.
GAEA_KPI_COLORS = ["#6b8e23", "#8b6b4a", "#4d6519", "#8f9779", "#a8763e", "#5a7a1e"]

# ---------------------------------------------------------------
# Config Plotly partagée : masque toute la barre d'outils sauf le
# bouton d'export en image (📷), pour garder un rendu épuré tout en
# permettant de télécharger un graphique en PNG.
# ---------------------------------------------------------------
CONFIG_PLOTLY_EXPORT = {
    "displayModeBar": "hover",
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d",
        "autoScale2d", "resetScale2d", "hoverClosestCartesian", "hoverCompareCartesian",
        "toggleSpikelines", "hoverClosestGeo", "resetGeo", "zoomInGeo", "zoomOutGeo",
        "hoverClosestPie",
    ],
    "toImageButtonOptions": {"format": "png", "scale": 2},
}


def couleurs_categorielles(n):
    """Retourne n couleurs de la palette Gaea, en répétant si besoin."""
    if n <= 0:
        return []
    return [GAEA_PALETTE[i % len(GAEA_PALETTE)] for i in range(n)]


# ---------------------------------------------------------------
# Formatage des nombres à la française (virgule décimale, espace
# insécable comme séparateur de milliers) -- pour rester cohérent
# avec le rapport LaTeX et le tableau de bord natif, tous deux en
# français, plutôt que le formatage anglo-saxon par défaut de Python.
# ---------------------------------------------------------------
def fmt_fr(valeur, decimales=1, suffixe=""):
    if valeur is None or (isinstance(valeur, float) and math.isnan(valeur)):
        return "n/d"
    texte = f"{valeur:,.{decimales}f}"
    texte = texte.replace(",", "§").replace(".", ",").replace("§", "\u00a0")
    return f"{texte}{suffixe}"


def fr(texte):
    """Remplace le point décimal par une virgule dans un texte déjà
    formaté (« 86.0 points » -> « 86,0 points »), pour des nombres à la
    française partout dans l'interface, comme dans le rapport."""
    return re.sub(r"(?<=\d)\.(?=\d)", ",", texte)


# ---------------------------------------------------------------
# Rendu : cartes KPI stylées (remplace st.columns + st.metric par
# un vrai composant visuel HTML/CSS, dans l'esprit du bandeau KPI
# du tableau de bord natif, recoloré sur la palette Gaea).
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# Rendu : cartes KPI stylées. Utilise st.columns (layout natif et
# fiable de Streamlit) plutôt qu'une grille CSS pure : plus robuste
# face aux styles internes de Streamlit qui peuvent entrer en
# conflit avec un display:grid personnalisé.
# ---------------------------------------------------------------
def cartes_kpi(metriques):
    """metriques : liste de dicts {icone, valeur, label, delta?, couleur?} --
    par défaut la couleur tourne automatiquement sur GAEA_KPI_COLORS, mais
    "couleur" (un code hexadécimal) permet de la fixer explicitement pour
    une carte donnée -- utile pour faire correspondre une carte KPI à la
    couleur d'une courbe précise d'un graphique associé. "delta" est
    optionnel : {"texte": "...", "sens": "hausse"|"baisse"|"neutre"} pour
    afficher une flèche de tendance sous le libellé."""
    # Une seule rangée flexible (plutôt qu'une colonne Streamlit par
    # carte) : toutes les cartes prennent la hauteur de la plus haute.
    fleches = {"hausse": "▲", "baisse": "▼", "neutre": "▬"}
    cartes = []
    for i, m in enumerate(metriques):
        couleur = m.get("couleur") or GAEA_KPI_COLORS[i % len(GAEA_KPI_COLORS)]
        delta_html = ""
        if m.get("delta"):
            fleche = fleches.get(m["delta"]["sens"], "▬")
            delta_html = f'<div class="gaea-kpi-delta">{fleche} {m["delta"]["texte"]}</div>'
        cartes.append(
            f'<div class="gaea-kpi" style="background-color:{couleur};">'
            f'<div class="gaea-kpi-icon">{m["icone"]}</div>'
            f'<div class="gaea-kpi-valeur">{m["valeur"]}</div>'
            f'<div class="gaea-kpi-label">{m["label"]}</div>'
            f'{delta_html}'
            f'</div>'
        )
    st.markdown(f'<div class="gaea-kpi-rangee">{"".join(cartes)}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------
# Rendu : thème Plotly commun à tous les graphiques (typographie,
# fond transparent pour s'intégrer à la page, grille discrète,
# légende horizontale au-dessus du graphique).
# ---------------------------------------------------------------
def theme_plotly(fig, hauteur=420, titre_x=None, titre_y=None, legende=True):
    fig.update_layout(
        template="plotly_white",
        height=hauteur,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Inter, 'Segoe UI', sans-serif", size=13, color=GAEA_CORP["text"]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        separators=", ",
        hoverlabel=dict(bgcolor="white", bordercolor=GAEA_CORP["accent"],
                        font=dict(family="Inter, 'Segoe UI', sans-serif", size=12, color=GAEA_CORP["text"])),
        showlegend=legende,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=None,
                    bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(title=titre_x, showgrid=False, zeroline=False,
                   showline=True, linecolor="rgba(46,43,38,0.18)", ticks="outside", tickcolor="rgba(46,43,38,0.18)"),
        yaxis=dict(title=titre_y, showgrid=True, gridcolor="rgba(46,43,38,0.06)", griddash="dot", zeroline=False),
    )
    # Plotly mesure la légende avant le chargement de la police Inter, plus large :
    # sans cette marge, la dernière lettre de la dernière entrée était coupée.
    for trace in fig.data:
        if trace.name:
            trace.name = trace.name + "  "
    return fig


def graphique_lignes(tableau_pivot, titre_y, hauteur=420, lisse=True):
    """Graphique multi-séries (une ligne par pays) à partir d'un pivot
    Pandas (index = année, colonnes = pays)."""
    fig = go.Figure()
    couleurs = couleurs_categorielles(len(tableau_pivot.columns))
    for colonne, couleur in zip(tableau_pivot.columns, couleurs):
        fig.add_trace(go.Scatter(
            x=tableau_pivot.index, y=tableau_pivot[colonne],
            mode="lines+markers", name=colonne,
            line=dict(width=2.5, color=couleur, shape="spline" if lisse else "linear", smoothing=0.3),
            marker=dict(size=5, color=couleur),
            hovertemplate="%{y:.1f}<extra>" + colonne + "</extra>",
        ))
    fig = theme_plotly(fig, hauteur=hauteur, titre_x="Année", titre_y=titre_y)

    # Rapproche le rendu de celui du tableau de bord natif (app.py) sur un
    # point seulement : 5 graduations Y réparties uniformément entre le
    # minimum et le maximum réels des données, au lieu des graduations
    # "à chiffres ronds" que Plotly choisit par défaut. L'axe X garde
    # l'espacement automatique de Plotly (comme les autres onglets) --
    # afficher toutes les années y avait été testé, mais rendait l'axe
    # illisible sur les graphiques plus étroits (trop d'étiquettes
    # empilées verticalement).
    toutes_valeurs = tableau_pivot.to_numpy(dtype=float)
    toutes_valeurs = toutes_valeurs[~np.isnan(toutes_valeurs)]
    if len(toutes_valeurs) > 0:
        v_min, v_max = float(toutes_valeurs.min()), float(toutes_valeurs.max())
        if v_max > v_min:
            pas = (v_max - v_min) / 4
            fig.update_yaxes(
                tickmode="array",
                tickvals=[v_min + i * pas for i in range(5)],
                tickformat=".1f",
            )
    return fig


def graphique_nuage(df, x, y, colonne_couleur, titre_x, titre_y, hauteur=460, afficher_regression=True):
    """Nuage de points coloré par pays (équivalent enrichi de st.scatter_chart),
    avec une droite de régression optionnelle (NumPy polyfit) superposée pour
    illustrer visuellement le sens et la force de la corrélation calculée."""
    fig = go.Figure()
    groupes = list(df.groupby(colonne_couleur))
    couleurs = couleurs_categorielles(len(groupes))
    for (nom, sous_df), couleur in zip(groupes, couleurs):
        fig.add_trace(go.Scatter(
            x=sous_df[x], y=sous_df[y], mode="markers", name=nom,
            marker=dict(size=8, color=couleur, opacity=0.75, line=dict(width=0.5, color="white")),
            hovertemplate=f"{nom}<br>%{{x:.1f}} / %{{y:.1f}}<extra></extra>",
        ))

    if afficher_regression:
        x_vals = df[x].to_numpy(dtype=float)
        y_vals = df[y].to_numpy(dtype=float)
        masque = ~(np.isnan(x_vals) | np.isnan(y_vals))
        if masque.sum() >= 3:
            pente, ordonnee = np.polyfit(x_vals[masque], y_vals[masque], deg=1)
            x_droite = np.array([x_vals[masque].min(), x_vals[masque].max()])
            y_droite = pente * x_droite + ordonnee
            fig.add_trace(go.Scatter(
                x=x_droite, y=y_droite, mode="lines", name="Régression linéaire",
                line=dict(width=2.5, color=GAEA_CORP["accent_rouge"], dash="dash"),
                hoverinfo="skip",
            ))

    fig = theme_plotly(fig, hauteur=hauteur, titre_x=titre_x, titre_y=titre_y)
    fig.update_layout(hovermode="closest")
    return fig


def graphique_camembert(labels, valeurs, couleurs, hauteur=420):
    fig = go.Figure(go.Pie(
        labels=labels, values=valeurs, hole=0.5,
        marker=dict(colors=couleurs, line=dict(color="white", width=2)),
        textinfo="percent", textfont=dict(size=13, color="white"),
        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_white", height=hauteur, separators=", ",
        margin=dict(l=10, r=120, t=10, b=10),
        font=dict(family="Inter, 'Segoe UI', sans-serif", size=13, color=GAEA_CORP["text"]),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def graphique_barres(labels, valeurs, couleurs, titre_y="", hauteur=380, horizontal=False):
    if horizontal:
        fig = go.Figure(go.Bar(
            y=labels, x=valeurs, orientation="h", marker_color=couleurs,
            text=[fmt_fr(v) if isinstance(v, float) else str(v) for v in valeurs],
            textposition="outside",
        ))
        return theme_plotly(fig, hauteur=hauteur, titre_x=titre_y, legende=False)
    fig = go.Figure(go.Bar(
        x=labels, y=valeurs, marker_color=couleurs,
        text=[fmt_fr(v, suffixe=" %") for v in valeurs], textposition="outside",
    ))
    return theme_plotly(fig, hauteur=hauteur, titre_y=titre_y, legende=False)


def objectif(texte_html):
    """Ce que la partie cherche à faire, en une phrase, au-dessus du graphique."""
    st.markdown(
        f'<div class="gaea-objectif"><span>Objectif</span>{fr(texte_html)}</div>',
        unsafe_allow_html=True,
    )


def a_retenir(texte_html):
    """Conclusion courte (une à deux phrases) sous une partie d'analyse."""
    st.markdown(
        f'<div class="gaea-retenir"><div><div class="gaea-retenir-titre">À retenir</div>'
        f'<div class="gaea-retenir-texte">{fr(texte_html)}</div></div></div>',
        unsafe_allow_html=True,
    )


def narratif(texte_html):
    """Paragraphe d'analyse au-dessus d'un graphique, avec les chiffres
    clés en gras (balises <b> directement dans texte_html)."""
    st.markdown(f'<div class="gaea-narratif">{fr(texte_html)}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------
# Rendu : bouton de téléchargement CSV, réutilisable sous chaque
# graphique/tableau (même principe que le modèle du coordinateur).
# ---------------------------------------------------------------
def bouton_telechargement_csv(df_a_exporter, nom_fichier, libelle="⬇️ Télécharger les données en CSV"):
    st.download_button(
        label=libelle,
        data=df_a_exporter.to_csv(index=True).encode("utf-8"),
        file_name=nom_fichier,
        mime="text/csv",
        key=f"dl_{nom_fichier}",
    )

st.markdown(f"""
<style>
/* ---------- Fond : crème légèrement texturé, comme le papier du rapport ---------- */
.stApp {{
    background:
        radial-gradient(circle at 92% 4%, rgba(107, 142, 35, 0.10) 0, rgba(107, 142, 35, 0) 32%),
        radial-gradient(circle at 0% 100%, rgba(139, 107, 74, 0.08) 0, rgba(139, 107, 74, 0) 35%),
        {GAEA_CORP["bg"]};
}}
.block-container {{ padding-top: 1.6rem; max-width: 1400px; }}

/* ---------- Bandeau d'accueil (même esprit que la page de garde du rapport) ---------- */
.gaea-hero {{
    position: relative; overflow: hidden; border-radius: 22px; padding: 30px 36px 30px 36px;
    background: linear-gradient(125deg, #3f5414 0%, {GAEA_CORP["accent_dark"]} 45%, {GAEA_CORP["accent"]} 100%);
    color: #fff; box-shadow: 0 18px 40px -18px rgba(46, 43, 38, 0.55); margin-bottom: 18px;
}}
.gaea-hero::before {{
    content: ""; position: absolute; inset: 0;
    background-image: radial-gradient(rgba(255,255,255,0.13) 1px, transparent 1.2px);
    background-size: 16px 16px; mask-image: linear-gradient(90deg, transparent 35%, #000 100%);
    -webkit-mask-image: linear-gradient(90deg, transparent 35%, #000 100%);
}}
.gaea-hero::after {{
    content: ""; position: absolute; left: -140px; bottom: -230px; width: 380px; height: 380px;
    border-radius: 50%; border: 1px solid rgba(255,255,255,0.18);
    box-shadow: 0 0 0 40px rgba(255,255,255,0.03), 0 0 0 90px rgba(255,255,255,0.025);
}}
.gaea-hero-filet {{ position: absolute; left: 0; right: 0; bottom: 0; height: 5px;
    background: linear-gradient(90deg, {GAEA_CORP["brown"]}, #d4a017 50%, {GAEA_CORP["brown"]}); }}
.gaea-hero-eyebrow {{ position: relative; font-size: 0.74rem; letter-spacing: 0.32em; text-transform: uppercase;
    color: rgba(255,255,255,0.78); font-weight: 600; }}
.gaea-hero-eyebrow span {{ display: inline-block; width: 26px; height: 2px; background: #d4a017;
    vertical-align: middle; margin: 0 10px 2px 10px; }}
.gaea-hero-title {{ position: relative; font-family: 'Fraunces', Georgia, serif; font-size: 2.45rem; line-height: 1.12;
    font-weight: 700; color: #fff; margin: 10px 0 10px 0; max-width: 860px; }}
.gaea-hero-sub {{ position: relative; color: rgba(255,255,255,0.9); font-size: 1.08rem; line-height: 1.6; max-width: 640px; }}
.gaea-hero-chips {{ position: relative; display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }}
.gaea-chip {{ display: inline-flex; align-items: baseline; gap: 8px; padding: 8px 14px; border-radius: 999px;
    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.22); backdrop-filter: blur(4px);
    font-size: 0.82rem; color: rgba(255,255,255,0.92); }}
.gaea-chip b {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.15rem; color: #fff; }}

.gaea-hero-grid {{ position: relative; display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(0, 1fr);
    gap: 34px; align-items: center; }}
@media (max-width: 1100px) {{ .gaea-hero-grid {{ grid-template-columns: 1fr; }} }}
.gaea-hero-sub b {{ color: #f5e6b8; font-weight: 600; }}
.gaea-hero-stats {{ position: relative; display: flex; flex-wrap: wrap; gap: 26px; margin-top: 22px; }}
.gaea-stat {{ flex: 1 1 150px; padding-left: 14px; border-left: 3px solid #d4a017; }}
.gaea-stat-valeur {{ font-family: 'Fraunces', Georgia, serif; font-size: 2.1rem; font-weight: 700; line-height: 1.05; color: #fff; }}
.gaea-stat-label {{ font-size: 0.8rem; line-height: 1.4; color: rgba(255,255,255,0.8); margin-top: 6px; }}
.gaea-spark {{ position: relative; padding: 18px 20px 14px 20px; border-radius: 18px; background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.18); backdrop-filter: blur(6px); }}
.gaea-spark-titre {{ font-size: 0.72rem; letter-spacing: 0.22em; text-transform: uppercase; color: rgba(255,255,255,0.75); font-weight: 600; }}
.gaea-spark-chiffres {{ display: flex; align-items: baseline; gap: 10px; margin: 6px 0 4px 0; font-family: 'Fraunces', Georgia, serif; }}
.gaea-spark-chiffres span {{ font-size: 1.3rem; color: rgba(255,255,255,0.75); }}
.gaea-spark-chiffres .gaea-spark-fleche {{ color: #d4a017; }}
.gaea-spark-chiffres b {{ font-size: 2rem; color: #f5e6b8; }}
.gaea-spark-badge {{ margin-left: auto; align-self: center; font-family: 'Inter', sans-serif; font-style: normal;
    font-size: 0.78rem; font-weight: 700; color: #3f5414; background: #f5e6b8; padding: 4px 10px; border-radius: 999px; }}
.gaea-spark-note {{ font-size: 0.72rem; line-height: 1.4; color: rgba(255,255,255,0.7); margin-top: 6px; }}
.gaea-hero .gaea-hero-chips {{ margin-top: 20px; }}

/* ---------- Question de recherche ---------- */
.gaea-quote {{ position: relative; font-family: 'Fraunces', Georgia, serif; font-style: italic; text-align: center;
    color: {GAEA_CORP["accent_dark"]}; font-size: 1.12rem; line-height: 1.5; padding: 18px 48px; margin: 6px 0 14px 0;
    background: rgba(255,255,255,0.65); border-radius: 16px; border: 1px solid rgba(77, 101, 25, 0.15); }}
.gaea-quote-source {{ font-family: 'Inter', sans-serif; font-style: normal; font-size: 0.8rem; color: rgba(46,43,38,0.6);
    margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(139,107,74,0.18); }}
.gaea-section-label {{ display: flex; align-items: center; gap: 12px; font-size: 0.74rem; letter-spacing: 0.22em;
    text-transform: uppercase; font-weight: 700; color: {GAEA_CORP["accent_dark"]}; margin: 4px 0 10px 0; }}
.gaea-section-label::before {{ content: ""; width: 26px; height: 3px; border-radius: 3px; background: #d4a017; }}
.gaea-section-label::after {{ content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(139,107,74,0.35), transparent); }}
.gaea-quote::before, .gaea-quote::after {{ position: absolute; font-size: 3.2rem; line-height: 1; color: #d4a017; opacity: 0.55; }}
.gaea-quote::before {{ content: "“"; left: 16px; top: 6px; }}
.gaea-quote::after {{ content: "”"; right: 16px; bottom: -14px; }}

/* ---------- Titres de section : filet doré, comme dans le rapport ---------- */
h2, h3 {{ color: {GAEA_CORP["accent_dark"]} !important; }}
[data-testid="stHeadingWithActionElements"] h3 {{ position: relative; padding-bottom: 10px; }}
[data-testid="stHeadingWithActionElements"] h3::after {{
    content: ""; position: absolute; left: 0; bottom: 0; width: 64px; height: 3px; border-radius: 3px;
    background: linear-gradient(90deg, {GAEA_CORP["brown"]}, #d4a017);
}}

/* ---------- Onglets : tuiles (5 + 4 sur grand écran) ---------- */
.stTabs::before {{ content: "Explorer les analyses"; display: block; text-align: center; font-size: 0.7rem;
    letter-spacing: 0.28em; text-transform: uppercase; font-weight: 700; color: {GAEA_CORP["brown"]}; margin: 8px 0 10px 0; }}
.stTabs [role="tablist"] {{ display: flex !important; flex-wrap: wrap; justify-content: center; gap: 8px;
    padding: 10px; border-radius: 22px; overflow: visible !important;
    position: relative; z-index: 5;
    background: rgba(255,255,255,0.86); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(46,43,38,0.08); box-shadow: 0 14px 30px -20px rgba(46,43,38,0.55); }}
/* Tuiles par ligne selon la largeur réelle de la zone : 5, puis 3, puis 2 (lignes incomplètes centrées) */
.stTabs {{ container-type: inline-size; }}
.stTabs [role="tab"] {{ flex: 0 1 calc(20% - 8px); }}
@container (max-width: 1050px) {{ .stTabs [role="tab"] {{ flex-basis: calc(33.3% - 8px); }} }}
@container (max-width: 560px) {{ .stTabs [role="tab"] {{ flex-basis: calc(50% - 8px); }} }}
.stTabs [role="tablist"]::after, .stTabs [role="tablist"]::before,
.stTabs .react-aria-SelectionIndicator {{ display: none !important; }}

.stTabs [role="tab"] {{ position: relative; display: flex; align-items: center; justify-content: flex-start; min-width: 0;
    min-height: 56px; height: auto !important; padding: 9px 14px !important; margin: 0 !important; border-radius: 16px;
    background: linear-gradient(180deg, #fffdf8, rgba(247, 243, 234, 0.95)); border: 1px solid rgba(46,43,38,0.07);
    transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease, border-color 0.2s ease; }}
.stTabs [role="tab"] [data-testid="stMarkdownContainer"] {{ min-width: 0; }}
.stTabs [role="tab"] p {{ display: flex; align-items: center; gap: 9px; margin: 0; font-size: 0.84rem; line-height: 1.2;
    font-weight: 500; color: {GAEA_CORP["text"]}; white-space: normal; text-align: left;
    overflow-wrap: normal; word-break: normal; hyphens: manual; }}
.stTabs [role="tab"] p span[role="img"] {{ flex: 0 0 auto; display: inline-flex !important; align-items: center; justify-content: center;
    width: 34px; height: 34px; border-radius: 11px; font-size: 19px; color: {GAEA_CORP["accent_dark"]};
    background: linear-gradient(135deg, rgba(107,142,35,0.18), rgba(107,142,35,0.06));
    transition: transform 0.2s ease, background 0.2s ease; }}
.stTabs [role="tab"]:not([aria-selected="true"]):hover {{ transform: translateY(-3px); background: #fff;
    border-color: rgba(107,142,35,0.45); box-shadow: 0 14px 22px -14px rgba(77,101,25,0.55); }}
.stTabs [role="tab"]:not([aria-selected="true"]):hover p span[role="img"] {{ transform: scale(1.08) rotate(-4deg);
    background: linear-gradient(135deg, #f5e6b8, rgba(212,160,23,0.35)); }}
.stTabs [role="tab"][aria-selected="true"] {{
    background: linear-gradient(135deg, {GAEA_CORP["accent"]} 0%, {GAEA_CORP["accent_dark"]} 70%);
    border-color: transparent; transform: translateY(-1px);
    box-shadow: 0 16px 28px -14px rgba(77, 101, 25, 0.95), 0 0 0 3px rgba(212,160,23,0.22), inset 0 -3px 0 #d4a017; }}
.stTabs [role="tab"][aria-selected="true"] p {{ color: #fff !important; font-weight: 600; }}
.stTabs [role="tab"][aria-selected="true"] p span[role="img"] {{ color: #3f5414; background: #f5e6b8; }}
.stTabs [role="tabpanel"] {{ padding-top: 18px; }}

.gaea-kpi-rangee {{ display: flex; flex-wrap: wrap; gap: 16px; align-items: stretch; margin-bottom: 10px; }}
/* ---------- Cartes KPI : dégradé, reflet et légère élévation au survol ---------- */
.gaea-kpi {{ position: relative; overflow: hidden; border-radius: 18px; padding: 18px 20px; margin-bottom: 6px;
    flex: 1 1 210px; display: flex; flex-direction: column; box-sizing: border-box;
    background-image: linear-gradient(145deg, rgba(255,255,255,0.16) 0%, rgba(255,255,255,0) 45%, rgba(0,0,0,0.16) 100%);
    box-shadow: 0 14px 26px -16px rgba(46, 43, 38, 0.65); transition: transform 0.2s ease, box-shadow 0.2s ease; }}
.gaea-kpi:hover {{ transform: translateY(-3px); box-shadow: 0 20px 32px -16px rgba(46, 43, 38, 0.7); }}
.gaea-kpi::after {{ content: ""; position: absolute; right: -26px; top: -26px; width: 96px; height: 96px; border-radius: 50%;
    background: rgba(255,255,255,0.10); }}
.gaea-kpi-icon {{ font-size: 20px; opacity: 0.95; }}
.gaea-kpi-valeur {{ font-family: 'Fraunces', Georgia, serif; font-size: 23px; white-space: nowrap; font-weight: 700; color: white;
    margin-top: 6px; line-height: 1.15; }}
.gaea-kpi-label {{ font-size: 12px; color: rgba(255,255,255,0.9); margin-top: 4px; letter-spacing: 0.01em; }}
.gaea-kpi-delta {{ display: inline-block; align-self: flex-start; font-size: 11.5px; color: #fff; margin-top: 8px; font-weight: 600;
    padding: 2px 9px; border-radius: 999px; background: rgba(255,255,255,0.18); }}

/* ---------- Bouton flottant « ↑ Analyses » ---------- */
#analyses {{ scroll-margin-top: 4.5rem; }}
.gaea-retour-onglets {{ position: fixed; right: 26px; bottom: 78px; z-index: 999; display: inline-flex; align-items: center;
    padding: 10px; border-radius: 999px; text-decoration: none !important;
    font-weight: 600; font-size: 0.88rem; color: #fff !important;
    background: linear-gradient(135deg, {GAEA_CORP["accent"]}, {GAEA_CORP["accent_dark"]});
    box-shadow: 0 14px 28px -12px rgba(77,101,25,0.85), 0 0 0 4px rgba(212,160,23,0.18);
    transition: transform 0.2s ease, box-shadow 0.2s ease; }}
.gaea-retour-onglets span {{ display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px;
    border-radius: 50%; background: #f5e6b8; color: #3f5414; font-weight: 800; }}
/* Replié en pastille pour ne pas cacher le texte ; le libellé apparaît au survol. */
.gaea-retour-onglets em {{ max-width: 0; overflow: hidden; white-space: nowrap; font-style: normal; transition: max-width 0.2s ease; }}
.gaea-retour-onglets:hover em {{ max-width: 90px; padding: 0 8px; }}
.gaea-retour-onglets:hover {{ transform: translateY(-3px); box-shadow: 0 18px 32px -12px rgba(77,101,25,0.9), 0 0 0 5px rgba(212,160,23,0.25); }}
@media print {{ .gaea-retour-onglets {{ display: none !important; }} }}

/* ---------- Volets « En savoir plus » ---------- */
div[data-testid="stExpander"] details {{ border-radius: 16px !important; border: 1px solid rgba(46,43,38,0.08) !important;
    background: rgba(255,255,255,0.75); box-shadow: 0 10px 24px -20px rgba(46,43,38,0.5); margin-bottom: 10px; }}
div[data-testid="stExpander"] summary {{ padding: 14px 18px !important; font-weight: 600; }}
div[data-testid="stExpander"] summary:hover {{ color: {GAEA_CORP["accent_dark"]}; }}
div[data-testid="stExpander"] summary [data-testid="stIconMaterial"] {{ color: {GAEA_CORP["accent_dark"]}; }}

/* ---------- Pied de page ---------- */
.gaea-pied {{ position: relative; overflow: hidden; margin: 30px 0 10px 0; padding: 22px 28px; border-radius: 20px; color: #fff;
    background: linear-gradient(125deg, #3f5414 0%, {GAEA_CORP["accent_dark"]} 55%, {GAEA_CORP["accent"]} 100%);
    box-shadow: 0 16px 34px -20px rgba(46,43,38,0.6); }}
.gaea-pied::after {{ content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 4px;
    background: linear-gradient(90deg, {GAEA_CORP["brown"]}, #d4a017 50%, {GAEA_CORP["brown"]}); }}
.gaea-pied-titre {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.25rem; font-weight: 700; }}
.gaea-pied-texte {{ font-size: 0.9rem; color: rgba(255,255,255,0.85); margin-top: 6px; max-width: 760px; line-height: 1.5; }}
.gaea-pied-source {{ font-size: 0.78rem; color: rgba(255,255,255,0.7); margin-top: 10px; }}
.gaea-pied-source a {{ color: #f5e6b8; }}

/* ---------- Encart « Objectif » ---------- */
.gaea-objectif {{ display: flex; align-items: baseline; gap: 10px; margin: 2px 0 10px 0; font-size: 0.95rem;
    line-height: 1.5; color: rgba(46,43,38,0.85); }}
.gaea-objectif span {{ flex: 0 0 auto; font-size: 0.66rem; letter-spacing: 0.16em; text-transform: uppercase; font-weight: 700;
    color: #fff; background: {GAEA_CORP["accent_dark"]}; padding: 3px 9px; border-radius: 999px; }}

/* ---------- Encart « À retenir » ---------- */
.gaea-frise {{ position: relative; padding: 6px 0 4px 0; }}
.gaea-frise::before {{ content: ""; position: absolute; left: 21px; top: 14px; bottom: 14px; width: 3px; border-radius: 3px;
    background: linear-gradient(180deg, #d4a017, {GAEA_CORP["accent_dark"]} 60%, rgba(77,101,25,0.15)); }}
.gaea-frise-etape {{ position: relative; display: flex; gap: 16px; align-items: flex-start; margin-bottom: 12px;
    animation: gaeaApparition 0.55s ease-out both; }}
.gaea-frise-etape:nth-child(2) {{ animation-delay: 0.08s; }} .gaea-frise-etape:nth-child(3) {{ animation-delay: 0.16s; }}
.gaea-frise-etape:nth-child(4) {{ animation-delay: 0.24s; }} .gaea-frise-etape:nth-child(5) {{ animation-delay: 0.32s; }}
.gaea-frise-point {{ position: relative; z-index: 1; flex: 0 0 auto; width: 44px; height: 44px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-size: 1.2rem; background: #fbf8f1;
    border: 3px solid {GAEA_CORP["accent_dark"]}; box-shadow: 0 8px 18px -10px rgba(46,43,38,0.6); }}
.gaea-frise-nouveau .gaea-frise-point {{ border-color: #d4a017; background: #fff6dc; animation: gaeaPulsation 2.4s ease-in-out infinite; }}
@keyframes gaeaPulsation {{ 0%, 100% {{ box-shadow: 0 0 0 0 rgba(212,160,23,0.45); }} 50% {{ box-shadow: 0 0 0 9px rgba(212,160,23,0); }} }}
.gaea-frise-carte {{ flex: 1; padding: 12px 16px; border-radius: 16px; background: #fff; border: 1px solid rgba(46,43,38,0.07);
    box-shadow: 0 12px 26px -22px rgba(46,43,38,0.55); transition: transform 0.2s ease, box-shadow 0.2s ease; }}
.gaea-frise-carte:hover {{ transform: translateX(4px); box-shadow: 0 16px 30px -18px rgba(77,101,25,0.45); }}
.gaea-frise-nouveau .gaea-frise-carte {{ background: linear-gradient(120deg, #fffaf0, #fff); border-color: rgba(212,160,23,0.45); }}
.gaea-frise-tag {{ display: inline-block; font-size: 0.66rem; letter-spacing: 0.16em; text-transform: uppercase; font-weight: 700;
    color: {GAEA_CORP["accent_dark"]}; background: rgba(77,101,25,0.10); padding: 2px 9px; border-radius: 999px; }}
.gaea-frise-nouveau .gaea-frise-tag {{ color: #6b4e00; background: #f5e6b8; }}
.gaea-frise-titre {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.08rem; font-weight: 700; color: #2e2b26; margin: 5px 0 2px 0; }}
.gaea-frise-carte p {{ margin: 0; font-size: 0.88rem; line-height: 1.5; color: rgba(46,43,38,0.78); }}
.gaea-frise-liste {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 8px; margin-top: 8px; }}
.gaea-frise-liste > div {{ display: flex; gap: 10px; align-items: flex-start; padding: 8px 10px; border-radius: 12px;
    background: rgba(245,230,184,0.28); border: 1px solid rgba(212,160,23,0.22); transition: background 0.2s ease; }}
.gaea-frise-liste > div:hover {{ background: rgba(245,230,184,0.55); }}
.gaea-frise-liste span {{ flex: 0 0 auto; width: 28px; height: 28px; border-radius: 9px; display: flex; align-items: center;
    justify-content: center; font-size: 0.95rem; background: #fff; box-shadow: 0 4px 10px -6px rgba(46,43,38,0.5); }}
.gaea-frise-liste p {{ font-size: 0.84rem !important; }}
.gaea-frise-liste b {{ color: #2e2b26; }}
.gaea-methodo-bandeau {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; overflow: hidden; border-radius: 18px;
    background: rgba(245,230,184,0.35); box-shadow: 0 16px 30px -20px rgba(46,43,38,0.6); margin: 4px 0 14px 0;
    animation: gaeaApparition 0.55s ease-out both; }}
.gaea-methodo-bandeau > div {{ padding: 16px 12px; text-align: center; color: #fff;
    background: linear-gradient(135deg, #3f5414, {GAEA_CORP["accent_dark"]}); }}
.gaea-methodo-bandeau b {{ display: block; font-family: 'Fraunces', Georgia, serif; font-size: 1.9rem; line-height: 1.1;
    background: linear-gradient(90deg, #fff, #f5e6b8); -webkit-background-clip: text; background-clip: text; color: transparent; }}
.gaea-methodo-bandeau span {{ font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(245,240,230,0.82); }}
.gaea-bandeau-survol {{ position: relative; cursor: help; outline: none; }}
.gaea-bandeau-face, .gaea-bandeau-dos {{ transition: opacity 0.3s ease, transform 0.3s ease; }}
.gaea-bandeau-face i {{ display: block; margin-top: 2px; font-size: 0.66rem; font-style: normal; color: rgba(245,230,184,0.7); }}
.gaea-bandeau-dos {{ position: absolute; inset: 0; display: flex; flex-wrap: wrap; align-content: center; justify-content: center;
    gap: 5px; padding: 8px; opacity: 0; transform: translateY(8px); pointer-events: none; }}
.gaea-bandeau-dos em {{ font-style: normal; font-size: 0.74rem; font-weight: 600; color: #33440f; background: #f5e6b8;
    padding: 3px 9px; border-radius: 999px; }}
.gaea-bandeau-survol:hover .gaea-bandeau-face, .gaea-bandeau-survol:focus .gaea-bandeau-face {{ opacity: 0; transform: translateY(-8px); }}
.gaea-bandeau-survol:hover .gaea-bandeau-dos, .gaea-bandeau-survol:focus .gaea-bandeau-dos {{ opacity: 1; transform: none; }}
.gaea-fiches {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 14px; margin: 6px 0 8px 0; }}
.gaea-fiche {{ position: relative; overflow: hidden; padding: 16px 16px 12px 16px; border-radius: 18px; background: #fff;
    border: 1px solid rgba(46,43,38,0.07); box-shadow: 0 14px 28px -22px rgba(46,43,38,0.6);
    transition: transform 0.2s ease, box-shadow 0.2s ease; animation: gaeaApparition 0.55s ease-out both; }}
.gaea-fiche::before {{ content: ""; position: absolute; left: 0; right: 0; top: 0; height: 5px; background: var(--profil); }}
.gaea-fiche::after {{ content: ""; position: absolute; right: -40px; top: -40px; width: 110px; height: 110px; border-radius: 50%;
    background: var(--profil); opacity: 0.07; }}
.gaea-fiche:hover {{ transform: translateY(-4px); box-shadow: 0 22px 36px -22px rgba(46,43,38,0.6); }}
.gaea-fiche:nth-child(2) {{ animation-delay: 0.06s; }} .gaea-fiche:nth-child(3) {{ animation-delay: 0.12s; }}
.gaea-fiche:nth-child(4) {{ animation-delay: 0.18s; }} .gaea-fiche:nth-child(5) {{ animation-delay: 0.24s; }}
.gaea-fiche-tete {{ display: flex; align-items: center; gap: 10px; }}
.gaea-fiche-rang {{ flex: 0 0 auto; min-width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-size: 1.15rem; font-weight: 700; color: #6b4e00; background: #f5e6b8; }}
.gaea-fiche-nom {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.2rem; font-weight: 700; color: #2e2b26; }}
.gaea-fiche-profil {{ display: inline-block; margin: 8px 0 10px 0; padding: 3px 10px; border-radius: 999px; font-size: 0.74rem;
    font-weight: 700; color: #fff; background: var(--profil); }}
.gaea-fiche-jauge {{ margin-top: 8px; }}
.gaea-fiche-jauge-tete {{ display: flex; justify-content: space-between; font-size: 0.78rem; color: rgba(46,43,38,0.65); }}
.gaea-fiche-jauge-tete b {{ color: #2e2b26; }}
.gaea-fiche-piste {{ position: relative; height: 8px; margin-top: 4px; border-radius: 999px; background: rgba(46,43,38,0.08); }}
.gaea-fiche-rempli {{ height: 100%; border-radius: 999px; }}
.gaea-fiche-rempli.bien {{ background: linear-gradient(90deg, #9cc35a, {GAEA_CORP["accent_dark"]}); }}
.gaea-fiche-rempli.moins {{ background: linear-gradient(90deg, #d98a9c, {GAEA_CORP["accent_rouge"]}); }}
.gaea-fiche-repere {{ position: absolute; top: -3px; width: 3px; height: 14px; border-radius: 2px; background: #d4a017;
    transform: translateX(-50%); box-shadow: 0 0 0 2px #fff; }}
.gaea-alerte {{ margin: 4px 0 16px 0; padding: 12px 16px; border-radius: 14px; font-size: 0.92rem; line-height: 1.5;
    color: #2e2b26; background: linear-gradient(120deg, rgba(77,101,25,0.10), rgba(255,255,255,0.7));
    border: 1px solid rgba(77,101,25,0.22); border-left: 4px solid {GAEA_CORP["accent_dark"]}; }}
.gaea-alerte b {{ color: {GAEA_CORP["accent_dark"]}; }}
.gaea-methodo-onglets {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }}
.gaea-methodo-onglets span {{ font-size: 0.78rem; font-weight: 600; color: {GAEA_CORP["accent_dark"]}; background: #fff;
    border: 1px solid rgba(77,101,25,0.25); padding: 4px 11px; border-radius: 999px; }}
.gaea-methodo-grille {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; }}
.gaea-methodo-carte {{ position: relative; overflow: hidden; padding: 16px 16px 14px 16px; border-radius: 16px; background: #fff;
    border: 1px solid rgba(46,43,38,0.07); box-shadow: 0 12px 26px -22px rgba(46,43,38,0.55);
    transition: transform 0.2s ease, box-shadow 0.2s ease; animation: gaeaApparition 0.55s ease-out both; }}
.gaea-methodo-carte::before {{ content: ""; position: absolute; left: 0; right: 0; top: 0; height: 4px;
    background: linear-gradient(90deg, {GAEA_CORP["accent_dark"]}, #d4a017); }}
.gaea-methodo-carte:hover {{ transform: translateY(-4px); box-shadow: 0 20px 34px -20px rgba(77,101,25,0.5); }}
.gaea-methodo-carte:nth-child(3)::before {{ background: linear-gradient(90deg, #b8860b, #8b6b4a); }}
.gaea-sources {{ position: relative; overflow: hidden; margin-bottom: 14px; padding: 18px 18px 16px 18px; border-radius: 20px; color: #fff;
    background: radial-gradient(circle at 100% 0%, rgba(212,160,23,0.28) 0, rgba(212,160,23,0) 45%),
        linear-gradient(135deg, #33440f, {GAEA_CORP["accent_dark"]});
    box-shadow: 0 18px 34px -20px rgba(46,43,38,0.65); animation: gaeaApparition 0.55s ease-out both; }}
.gaea-sources-titre {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.15rem; font-weight: 700; margin-bottom: 12px; }}
.gaea-sources-grille {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; }}
a.gaea-source {{ display: block; padding: 12px 14px; border-radius: 14px; text-decoration: none !important;
    background: rgba(255,255,255,0.10); border: 1px solid rgba(245,230,184,0.30);
    transition: transform 0.2s ease, background 0.2s ease; }}
a.gaea-source:hover {{ transform: translateY(-3px); background: rgba(255,255,255,0.18); }}
.gaea-source-tete {{ display: flex; gap: 10px; align-items: center; margin-bottom: 6px; }}
.gaea-source-icone {{ flex: 0 0 auto; width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center;
    justify-content: center; font-size: 1.05rem; background: #fbf8f1; }}
.gaea-source-role {{ font-size: 0.62rem; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 700; color: #f5e6b8; }}
.gaea-source-nom {{ font-family: 'Fraunces', Georgia, serif; font-size: 1rem; font-weight: 700; color: #fff; }}
a.gaea-source p {{ margin: 0; font-size: 0.8rem; line-height: 1.45; color: rgba(255,255,255,0.82); }}
.gaea-methodo-icone {{ width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center;
    font-size: 1.15rem; background: rgba(77,101,25,0.10); margin-bottom: 8px; }}
.gaea-methodo-titre {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.05rem; font-weight: 700; color: #2e2b26; margin-bottom: 4px; }}
.gaea-methodo-carte p {{ margin: 0; font-size: 0.86rem; line-height: 1.5; color: rgba(46,43,38,0.78); }}
.gaea-methodo-carte a {{ color: {GAEA_CORP["accent_dark"]}; font-weight: 600; }}
.gaea-methodo-note {{ margin-top: 12px; font-size: 0.78rem; color: rgba(46,43,38,0.6); line-height: 1.5; }}
@media (max-width: 640px) {{ .gaea-methodo-bandeau {{ grid-template-columns: repeat(2, 1fr); }} }}
@keyframes gaeaApparition {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
.gaea-retenir, .gaea-objectif {{ animation: gaeaApparition 0.55s ease-out both; }}
.gaea-retenir {{ position: relative; display: flex; align-items: flex-start; gap: 14px; margin: 12px 0 22px 0;
    padding: 14px 18px 14px 16px; border-radius: 16px;
    background: linear-gradient(100deg, rgba(212,160,23,0.16), rgba(212,160,23,0.04) 60%, rgba(255,255,255,0.5));
    border: 1px solid rgba(212,160,23,0.35); box-shadow: 0 10px 22px -18px rgba(139,107,74,0.7); }}
.gaea-retenir::before {{ content: "★"; flex: 0 0 auto; display: flex; align-items: center; justify-content: center;
    width: 30px; height: 30px; border-radius: 50%; background: #d4a017; color: #fff; font-size: 0.95rem;
    box-shadow: 0 0 0 5px rgba(212,160,23,0.18); }}
.gaea-retenir-titre {{ font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 700;
    color: {GAEA_CORP["brown"]}; margin-bottom: 2px; }}
.gaea-retenir-texte {{ font-size: 0.95rem; line-height: 1.55; color: {GAEA_CORP["text"]}; }}
.gaea-retenir-texte b {{ color: {GAEA_CORP["accent_dark"]}; }}

/* ---------- Cartes de profil des groupes (onglet Cluster) ---------- */
.gaea-groupes {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin: 4px 0 18px 0; }}
.gaea-groupe {{ position: relative; overflow: hidden; background: #fff; border-radius: 18px; padding: 18px 18px 16px 22px;
    border: 1px solid rgba(46,43,38,0.07); box-shadow: 0 12px 26px -18px rgba(46,43,38,0.55);
    transition: transform 0.2s ease, box-shadow 0.2s ease; }}
.gaea-groupe::before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: var(--couleur-groupe); }}
.gaea-groupe::after {{ content: ""; position: absolute; right: -40px; top: -40px; width: 120px; height: 120px; border-radius: 50%;
    background: var(--couleur-groupe); opacity: 0.08; }}
.gaea-groupe:hover {{ transform: translateY(-3px); box-shadow: 0 18px 30px -18px rgba(46,43,38,0.6); }}
.gaea-groupe-tete {{ display: flex; align-items: center; gap: 8px; font-weight: 700; color: {GAEA_CORP["text"]}; }}
.gaea-groupe-pastille {{ width: 12px; height: 12px; border-radius: 4px; background: var(--couleur-groupe); }}
.gaea-groupe-effectif {{ margin-left: auto; font-size: 0.78rem; font-weight: 600; color: #fff; background: var(--couleur-groupe);
    padding: 2px 10px; border-radius: 999px; }}
.gaea-groupe-profil {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.12rem; font-weight: 700; line-height: 1.25;
    color: var(--couleur-groupe); margin: 10px 0 12px 0; }}
.gaea-groupe-stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; padding: 10px 0;
    border-top: 1px solid rgba(46,43,38,0.08); border-bottom: 1px solid rgba(46,43,38,0.08); }}
.gaea-groupe-stats b {{ display: block; font-size: 0.98rem; color: {GAEA_CORP["text"]}; }}
.gaea-groupe-stats span {{ font-size: 0.72rem; color: rgba(46,43,38,0.6); }}
.gaea-groupe-exemples {{ font-size: 0.82rem; line-height: 1.5; color: rgba(46,43,38,0.85); margin-top: 10px; }}
.gaea-groupe-exemples span {{ font-weight: 600; color: rgba(46,43,38,0.6); }}

/* ---------- Cartes à bordure (graphiques, tableaux) ---------- */
[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {{ background-color: {GAEA_CORP["card_bg"]}; border-radius: 18px !important;
    border: 1px solid rgba(46,43,38,0.07) !important; box-shadow: 0 12px 30px -20px rgba(46, 43, 38, 0.45); padding: 8px; }}

/* ---------- Encarts de texte ---------- */
.gaea-narratif {{ font-size: 0.99rem; line-height: 1.65; margin-bottom: 14px; }}
.gaea-narratif b {{ color: {GAEA_CORP["accent_rouge"]}; }}

/* ---------- Boutons ---------- */
.stButton button, .stDownloadButton button {{ background: linear-gradient(135deg, {GAEA_CORP["accent"]}, {GAEA_CORP["accent_dark"]}) !important;
    color: white !important; border: 0 !important; font-weight: 600 !important;
    box-shadow: 0 8px 18px -10px rgba(77, 101, 25, 0.8); transition: transform 0.15s ease, filter 0.15s ease; }}
.stButton button:hover, .stDownloadButton button:hover {{ filter: brightness(1.06); transform: translateY(-1px); }}
.stButton button p, .stDownloadButton button p {{ color: white !important; }}

/* ---------- Barre latérale ---------- */
section[data-testid="stSidebar"] [data-testid="stImage"] img {{ background: #fff; padding: 10px 14px; border-radius: 14px;
    box-shadow: 0 8px 20px -14px rgba(46,43,38,0.6); }}
section[data-testid="stSidebar"] {{
    background:
        radial-gradient(circle at 15% 0%, rgba(255,255,255,0.16) 0, rgba(255,255,255,0) 38%),
        radial-gradient(circle at 100% 85%, rgba(212,160,23,0.22) 0, rgba(212,160,23,0) 40%),
        radial-gradient(rgba(255,255,255,0.07) 1px, transparent 1.2px) 0 0 / 16px 16px,
        linear-gradient(180deg, #33440f 0%, {GAEA_CORP["accent_dark"]} 55%, #5c7a21 100%) !important;
    border-right: 3px solid #d4a017; }}
section[data-testid="stSidebar"] > div {{ background: transparent !important; }}
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg {{ color: #f5e6b8; }}
.gaea-filtres-titre {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.6rem; font-weight: 700; color: #fff;
    margin: 16px 0 0 2px; letter-spacing: 0.01em; }}
.gaea-filtres-titre::after {{ content: ""; display: block; width: 46px; height: 3px; border-radius: 3px; margin-top: 6px;
    background: linear-gradient(90deg, #d4a017, #f5e6b8); }}
.gaea-filtres-sous-titre {{ font-size: 0.8rem; color: rgba(245,240,230,0.78); margin: 8px 0 14px 2px; line-height: 1.45; }}
.gaea-sel {{ margin: 6px 0 12px 0; padding: 14px 14px 12px 14px; border-radius: 16px;
    background: rgba(255,255,255,0.10); border: 1px solid rgba(245,230,184,0.35); backdrop-filter: blur(6px); }}
.gaea-sel-titre {{ font-size: 0.7rem; letter-spacing: 0.22em; text-transform: uppercase; font-weight: 700; color: #f5e6b8; }}
.gaea-sel-chiffres {{ font-size: 0.92rem; color: rgba(255,255,255,0.88); margin: 4px 0 8px 0; }}
.gaea-sel-chiffres b {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.15rem; color: #fff; }}
.gaea-sel-liste {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.gaea-sel-pays {{ font-size: 0.76rem; font-weight: 600; color: #3f5414; background: #f5e6b8; padding: 3px 10px;
    border-radius: 999px; }}
.gaea-jauge-legende {{ display: flex; justify-content: space-between; align-items: baseline; margin-top: 12px;
    font-size: 0.74rem; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(245,240,230,0.8); }}
.gaea-jauge-legende b {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.05rem; letter-spacing: 0; text-transform: none; color: #fff; }}
.gaea-jauge {{ position: relative; height: 10px; border-radius: 999px; background: rgba(255,255,255,0.18); margin: 6px 0 6px 0; overflow: visible; }}
.gaea-jauge-rempli {{ height: 100%; border-radius: 999px; background: linear-gradient(90deg, #9cc35a, #f5e6b8);
    box-shadow: 0 0 12px rgba(245,230,184,0.55); }}
.gaea-jauge-repere {{ position: absolute; top: -4px; width: 3px; height: 18px; border-radius: 2px; background: #d4a017;
    transform: translateX(-50%); box-shadow: 0 0 0 2px rgba(51,68,15,0.6); }}
.gaea-jauge-note {{ font-size: 0.72rem; color: rgba(245,240,230,0.72); line-height: 1.4; }}
.gaea-guide > div {{ display: flex; gap: 10px; align-items: flex-start; margin-bottom: 8px; }}
.gaea-guide span {{ flex: 0 0 auto; display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px;
    border-radius: 50%; font-size: 0.75rem; font-weight: 700; color: #fff; background: {GAEA_CORP["accent_dark"]}; }}
.gaea-guide p {{ margin: 0; font-size: 0.84rem; line-height: 1.45; }}
section[data-testid="stSidebar"] [data-testid="stButtonGroup"] button {{ font-size: 0.8rem; }}
.gaea-filtres-note {{ font-size: 0.74rem; color: rgba(245,240,230,0.7); margin: 10px 2px 4px 2px; line-height: 1.45; }}
section[data-testid="stSidebar"] .stButton button {{ background: linear-gradient(135deg, #e0b23a, #b8860b) !important;
    color: #2e2b26 !important; box-shadow: 0 10px 22px -10px rgba(0,0,0,0.55) !important; }}
section[data-testid="stSidebar"] .stButton button p, section[data-testid="stSidebar"] .stButton button span {{ color: #2e2b26 !important; }}
.gaea-filtre-entete {{ display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: {GAEA_CORP["accent_dark"]}; margin: 2px 0 8px 0; }}
.gaea-filtre-num {{ display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%;
    font-size: 0.78rem; letter-spacing: 0; color: #fff; background: linear-gradient(135deg, {GAEA_CORP["accent"]}, {GAEA_CORP["accent_dark"]});
    box-shadow: 0 0 0 3px rgba(212,160,23,0.25); }}
section[data-testid="stSidebar"] [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {{ background: #fbf8f1;
    border-radius: 18px !important; border: 1px solid rgba(245,230,184,0.6) !important;
    box-shadow: 0 16px 30px -18px rgba(0,0,0,0.6); padding: 14px 14px 10px 14px !important; margin-bottom: 6px; }}
label, .stSelectbox label, .stRadio label {{ color: {GAEA_CORP["text"]} !important; font-weight: 500; }}

/* ---------- Impression ---------- */
.gaea-btn-export {{ background-color: {GAEA_CORP["accent"]}; color: white; border: 0; border-radius: 10px; font-weight: 600; padding: 10px 18px; font-size: 14px; cursor: pointer; }}
@media print {{ section[data-testid="stSidebar"], .gaea-btn-export, .stTabs [role="tablist"], iframe {{ display: none !important; }} }}
</style>
""", unsafe_allow_html=True)

df = charger_donnees()

# ---------------------------------------------------------------
# Page d'ouverture : lever de soleil sur un paysage éolien et solaire,
# jusqu'au bouton « Entrer ». Le bouton n'apparaît qu'une fois les onglets
# construits, ce qui couvre aussi l'attente du premier chargement. Elle
# est insérée dans le document PARENT (comme les blocs techniques du haut)
# et ne s'affiche qu'une fois par onglet du navigateur. En cas d'échec du
# script, rien n'est ajouté : l'application reste utilisable.
# ---------------------------------------------------------------
OUVERTURE_STREAMLIT = """
<template id="gaea-ouverture">
<style>
#gaea-rideau { position: fixed; inset: 0; z-index: 999999; overflow: hidden; color: #fff; font-family: 'Inter', 'Segoe UI', sans-serif; }
#gaea-rideau .volet { position: absolute; top: 0; bottom: 0; width: 50.5%; background: #16230f; transition: transform 1s cubic-bezier(0.7, 0, 0.2, 1) 0.25s; }
#gaea-rideau .volet.g { left: 0; }
#gaea-rideau .volet.d { right: 0; }
#gaea-rideau.ouvert { pointer-events: none; }
#gaea-rideau.ouvert .volet.g { transform: translateX(-101%); }
#gaea-rideau.ouvert .volet.d { transform: translateX(101%); }
#gaea-rideau .scene { position: absolute; inset: 0; background: linear-gradient(180deg, #0d1a12 0%, #16301c 55%, #2d4a1e 100%); transition: opacity 0.45s ease, transform 0.8s ease; }
#gaea-rideau.ouvert .scene { opacity: 0; transform: scale(1.08); }
#gaea-rideau .aube { position: absolute; inset: 0; opacity: 0; background: linear-gradient(180deg, #24452f 0%, #7a8a3a 48%, #e0b04a 74%, #f5e6b8 100%); animation: gaeaAube 3.4s ease-out 0.2s forwards; }
#gaea-rideau .etoiles { position: absolute; inset: 0 0 45% 0; background-image: radial-gradient(1.5px 1.5px at 12% 22%, #fff, transparent), radial-gradient(1px 1px at 28% 58%, #fff, transparent), radial-gradient(1.5px 1.5px at 43% 16%, #fff, transparent), radial-gradient(1px 1px at 61% 44%, #fff, transparent), radial-gradient(1.5px 1.5px at 76% 19%, #fff, transparent), radial-gradient(1px 1px at 89% 52%, #fff, transparent), radial-gradient(1px 1px at 7% 71%, #fff, transparent), radial-gradient(1px 1px at 53% 74%, #fff, transparent); animation: gaeaEtoiles 2.6s ease-out forwards; }
#gaea-rideau .soleil { position: absolute; left: 50%; bottom: 8%; width: min(44vh, 62vw); aspect-ratio: 1; margin-left: calc(min(44vh, 62vw) / -2); border-radius: 50%; background: radial-gradient(circle, #fff6d6 0%, #fbe08a 34%, rgba(240, 190, 70, 0.55) 52%, rgba(240, 190, 70, 0) 71%); transform: translateY(70%); animation: gaeaSoleil 3.6s cubic-bezier(0.2, 0.7, 0.2, 1) 0.1s forwards; }
#gaea-rideau svg.paysage { position: absolute; left: 0; right: 0; bottom: 0; width: 100%; height: 46%; }
#gaea-rideau .pale { transform-box: view-box; animation: gaeaPale 5s linear infinite; }
#gaea-rideau .pale.b { animation-duration: 7s; }
#gaea-rideau .pale.c { animation-duration: 4s; }
#gaea-rideau .texte { position: absolute; inset: 0 16px 20% 16px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; text-align: center; text-shadow: 0 2px 22px rgba(10, 22, 12, 0.6); }
#gaea-rideau small { font-size: clamp(11px, 1.5vw, 14px); font-weight: 600; letter-spacing: 0.32em; text-transform: uppercase; color: #f5e6b8; animation: gaeaMontee 0.8s 0.2s both; }
#gaea-rideau h1 { margin: 0; padding: 0; font-family: 'Fraunces', Georgia, serif; font-size: clamp(36px, 7vw, 84px); font-weight: 700; line-height: 1.06; color: #fff; animation: gaeaMontee 0.9s 0.45s both; }
#gaea-rideau .filet { width: min(280px, 60vw); height: 3px; border-radius: 3px; background: linear-gradient(90deg, transparent, #f5e6b8, transparent); animation: gaeaFilet 0.9s 0.8s both; }
#gaea-rideau .question { max-width: 640px; font-size: clamp(16px, 2.2vw, 21px); line-height: 1.4; animation: gaeaMontee 0.8s 1.05s both; }
#gaea-rideau .annee { font-family: 'Fraunces', Georgia, serif; font-size: clamp(30px, 5vw, 50px); font-weight: 700; color: #fff6d6; font-variant-numeric: tabular-nums; animation: gaeaMontee 0.8s 1.2s both; }
#gaea-rideau .perimetre { font-size: clamp(13px, 1.7vw, 16px); color: rgba(255, 255, 255, 0.9); animation: gaeaMontee 0.8s 1.35s both; }
#gaea-rideau .attente { width: 200px; height: 4px; margin-top: 20px; overflow: hidden; border-radius: 4px; background: rgba(255, 255, 255, 0.25); }
#gaea-rideau .attente i { display: block; width: 40%; height: 100%; border-radius: 4px; background: #f5e6b8; animation: gaeaAttente 1.3s ease-in-out infinite; }
#gaea-rideau button { display: none; margin-top: 16px; padding: 15px 46px; border: 0; border-radius: 999px; cursor: pointer; font: 700 19px 'Inter', 'Segoe UI', sans-serif; color: #16230f; background: linear-gradient(135deg, #fbeec6, #d4a017); animation: gaeaMontee 0.6s both, gaeaAppel 2.4s 0.7s ease-in-out infinite; transition: transform 0.25s ease; }
#gaea-rideau.pret button { display: inline-block; }
#gaea-rideau.pret .attente { display: none; }
#gaea-rideau button:hover { transform: scale(1.07); }
#gaea-rideau button:focus-visible { outline: 3px solid #fff; outline-offset: 3px; }
@keyframes gaeaAube { to { opacity: 1; } }
@keyframes gaeaEtoiles { to { opacity: 0; } }
@keyframes gaeaSoleil { to { transform: translateY(0); } }
@keyframes gaeaPale { to { transform: rotate(360deg); } }
@keyframes gaeaMontee { from { opacity: 0; transform: translateY(22px); } }
@keyframes gaeaFilet { from { transform: scaleX(0); } }
@keyframes gaeaAttente { from { transform: translateX(-100%); } to { transform: translateX(260%); } }
@keyframes gaeaAppel { 50% { box-shadow: 0 0 0 16px rgba(212, 160, 23, 0), 0 0 34px rgba(245, 230, 184, 0.7); } 0%, 100% { box-shadow: 0 0 0 0 rgba(212, 160, 23, 0.55); } }
@media (max-height: 620px) { #gaea-rideau .question, #gaea-rideau .perimetre { display: none; } }
@media (prefers-reduced-motion: reduce) {
    #gaea-rideau *, #gaea-rideau { animation: none !important; transition: none !important; }
    #gaea-rideau .aube { opacity: 1; }
    #gaea-rideau .etoiles { opacity: 0; }
    #gaea-rideau .soleil { transform: none; }
}
@media print { #gaea-rideau { display: none !important; } }
</style>
<div id="gaea-rideau" role="dialog" aria-modal="true" aria-label="Page d'ouverture">
    <div class="volet g"></div><div class="volet d"></div>
    <div class="scene">
        <div class="aube"></div><div class="etoiles"></div><div class="soleil"></div>
        <svg class="paysage" viewBox="0 0 1600 420" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
            <path d="M0 300 C260 220 480 300 760 250 C1040 200 1280 290 1600 230 V420 H0 Z" fill="#3c5a24" opacity="0.75"/>
            <g fill="#1e3214">
                <path d="M286 300 l5 -176 h4 l5 176 z"/>
                <g class="pale" style="transform-origin: 293px 122px"><path d="M291 122 L293 22 L298 120 Z M293 120 L381 174 L289 126 Z M295 125 L205 172 L291 119 Z"/></g>
                <path d="M1290 282 l4 -136 h3 l4 136 z"/>
                <g class="pale b" style="transform-origin: 1295px 145px"><path d="M1293 145 L1295 67 L1299 143 Z M1295 143 L1364 186 L1291 148 Z M1297 147 L1226 185 L1293 142 Z"/></g>
                <g transform="translate(-55 0)">
                    <path d="M1012 262 l3 -96 h2 l3 96 z"/>
                    <g class="pale c" style="transform-origin: 1016px 165px"><path d="M1015 165 L1016 110 L1019 164 Z M1016 164 L1064 194 L1013 167 Z M1017 167 L968 193 L1015 163 Z"/></g>
                </g>
                <g transform="translate(-640 8)">
                    <path d="M1290 282 l4 -136 h3 l4 136 z"/>
                    <g class="pale" style="transform-origin: 1295px 145px"><path d="M1293 145 L1295 67 L1299 143 Z M1295 143 L1364 186 L1291 148 Z M1297 147 L1226 185 L1293 142 Z"/></g>
                </g>
            </g>
            <path d="M0 360 C300 300 620 370 900 325 C1180 285 1380 345 1600 305 V420 H0 Z" fill="#16230f"/>
            <g fill="#27401b" stroke="#d4a017" stroke-width="1.4" stroke-opacity="0.65">
                <path d="M520 372 l66 -10 l30 30 l-72 12 z"/><path d="M620 362 l66 -10 l30 30 l-72 12 z"/><path d="M720 352 l66 -10 l30 30 l-72 12 z"/><path d="M820 343 l66 -10 l30 30 l-72 12 z"/>
            </g>
        </svg>
        <div class="texte">
            <small>Projet Trends · gaea21</small>
            <h1>Énergies renouvelables</h1>
            <div class="filet"></div>
            <div class="question">Le monde produit de plus en plus d'électricité verte. Ses émissions baissent-elles pour autant ?</div>
            <div class="annee" aria-hidden="true">%%DEBUT%%</div>
            <div class="perimetre">%%PAYS%% pays et territoires · %%DUREE%% ans de données · une question</div>
            <div class="attente" role="status" aria-label="Chargement"><i></i></div>
            <button type="button">Entrer →</button>
        </div>
    </div>
</div>
</template>
<script>
(function () {
    // Bloc technique sans contenu : on le sort de la page pour qu'il ne laisse ni trait ni marge.
    const bloc = window.frameElement.closest('.stElementContainer');
    Object.assign(bloc.style, { position: 'absolute', height: '0', overflow: 'hidden' });
    const doc = window.parent.document;
    if (doc.getElementById('gaea-rideau')) return;
    try {
        if (window.parent.sessionStorage.getItem('gaea-entree')) return;
    } catch (e) { /* stockage indisponible : la page s'affiche à chaque ouverture */ }

    doc.body.appendChild(doc.importNode(document.getElementById('gaea-ouverture').content, true));
    const rideau = doc.getElementById('gaea-rideau');
    const bouton = rideau.querySelector('button');
    const annee = rideau.querySelector('.annee');
    const calme = window.parent.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const debut = %%DEBUT%%, fin = %%FIN%%;

    if (calme) {
        annee.textContent = fin;
    } else {
        const depart = performance.now() + 700;
        (function pas(maintenant) {
            const avance = Math.min(1, Math.max(0, (maintenant - depart) / 2600));
            annee.textContent = Math.round(debut + (fin - debut) * avance);
            if (avance < 1) requestAnimationFrame(pas);
        })(performance.now());
    }

    // Les chiffres du bandeau d'accueil montent à l'entrée, puis retrouvent leur texte exact.
    function compterChiffres() {
        if (calme) return;
        doc.querySelectorAll('.gaea-stat-valeur').forEach(function (cible) {
            const texte = cible.textContent;
            const trouve = texte.match(/\\d[\\d\\s\\u202f]*(,\\d+)?/);
            if (!trouve) return;
            const decimales = trouve[1] ? trouve[1].length - 1 : 0;
            const valeur = parseFloat(trouve[0].replace(/[\\s\\u202f]/g, '').replace(',', '.'));
            const depart = performance.now();
            (function pas(maintenant) {
                const avance = Math.min(1, (maintenant - depart) / 1200);
                if (avance >= 1) { cible.textContent = texte; return; }
                const courant = (valeur * (1 - Math.pow(1 - avance, 3))).toFixed(decimales).replace('.', ',');
                cible.textContent = texte.replace(trouve[0], courant);
                requestAnimationFrame(pas);
            })(depart);
        });
    }

    function entrer() {
        if (rideau.classList.contains('ouvert')) return;
        rideau.classList.add('ouvert');
        doc.removeEventListener('keydown', toucheEntrer);
        try { window.parent.sessionStorage.setItem('gaea-entree', '1'); } catch (e) { /* voir plus haut */ }
        setTimeout(compterChiffres, calme ? 0 : 650);
        setTimeout(function () { rideau.remove(); }, calme ? 0 : 1400);
    }
    function toucheEntrer(e) {
        if ((e.key === 'Enter' || e.key === ' ') && rideau.classList.contains('pret')) { e.preventDefault(); entrer(); }
    }
    function pret() {
        rideau.classList.add('pret');
        bouton.focus({ preventScroll: true });
    }

    bouton.addEventListener('click', entrer);
    doc.addEventListener('keydown', toucheEntrer);
    // Pas de bouton avant la fin de l'animation, ni avant que les onglets existent ;
    // au bout de 20 secondes, on le propose quand même.
    const ouverture = performance.now();
    (function attendre() {
        const ecoule = performance.now() - ouverture;
        if (ecoule > 20000 || (ecoule > (calme ? 0 : 3300) && doc.querySelector('[role="tab"]'))) { pret(); return; }
        setTimeout(attendre, 150);
    })();
})();
</script>
"""
_annees_base = df["annee"].dropna().astype(int)
st.iframe(
    OUVERTURE_STREAMLIT
    .replace("%%DEBUT%%", str(_annees_base.min()))
    .replace("%%FIN%%", str(_annees_base.max()))
    .replace("%%PAYS%%", str(df["pays"].nunique()))
    .replace("%%DUREE%%", str(_annees_base.max() - _annees_base.min() + 1)),
    height=1,
)

resultat_precedence = calculer_precedence_temporelle(df)
resultat_cluster = executer_clustering_socio_energetique(df)

# --------------------------------------------------------------
# Bandeau d'accueil : une accroche, trois chiffres calculés en
# direct sur la base et une mini-courbe de la tendance mondiale.
# La courbe ne garde que les pays renseignés chaque année de 1990
# à 2024, pour que l'arrivée de nouveaux pays dans la base ne
# fausse pas l'évolution.
# --------------------------------------------------------------
@st.cache_data
def chiffres_accroche(_df):
    col = "part_renouvelables_dans_electricite"
    d = _df[(_df["annee"] >= 1990) & (_df["annee"] <= 2024)].dropna(subset=[col])
    d2024 = d[d["annee"] == 2024]
    nb_annees = d.groupby("pays")["annee"].nunique()
    pays_complets = nb_annees[nb_annees == 35].index
    serie = d[d["pays"].isin(pays_complets)].groupby("annee")[col].mean()

    progressions = {}
    for pays in PAYS_COMPARAISON:
        v = d[d["pays"] == pays].set_index("annee")[col]
        if 1990 in v.index and 2024 in v.index:
            progressions[pays] = float(v[2024] - v[1990])
    meilleur = max(progressions, key=progressions.get) if progressions else None

    return {
        "moyenne_2024": float(d2024[col].mean()),
        "nb_pays_2024": int(d2024[col].count()),
        "nb_plus_moitie": int((d2024[col] > 50).sum()),
        "serie": serie,
        "nb_pays_serie": len(pays_complets),
        "meilleur": meilleur,
        "meilleure_progression": progressions.get(meilleur),
    }


def mini_courbe_svg(serie, largeur=360, hauteur=150):
    """Petite courbe aire en SVG (sans axes) pour le bandeau d'accueil."""
    annees = list(serie.index)
    valeurs = [float(v) for v in serie.values]
    v_min, v_max = min(valeurs) - 3, max(valeurs) + 3
    def xy(i, v):
        x = 12 + i * (largeur - 24) / (len(valeurs) - 1)
        y = 18 + (v_max - v) * (hauteur - 40) / (v_max - v_min)
        return x, y
    points = [xy(i, v) for i, v in enumerate(valeurs)]
    ligne = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    aire = f"{points[0][0]:.1f},{hauteur - 18} " + ligne + f" {points[-1][0]:.1f},{hauteur - 18}"
    x0, y0 = points[0]
    x1, y1 = points[-1]
    reperes = ""
    for annee in (2000, 2010):
        if annee in annees:
            i = annees.index(annee)
            xr, yr = points[i]
            reperes += (
                f'<line x1="{xr:.1f}" y1="14" x2="{xr:.1f}" y2="{hauteur - 18}" '
                'stroke="rgba(255,255,255,0.16)" stroke-dasharray="3 4"/>'
                f'<circle cx="{xr:.1f}" cy="{yr:.1f}" r="3" fill="#f5e6b8"/>'
                f'<text x="{xr:.1f}" y="{hauteur - 2}" fill="rgba(255,255,255,0.55)" font-size="11" '
                f'text-anchor="middle">{annee}</text>'
            )
    valeur_fin = f"{valeurs[-1]:.1f}".replace(".", ",") + " %"
    return (
        f'<svg viewBox="0 0 {largeur} {hauteur}" width="100%" preserveAspectRatio="none" role="img" '
        f'aria-label="Part moyenne des renouvelables de {annees[0]} à {annees[-1]}">'
        '<defs><linearGradient id="gaeaAire" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#d4a017" stop-opacity="0.45"/>'
        '<stop offset="100%" stop-color="#d4a017" stop-opacity="0"/></linearGradient></defs>'
        f'<polygon points="{aire}" fill="url(#gaeaAire)"/>'
        + reperes +
        f'<polyline points="{ligne}" fill="none" stroke="#f5e6b8" stroke-width="2.6" '
        'stroke-linejoin="round" stroke-linecap="round"/>'
        f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="4" fill="#fff"/>'
        f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="9" fill="#d4a017" opacity="0.35"/>'
        f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="5" fill="#d4a017" stroke="#fff" stroke-width="2"/>'
        f'<text x="{x1 - 12:.1f}" y="{y1 + 4:.1f}" fill="#f5e6b8" font-size="12" font-weight="700" '
        f'text-anchor="end">{valeur_fin}</text>'
        f'<text x="{x0:.1f}" y="{hauteur - 2}" fill="rgba(255,255,255,0.7)" font-size="11">{annees[0]}</text>'
        f'<text x="{x1:.1f}" y="{hauteur - 2}" fill="rgba(255,255,255,0.7)" font-size="11" text-anchor="end">{annees[-1]}</text>'
        '</svg>'
    )


_acc = chiffres_accroche(df)
_serie = _acc["serie"]
_stat_record = ""
if _acc["meilleur"]:
    _stat_record = (
        f'<div class="gaea-stat"><div class="gaea-stat-valeur">+{fmt_fr(_acc["meilleure_progression"], 0)} pts</div>'
        f'<div class="gaea-stat-label">progression record {de_pays(_acc["meilleur"])} depuis 1990, '
        f'parmi les 7 pays suivis</div></div>'
    )
st.markdown(
    '<div class="gaea-hero"><div class="gaea-hero-grid"><div>'
    '<div class="gaea-hero-eyebrow">Projet Trends<span></span>gaea21</div>'
    '<div class="gaea-hero-title">Trends — Énergies renouvelables et GES</div>'
    '<div class="gaea-hero-sub">Le monde produit de plus en plus d\'électricité verte. '
    '<b>Est-ce que cela fait vraiment baisser les émissions ?</b> Ce tableau de bord y répond '
    'en suivant 206 pays et territoires, année après année, de 1990 à 2024.</div>'
    '<div class="gaea-hero-stats">'
    f'<div class="gaea-stat"><div class="gaea-stat-valeur">{fmt_fr(_acc["moyenne_2024"], 1)} %</div>'
    f'<div class="gaea-stat-label">d\'électricité renouvelable en moyenne dans les '
    f'{_acc["nb_pays_2024"]} pays renseignés en 2024</div></div>'
    f'<div class="gaea-stat"><div class="gaea-stat-valeur">{_acc["nb_plus_moitie"]} pays</div>'
    f'<div class="gaea-stat-label">produisent déjà plus de la moitié de leur électricité '
    f'avec des renouvelables</div></div>'
    + _stat_record +
    '</div></div>'
    '<div class="gaea-spark">'
    '<div class="gaea-spark-titre">La transition en une courbe</div>'
    f'<div class="gaea-spark-chiffres"><span>{fmt_fr(float(_serie.iloc[0]), 1)} %</span>'
    f'<span class="gaea-spark-fleche">→</span><b>{fmt_fr(float(_serie.iloc[-1]), 1)} %</b>'
    f'<em class="gaea-spark-badge">+{fmt_fr(round(float(_serie.iloc[-1]), 1) - round(float(_serie.iloc[0]), 1), 1)} pts</em></div>'
    + mini_courbe_svg(_serie) +
    f'<div class="gaea-spark-note">Part moyenne des renouvelables dans l\'électricité des '
    f'{_acc["nb_pays_serie"]} pays suivis sans interruption de 1990 à 2024</div>'
    '</div></div>'
    '<div class="gaea-hero-filet"></div>'
    '</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="gaea-quote">« Dans quelle mesure le développement des énergies renouvelables '
    'contribue-t-il à la réduction des émissions de gaz à effet de serre dans différents pays ? »'
    '<div class="gaea-quote-source">Exploration de cette question pour 206 pays et territoires sur la '
    'période 1990-2024, à partir des données Our World in Data (production électrique, mix énergétique, '
    'émissions de CO2 et de GES) et de la Banque mondiale (PIB par habitant), confrontées aux repères de '
    'Climate Watch, de l\'IRENA et de l\'AIE.</div></div>',
    unsafe_allow_html=True,
)


def bouton_export_pdf():
    # Un simple onclick="window.print()" inséré via st.markdown ne
    # fonctionne pas de façon fiable : Streamlit injecte ce HTML dans le
    # document principal, où les gestionnaires d'événements inline
    # (onclick="...") sont souvent neutralisés par la politique de
    # sécurité du navigateur/Streamlit. On passe donc par
    # st.iframe, qui crée un vrai document HTML (dans une iframe)
    # où un <script> classique peut attacher un addEventListener --
    # et on appelle window.parent.print() pour imprimer la page
    # Streamlit elle-même (la fenêtre parente), et non le contenu vide
    # de l'iframe du bouton.
    #
    # Le bouton était auparavant coupé : la colonne est étroite et,
    # sans consigne explicite, le texte du bouton repassait à la ligne
    # tout en restant contraint par une iframe trop basse (60px) pour
    # afficher deux lignes -- d'où un bouton visuellement tronqué.
    # Le texte est donc forcé sur une seule ligne (white-space: nowrap),
    # la colonne du bouton élargie, et l'iframe rendue transparente et
    # suffisamment haute pour ne plus rogner son contenu.
    st.iframe(
        f"""
        <div style="text-align:right; padding-top:6px; margin:0;
                    font-family:'Inter','Segoe UI',sans-serif;">
            <button id="gaeaBtnExport" style="
                background:linear-gradient(135deg,{GAEA_CORP['accent']},{GAEA_CORP['accent_dark']}); color:white; border:0;
                border-radius:999px; box-shadow:0 8px 18px -10px rgba(77,101,25,0.8); font-weight:600; padding:10px 18px;
                font-size:14px; cursor:pointer; white-space:nowrap;
                font-family:'Inter','Segoe UI',sans-serif;">
                🖨️ Exporter en PDF / Imprimer
            </button>
        </div>
        <script>
        document.getElementById("gaeaBtnExport").addEventListener("click", function() {{
            window.parent.print();
        }});
        </script>
        <style>
            html, body {{ margin:0; padding:0; background:transparent; overflow:hidden; }}
        </style>
        """,
        height=64,
    )



# --------------------------------------------------------------
# Texte historique d'ouverture -- même esprit que le paragraphe
# "Tendances générales" du modèle transmis par le coordinateur :
# un constat global chiffré, puis les contrastes marquants entre
# pays. Calculé dynamiquement sur les 7 pays de comparaison du
# projet (1990-2024), donc toujours à jour si la base évolue.
# --------------------------------------------------------------
_annee_ref_debut, _annee_ref_fin = 1990, 2024
_evol = {}
for _p in PAYS_COMPARAISON:
    _d = df[df["pays"] == _p]
    _vd = _d.loc[_d["annee"] == _annee_ref_debut, "part_renouvelables_dans_electricite"]
    _vf = _d.loc[_d["annee"] == _annee_ref_fin, "part_renouvelables_dans_electricite"]
    if not _vd.empty and not _vf.empty and pd.notna(_vd.values[0]) and pd.notna(_vf.values[0]):
        _evol[_p] = (float(_vd.values[0]), float(_vf.values[0]))

if len(_evol) >= 2:
    _moy_debut = sum(v[0] for v in _evol.values()) / len(_evol)
    _moy_fin = sum(v[1] for v in _evol.values()) / len(_evol)
    _classement = sorted(_evol.items(), key=lambda kv: kv[1][1] - kv[1][0], reverse=True)
    _p1, (_p1d, _p1f) = _classement[0]
    _p2, (_p2d, _p2f) = _classement[1]
    _dernier, (_pld, _plf) = _classement[-1]
    _nom_plus_haut, (_phd, _phf) = max(_evol.items(), key=lambda kv: kv[1][1])

    if _dernier == _nom_plus_haut:
        _phrase_fin = (
            f"il reste malgré tout, avec <b>{fmt_fr(_phf)} %</b> de renouvelables en {_annee_ref_fin}, "
            f"le pays le plus avancé du groupe sur cet indicateur."
        )
    else:
        _phrase_fin = (
            f"tout en restant à un niveau significatif. <b>{avec_article_maj(_nom_plus_haut)}</b> "
            f"est le pays le plus avancé du groupe en {_annee_ref_fin}, avec <b>{fmt_fr(_phf)} %</b> de renouvelables."
        )

    with st.container(border=True):
        st.markdown(
            f'<div class="gaea-section-label">Ce que montrent les 7 pays suivis, '
            f'{_annee_ref_debut} → {_annee_ref_fin}</div>',
            unsafe_allow_html=True,
        )
        narratif(
            f"Entre {_annee_ref_debut} et {_annee_ref_fin}, la part moyenne des énergies renouvelables dans "
            f"l'électricité des 7 pays suivis dans ce sous-projet est passée de <b>{fmt_fr(_moy_debut)} %</b> à "
            f"<b>{fmt_fr(_moy_fin)} %</b>, soit une progression de <b>+{fmt_fr(_moy_fin - _moy_debut)} points</b> sur la "
            f"période. Cette hausse traduit à la fois les politiques de soutien aux renouvelables et la baisse "
            f"du coût des technologies solaires et éoliennes."
        )
        narratif(
            f"Parmi les pays suivis, <b>{avec_article(_p1)}</b> enregistre la progression la plus "
            f"marquée (<b>+{fmt_fr(_p1f - _p1d)} points</b>, de {fmt_fr(_p1d)} % à {fmt_fr(_p1f)} %), suivi "
            f"{de_pays(_p2)} (+{fmt_fr(_p2f - _p2d)} points, de {fmt_fr(_p2d)} % à {fmt_fr(_p2f)} %). "
            f"À l'inverse, <b>{avec_article(_dernier)}</b> affiche un léger recul "
            f"({'+' if _plf - _pld > 0 else ''}{fmt_fr(_plf - _pld)} points) — {_phrase_fin}"
        )

# --------------------------------------------------------------
# Barre latérale : filtres, structurée en blocs comme le modèle
# transmis par le coordinateur de projet (en-têtes en gras par
# groupe de filtres, plutôt qu'un unique bloc "Filtres").
# --------------------------------------------------------------
def entete_filtre(numero, texte):
    st.markdown(
        f'<div class="gaea-filtre-entete"><span class="gaea-filtre-num">{numero}</span>{texte}</div>',
        unsafe_allow_html=True,
    )


# Logo gaea21 en haut de la barre latérale -- ne casse pas l'app si le
# fichier n'est pas trouvé (chemin à adapter selon l'emplacement réel
# du logo dans le projet, ex: "logo.png" ou "rapport_Stage/logo.png").
try:
    st.sidebar.image("logo.png", width=140)
except Exception:
    pass

st.sidebar.markdown(
    '<div class="gaea-filtres-titre">Filtres</div>'
    '<div class="gaea-filtres-sous-titre">Ils s\'appliquent à toutes les analyses, sauf la carte mondiale.</div>',
    unsafe_allow_html=True,
)

top5_par_continent = calculer_top5_par_continent(df)

# --------------------------------------------------------------
# Partage de vue par URL : pré-remplit les filtres depuis les
# paramètres de l'URL au premier chargement (lien partageable),
# avant que les widgets correspondants ne soient créés. Protégé
# par try/except : st.query_params est disponible sur les versions
# récentes de Streamlit uniquement, et ne doit jamais faire planter
# l'app si un paramètre d'URL est absent ou mal formé.
# --------------------------------------------------------------
try:
    _params_url = st.query_params
    if "vue_continent" not in st.session_state and _params_url.get("vue") in (
        ["7 pays de comparaison du projet", "Monde"] + CONTINENTS_DISPONIBLES
    ):
        st.session_state["vue_continent"] = _params_url.get("vue")
    if "periode_slider" not in st.session_state and _params_url.get("debut") and _params_url.get("fin"):
        st.session_state["periode_slider"] = (int(_params_url.get("debut")), int(_params_url.get("fin")))
except Exception:
    _params_url = {}

# Préréglages : un clic remplit zone, tri et pays. Les pastilles se comportent
# comme des boutons (elles se désélectionnent aussitôt après le clic) ; le
# préréglage est appliqué plus bas, avant la création des widgets concernés.
PRESELECTIONS = {
    "Géants mondiaux": {"vue": "Monde", "tri": "décroissant", "tous": True},
    "Europe": {"vue": "Europe", "tri": "décroissant", "tous": True},
    "7 pays du projet": {"vue": "7 pays de comparaison du projet", "tri": "décroissant", "tous": True},
    "Les plus verts": {"vue": None, "tri": "décroissant", "tous": False},
    "Les plus carbonés": {"vue": None, "tri": "croissant", "tous": False},
}
ICONES_PRESELECTION = {
    "Géants mondiaux": ":material/public:", "Europe": ":material/euro:",
    "7 pays du projet": ":material/star:", "Les plus verts": ":material/eco:",
    "Les plus carbonés": ":material/factory:",
}


def _choisir_preselection():
    st.session_state["_preselection"] = st.session_state.get("pastilles_preselection")
    st.session_state["pastilles_preselection"] = None


_preselection = st.session_state.pop("_preselection", None)
if _preselection and PRESELECTIONS[_preselection]["vue"]:
    st.session_state["vue_continent"] = PRESELECTIONS[_preselection]["vue"]

with st.sidebar.container(border=True):
    entete_filtre("★", "Accès rapide")
    st.pills(
        "Accès rapide", options=list(PRESELECTIONS), key="pastilles_preselection",
        format_func=lambda o: f"{ICONES_PRESELECTION[o]} {o}", label_visibility="collapsed",
        on_change=_choisir_preselection,
    )

with st.sidebar.container(border=True):
    entete_filtre(1, "Zone géographique")
    vue = st.selectbox(
        "Vue",
        options=["7 pays de comparaison du projet", "Monde"] + CONTINENTS_DISPONIBLES,
        key="vue_continent",
        label_visibility="collapsed",
    )
    st.caption("Propose les 5 plus grands producteurs d'électricité de la zone.")

if vue == "7 pays de comparaison du projet":
    pool_pays = [p for p in PAYS_COMPARAISON if p in df["pays"].unique()]
else:
    pool_pays = top5_par_continent.get(vue, [])

with st.sidebar.container(border=True):
    entete_filtre(2, "Pays à comparer")
    if not pool_pays:
        st.warning(f"Aucune donnée disponible pour « {vue} ».")
        pays_selectionnes = []
    else:

        # ---- Valeur de référence par pays (dernière année disponible, part des
        # renouvelables) -- utilisée à la fois pour le tri et pour l'affichage
        # dans la liste, dans l'esprit du panneau de sélection d'Our World in Data. ----
        _valeurs_pool = {}
        for _p in pool_pays:
            _d = df[df["pays"] == _p].dropna(subset=["part_renouvelables_dans_electricite"])
            if not _d.empty:
                _ligne = _d.sort_values("annee").iloc[-1]
                _valeurs_pool[_p] = (float(_ligne["part_renouvelables_dans_electricite"]), int(_ligne["annee"]))
            else:
                _valeurs_pool[_p] = (None, None)

        _options_tri = ["Plus verts d'abord", "Moins verts d'abord"]
        # une valeur d'une ancienne version des libellés ne doit pas bloquer le widget
        if st.session_state.get(f"tri_pays_{vue}") not in (None, *_options_tri):
            del st.session_state[f"tri_pays_{vue}"]
        if _preselection:
            st.session_state[f"recherche_pays_{vue}"] = ""
            st.session_state[f"tri_pays_{vue}"] = (
                _options_tri[0] if PRESELECTIONS[_preselection]["tri"] == "décroissant" else _options_tri[1]
            )

        _recherche = st.text_input(
            "Rechercher un pays", key=f"recherche_pays_{vue}", label_visibility="collapsed",
            placeholder="Rechercher : France, Chine…",
            icon=":material/search:",
        )
        _tri = st.selectbox(
            "Trier par",
            options=_options_tri,
            key=f"tri_pays_{vue}",
            help="Classe les pays selon leur part d'électricité renouvelable (dernière année connue) "
                 "et présélectionne les 3 premiers (modifiable ensuite).",
        )

        _termes_recherche = [t.strip().lower() for t in _recherche.split(",") if t.strip()]
        if _termes_recherche:
            _pool_affiche = [
                p for p in pool_pays
                if any(t in NOMS_FR.get(p, p).lower() for t in _termes_recherche)
            ]
        else:
            _pool_affiche = list(pool_pays)

        if _tri == _options_tri[0]:
            _pool_affiche.sort(key=lambda p: (_valeurs_pool[p][0] is None, -(_valeurs_pool[p][0] or 0)))
        else:
            _pool_affiche.sort(key=lambda p: (_valeurs_pool[p][0] is None, _valeurs_pool[p][0] or 0))

        def _libelle_pays(p):
            valeur, annee = _valeurs_pool.get(p, (None, None))
            nom = NOMS_FR.get(p, p)
            if valeur is None:
                return f"{nom} (n/d)"
            return f"{nom} · {fmt_fr(valeur, decimales=0)} %"

        if not _pool_affiche:
            st.caption("Aucun pays ne correspond à cette recherche.")
            pays_selectionnes = []
        else:
            # Pas de mémoire cachée entre deux recherches : ce qui est affiché
            # (et coché) dans la liste EST la sélection utilisée par les
            # graphiques, directement -- plus simple et plus prévisible que
            # l'ancienne version, qui gardait en mémoire les pays masqués par
            # une recherche et donnait l'impression que la recherche "ne
            # suivait pas" sur les graphiques.
            # Sans recherche active : ne pré-sélectionne que le top 3 selon le
            # classement choisi (plutôt que tout le monde), pour que changer le
            # classement ait un effet visible immédiat sur les graphiques.
            # Avec une recherche active : garde tous les pays trouvés.
            if _recherche.strip():
                _defaut_widget = list(_pool_affiche)
            else:
                _defaut_widget = _pool_affiche[:3] if len(_pool_affiche) > 3 else list(_pool_affiche)
                # Les pays de l'adresse (lien partagé) ne servent qu'au premier chargement :
                # ensuite, un changement de tri présélectionne bien les 3 premiers du classement.
                try:
                    if _params_url.get("pays") and not st.session_state.get("_pays_url_utilises"):
                        _pays_url = [p for p in _params_url.get("pays").split(",") if p in _pool_affiche]
                        if _pays_url:
                            _defaut_widget = _pays_url
                            st.session_state["_pays_url_utilises"] = True
                except Exception:
                    pass

            _cle_pays = f"pays_widget_{vue}_{_recherche}_{_tri}"
            if _preselection:
                st.session_state[_cle_pays] = (
                    list(_pool_affiche) if PRESELECTIONS[_preselection]["tous"] else _pool_affiche[:3]
                )
            pays_selectionnes = st.multiselect(
                "Pays",
                options=_pool_affiche,
                default=None if _cle_pays in st.session_state else _defaut_widget,
                format_func=_libelle_pays,
                placeholder="Choisir un ou plusieurs pays…",
                # La clé change avec la recherche/le tri : un changement de
                # recherche ou de tri redonne donc une sélection "propre"
                # (tous les pays actuellement affichés), plutôt que de garder
                # une ancienne sélection invisible.
                key=_cle_pays,
                label_visibility="collapsed",
            )

with st.sidebar.container(border=True):
    entete_filtre(3, "Période")
    annee_min_dispo = int(df["annee"].min())
    annee_max_dispo = int(df["annee"].max())
    _periodes_rapides = {
        "Tout": (annee_min_dispo, annee_max_dispo),
        "Depuis 2000": (max(2000, annee_min_dispo), annee_max_dispo),
        "10 dernières années": (annee_max_dispo - 9, annee_max_dispo),
    }

    def _choisir_periode():
        choix = st.session_state.get("pastilles_periode")
        if choix:
            st.session_state["periode_slider"] = _periodes_rapides[choix]
        st.session_state["pastilles_periode"] = None

    st.pills("Période rapide", options=list(_periodes_rapides), key="pastilles_periode",
             label_visibility="collapsed", on_change=_choisir_periode)
    # Valeur initiale posée dans la session plutôt que via value=, pour ne pas
    # entrer en conflit avec les périodes rapides et le lien partagé.
    st.session_state.setdefault("periode_slider", (annee_min_dispo, annee_max_dispo))
    periode = st.slider(
        "Période", min_value=annee_min_dispo, max_value=annee_max_dispo,
        key="periode_slider",
        label_visibility="collapsed",
    )

if pays_selectionnes:
    _pastilles = "".join(f'<span class="gaea-sel-pays">{NOMS_FR.get(p, p)}</span>' for p in pays_selectionnes)
    # Jauge : part moyenne des renouvelables de la sélection (dernière année connue
    # de la période, pour chaque pays) face à la moyenne de tous les pays en 2024.
    _parts_sel = []
    for _p in pays_selectionnes:
        _d = df[(df["pays"] == _p) & (df["annee"] <= periode[1])].dropna(subset=["part_renouvelables_dans_electricite"])
        if not _d.empty:
            _parts_sel.append(float(_d.sort_values("annee").iloc[-1]["part_renouvelables_dans_electricite"]))
    _jauge = ""
    if _parts_sel:
        _moy_sel = sum(_parts_sel) / len(_parts_sel)
        _moy_monde = _acc["moyenne_2024"]
        _jauge = (
            f'<div class="gaea-jauge-legende"><span>Renouvelables</span><b>{fmt_fr(_moy_sel)} %</b></div>'
            f'<div class="gaea-jauge"><div class="gaea-jauge-rempli" style="width:{min(_moy_sel, 100):.1f}%"></div>'
            f'<div class="gaea-jauge-repere" style="left:{min(_moy_monde, 100):.1f}%"></div></div>'
            f'<div class="gaea-jauge-note">Repère : moyenne de tous les pays en 2024 ({fmt_fr(_moy_monde)} %)'
            f'{" · ta sélection fait mieux" if _moy_sel > _moy_monde else ""}</div>'
        )
    st.sidebar.markdown(
        f'<div class="gaea-sel"><div class="gaea-sel-titre">Ta sélection</div>'
        f'<div class="gaea-sel-chiffres"><b>{len(pays_selectionnes)}</b> pays · <b>{periode[0]}–{periode[1]}</b></div>'
        f'<div class="gaea-sel-liste">{_pastilles}</div>{_jauge}</div>',
        unsafe_allow_html=True,
    )
if st.sidebar.button("Réinitialiser les filtres", icon=":material/restart_alt:", width="stretch"):
    _prefixes_a_effacer = ("pays_widget_", "selection_pays_", "recherche_pays_", "tri_pays_")
    for _cle in list(st.session_state.keys()):
        if _cle in ("vue_continent", "periode_slider") or _cle.startswith(_prefixes_a_effacer):
            del st.session_state[_cle]
    st.rerun()
with st.sidebar.expander("Guide express", icon=":material/help:"):
    st.markdown(
        '<div class="gaea-guide">'
        '<div><span>1</span><p><b>Choisis tes pays</b> : un accès rapide, ou une zone puis les pays.</p></div>'
        '<div><span>2</span><p><b>Règle la période</b> : tout, depuis 2000 ou les 10 dernières années.</p></div>'
        '<div><span>3</span><p><b>Explore les onglets</b> : chaque analyse finit par un encadré « À retenir ».</p></div>'
        '</div>',
        unsafe_allow_html=True,
    )
st.sidebar.markdown(
    '<div class="gaea-filtres-note">🔗 L\'adresse de la page garde tes filtres : copie-la pour partager cette vue.</div>',
    unsafe_allow_html=True,
)

if not pays_selectionnes:
    st.warning("Sélectionne au moins un pays dans la barre latérale pour cette vue.")
    st.stop()

df_filtre = df[
    df["pays"].isin(pays_selectionnes)
    & df["annee"].between(periode[0], periode[1])
].copy()
df_filtre["pays_fr"] = df_filtre["pays"].map(NOMS_FR).fillna(df_filtre["pays"])

# Réécrit l'état courant des filtres dans l'URL, pour que le lien affiché
# dans le navigateur soit toujours partageable tel quel (copier-coller
# rouvre la même vue). Protégé par try/except pour la même raison que
# ci-dessus (disponibilité de st.query_params selon la version).
try:
    st.query_params["vue"] = vue
    st.query_params["debut"] = str(periode[0])
    st.query_params["fin"] = str(periode[1])
    st.query_params["pays"] = ",".join(pays_selectionnes)
except Exception:
    pass

if df_filtre.empty:
    st.warning("Aucune donnée pour cette sélection. Choisis au moins un pays.")
    st.stop()

# --------------------------------------------------------------
# Indicateurs clés (équivalent de la bannière KPI du dashboard natif)
# --------------------------------------------------------------
derniere_annee = int(df_filtre["annee"].max())
moy_renouv = df_filtre.loc[df_filtre["annee"] == derniere_annee, "part_renouvelables_dans_electricite"].mean()
moy_intens = df_filtre.loc[df_filtre["annee"] == derniere_annee, "intensite_carbone_electricite"].mean()

# ---- Tendance vs 5 ans plus tôt (ou le début de la période si plus courte) ----
_annee_comparaison = max(int(df_filtre["annee"].min()), derniere_annee - 5)
_moy_renouv_comp = df_filtre.loc[df_filtre["annee"] == _annee_comparaison, "part_renouvelables_dans_electricite"].mean()
_moy_intens_comp = df_filtre.loc[df_filtre["annee"] == _annee_comparaison, "intensite_carbone_electricite"].mean()

_delta_renouv = None
if pd.notna(moy_renouv) and pd.notna(_moy_renouv_comp) and _annee_comparaison != derniere_annee:
    _ecart = moy_renouv - _moy_renouv_comp
    _delta_renouv = {
        "sens": "hausse" if _ecart > 0.05 else ("baisse" if _ecart < -0.05 else "neutre"),
        "texte": f"{_ecart:+.1f} pts vs {_annee_comparaison}".replace(".", ","),
    }

_delta_intens = None
if pd.notna(moy_intens) and pd.notna(_moy_intens_comp) and _annee_comparaison != derniere_annee:
    _ecart = moy_intens - _moy_intens_comp
    _delta_intens = {
        "sens": "hausse" if _ecart > 0.5 else ("baisse" if _ecart < -0.5 else "neutre"),
        "texte": f"{_ecart:+.0f} gCO2/kWh vs {_annee_comparaison}",
    }

_col_selection, _col_export = st.columns([4, 1.4], vertical_alignment="center")
with _col_selection:
    st.markdown(
        f'<div class="gaea-section-label">Votre sélection · {derniere_annee}</div>',
        unsafe_allow_html=True,
    )
with _col_export:
    bouton_export_pdf()

cartes_kpi([
    {"icone": "🌐", "valeur": len(pays_selectionnes), "label": "Pays sélectionnés",
     "couleur": GAEA_CORP["brown"]},
    {"icone": "📊", "valeur": fmt_fr(len(df_filtre), decimales=0), "label": "Observations",
     "couleur": "#3d346b"},
    {"icone": "🌱", "valeur": fmt_fr(moy_renouv, decimales=1, suffixe=" %"),
     "label": f"Moy. renouvelables ({derniere_annee})", "delta": _delta_renouv,
     "couleur": GAEA_CORP["accent_dark"]},
    {"icone": "🏭", "valeur": fmt_fr(moy_intens, decimales=0, suffixe=" gCO2/kWh"),
     "label": f"Moy. intensité carbone ({derniere_annee})", "delta": _delta_intens,
     "couleur": GAEA_CORP["accent_rouge"]},
])

# --------------------------------------------------------------
# Onglets
# --------------------------------------------------------------
# Ancre des onglets et bouton flottant pour y revenir depuis n'importe où dans la page
# (la barre d'onglets ne suit plus le défilement, pour ne jamais masquer le contenu).
st.markdown(
    '<div id="analyses"></div>'
    '<a class="gaea-retour-onglets" href="#analyses" title="Revenir aux onglets">'
    '<span>↑</span><em>Analyses</em></a>',
    unsafe_allow_html=True,
)
onglet_transition, onglet2, onglet3, onglet_objectif, onglet5, onglet6, onglet_cluster, onglet8, onglet9 = st.tabs([
    ":material/swap_horiz: Transition énergétique", ":material/hub: Corrélation renouvelables / carbone",
    ":material/trending_up: Projection", ":material/flag: Simulateur d'objectif",
    ":material/factory: CO2 & GES", ":material/compare_arrows: Comparaison pays",
    ":material/scatter_plot: Cluster socio-économique", ":material/science: Tests statistiques",
    ":material/public: Carte",
])

with onglet_transition:
    st.subheader("Progression des renouvelables et baisse de l'intensité carbone")
    objectif("Vérifier, pays par pays, que la hausse des renouvelables va de pair avec une électricité "
             "moins carbonée.")

    pivot_transition_renouv = df_filtre.pivot_table(
        index="annee", columns="pays_fr", values="part_renouvelables_dans_electricite"
    )
    pivot_transition_intensite = df_filtre.pivot_table(
        index="annee", columns="pays_fr", values="intensite_carbone_electricite"
    )

    col_trans1, col_trans2 = st.columns(2)
    with col_trans1:
        with st.container(border=True):
            fig = graphique_lignes(pivot_transition_renouv, titre_y="Part des renouvelables (%)", hauteur=420)
            st.plotly_chart(fig, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_transition_renouv")
            st.caption("Part des renouvelables dans l'électricité, une courbe par pays.")
    with col_trans2:
        with st.container(border=True):
            fig = graphique_lignes(pivot_transition_intensite, titre_y="Intensité carbone (gCO2/kWh)", hauteur=420)
            st.plotly_chart(fig, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_transition_intensite")
            st.caption("Intensité carbone de l'électricité, une courbe par pays.")

    # « À retenir » : meilleure progression des renouvelables (ancien onglet Évolution)
    # et plus forte baisse de l'intensité carbone, sur la période choisie.
    _phrases_transition = []
    if not pivot_transition_renouv.empty:
        _an_debut = pivot_transition_renouv.index.min()
        _debut = pivot_transition_renouv.loc[_an_debut]
        _fin = (pivot_transition_renouv.loc[derniere_annee] if derniere_annee in pivot_transition_renouv.index
                else pivot_transition_renouv.iloc[-1])
        _progression = (_fin - _debut).dropna()
        if not _progression.empty and not _fin.dropna().empty:
            _pays_prog, _pays_tete = _progression.idxmax(), _fin.idxmax()
            _phrase = (
                f"Plus forte progression des renouvelables : <b>{_pays_prog}</b> (<b>{_progression[_pays_prog]:+.1f} "
                f"points</b>, de {_debut[_pays_prog]:.1f} % à {_fin[_pays_prog]:.1f} % entre {int(_an_debut)} et "
                f"{derniere_annee})"
            )
            if _pays_tete == _pays_prog:
                _phrase += ", qui finit <b>en tête</b> de la sélection."
            else:
                _phrase += f" ; en tête : <b>{_pays_tete}</b> avec <b>{_fin[_pays_tete]:.1f} %</b>."
            _phrases_transition.append(_phrase)
    if derniere_annee in pivot_transition_intensite.index and not pivot_transition_intensite.empty:
        _baisse = (pivot_transition_intensite.iloc[0] - pivot_transition_intensite.loc[derniere_annee]).dropna()
        if not _baisse.empty:
            _pays_baisse = _baisse.idxmax()
            _phrases_transition.append(
                f"Plus forte baisse de l'intensité carbone : <b>{_pays_baisse}</b> (<b>{_baisse[_pays_baisse]:.0f} gCO2/kWh "
                f"de moins</b> depuis {int(pivot_transition_intensite.index.min())})."
            )
    if _phrases_transition:
        a_retenir("<br>".join(_phrases_transition))

    bouton_telechargement_csv(
        pivot_transition_renouv.join(pivot_transition_intensite, lsuffix=" (renouv. %)", rsuffix=" (intensité)"),
        "transition_energetique.csv",
    )

with onglet2:
    st.subheader("Renouvelables vs intensité carbone de l'électricité")
    objectif("Mesurer à quel point plus de renouvelables rime avec une électricité moins carbonée.")
    nuage = df_filtre.dropna(subset=["part_renouvelables_dans_electricite", "intensite_carbone_electricite"])

    with st.container(border=True):
        fig = graphique_nuage(
            nuage, x="part_renouvelables_dans_electricite", y="intensite_carbone_electricite",
            colonne_couleur="pays_fr",
            titre_x="Part des renouvelables (%)", titre_y="Intensité carbone (gCO2/kWh)",
        )
        st.plotly_chart(fig, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_correlation_nuage")
        st.caption("La ligne en pointillé bordeaux est la droite de régression linéaire (NumPy polyfit) sur l'ensemble des points.")

    r, n, t, ddl, p = correlation_pearson_avec_p(
        nuage["part_renouvelables_dans_electricite"].to_numpy(),
        nuage["intensite_carbone_electricite"].to_numpy(),
    )
    if r is None:
        st.warning("Pas assez de points pour calculer une corrélation (minimum 3).")
    else:
        cartes_kpi([
            {"icone": "📐", "valeur": fmt_fr(r, decimales=3), "label": "Corrélation r (Pearson)",
             "couleur": GAEA_CORP["accent_rouge"]},
            {"icone": "🔢", "valeur": f"n = {fmt_fr(n, decimales=0)}", "label": "Taille d'échantillon",
             "couleur": GAEA_CORP["accent_dark"]},
            {"icone": "🎯", "valeur": "< 0,001" if p is not None and p < 0.001 else (fmt_fr(p, decimales=3) if p is not None else "n/d"),
             "label": "p-valeur bilatérale", "couleur": "#3d346b"},
        ])

        if p is not None and p < 0.05:
            sens = "négative" if r < 0 else "positive"
            a_retenir(
                f"Corrélation <b>{sens} forte et significative</b> (r = {r:.2f}, p &lt; 0,05) sur {n} observations : "
                + ("<b>plus un pays a d'électricité renouvelable, moins elle est carbonée</b>."
                   if r < 0 else "les deux indicateurs augmentent ensemble, à l'inverse de l'attendu.")
            )
        else:
            a_retenir(f"Pas de corrélation significative avec cette sélection (r = {r:.2f}, p ≥ 0,05) : "
                      "élargis la sélection de pays.")

    st.caption(
        "Test 1 : corrélation et p-valeur calculées avec `numpy.corrcoef` et la loi de Student, sur l'ensemble "
        "des observations pays-années de la sélection (et non par pays pris isolément). "
        "Les tests 2 et 3 sont dans l'onglet Tests statistiques."
    )
    bouton_telechargement_csv(
        nuage[["pays_fr", "annee", "part_renouvelables_dans_electricite", "intensite_carbone_electricite"]],
        "correlation_renouvelables_intensite.csv",
    )

    st.divider()
    st.subheader("Au-delà de la corrélation : un décalage temporel ?")
    objectif("Voir si la baisse de l'intensité carbone suit la hausse des renouvelables avec quelques années "
             "de retard.")
    st.caption("Variations annuelles · 206 pays de la base, quelle que soit la sélection.")
    with st.container(border=True):
        fig_precedence = graphique_precedence_temporelle(resultat_precedence)
        st.plotly_chart(fig_precedence, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_precedence")
        st.caption("La barre bordeaux marque le décalage donnant la corrélation la plus forte (la plus négative).")
    a_retenir(texte_precedence_temporelle(resultat_precedence))

with onglet3:
    st.subheader("Projection : droite ou courbe en S, départagées par backtest")
    objectif("Prolonger la tendance d'un pays jusqu'en 2050 avec deux modèles, puis garder celui qui aurait le "
             "mieux prédit les 5 dernières années connues.")
    pays_pour_projection = st.selectbox(
        "Pays", options=pays_selectionnes, format_func=lambda p: NOMS_FR.get(p, p), key="pays_projection"
    )

    sous_df = df_filtre[df_filtre["pays"] == pays_pour_projection].dropna(
        subset=["annee", "part_renouvelables_dans_electricite"]
    ).sort_values("annee")
    annees_np = sous_df["annee"].to_numpy(dtype=float)
    valeurs_np = sous_df["part_renouvelables_dans_electricite"].to_numpy(dtype=float)

    with st.spinner("Ajustement des deux modèles et backtest…"):
        modeles = {}
        for mode, ajuster in (("lineaire", regression_numpy), ("logistique", regression_logistique_numpy)):
            pente_m, ordonnee_m, r2_m = ajuster(annees_np, valeurs_np)
            if pente_m is not None:
                modeles[mode] = {
                    "pente": pente_m, "ordonnee": ordonnee_m, "r2": r2_m,
                    "backtest": backtest_numpy(annees_np, valeurs_np, n_annees_test=5, mode=mode),
                }

    if "lineaire" not in modeles:
        st.warning("Pas assez de données pour ce pays sur la période sélectionnée.")
    else:
        NOMS_MODELES = {"lineaire": "droite", "logistique": "courbe en S"}
        # Modèle retenu : la plus petite erreur de backtest ; à défaut de backtest, la courbe en S
        # (bornée entre 0 et 100 %) si elle a pu être ajustée.
        avec_backtest = {m: v["backtest"]["mae"] for m, v in modeles.items() if v["backtest"] is not None}
        if avec_backtest:
            modele_retenu = min(avec_backtest, key=avec_backtest.get)
        else:
            modele_retenu = "logistique" if "logistique" in modeles else "lineaire"
        autre = "lineaire" if modele_retenu == "logistique" else "logistique"

        annee_fin = int(annees_np.max())
        annees_courbe = np.arange(annee_fin, 2051)
        annees_futures = np.array([2030, 2040, 2050])
        courbes = {
            m: np.clip(predire_modele(m, v["pente"], v["ordonnee"], annees_courbe), 0, 100)
            for m, v in modeles.items()
        }
        projections = np.clip(
            predire_modele(modele_retenu, modeles[modele_retenu]["pente"], modeles[modele_retenu]["ordonnee"],
                           annees_futures), 0, 100,
        )

        with st.container(border=True):
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=annees_np, y=valeurs_np, mode="lines+markers", name="Historique",
                line=dict(width=3, color=GAEA_CORP["accent_dark"]), marker=dict(size=6),
            ))
            styles = {
                "lineaire": dict(color=GAEA_CORP["brown"], dash="dot"),
                "logistique": dict(color="#d4a017", dash="dash"),
            }
            for m in modeles:
                retenu = m == modele_retenu
                fig.add_trace(go.Scatter(
                    x=annees_courbe, y=courbes[m], mode="lines",
                    name=f"{NOMS_MODELES[m][0].upper()}{NOMS_MODELES[m][1:]}{' (retenue)' if retenu else ''}",
                    line=dict(width=4 if retenu else 2, **styles[m]), opacity=1 if retenu else 0.45,
                    hovertemplate="%{x} : %{y:.1f} %<extra>" + NOMS_MODELES[m] + "</extra>",
                ))
            fig.add_hline(y=100, line_dash="dot", line_color="rgba(46,43,38,0.25)", line_width=1)
            fig = theme_plotly(fig, hauteur=440, titre_x="Année", titre_y="Part des renouvelables (%)")
            fig.update_yaxes(range=[0, 105])
            st.plotly_chart(fig, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_projection")
            st.caption("Trait plein = historique · pointillé marron = droite · tirets dorés = courbe en S (plafond "
                       "100 %). Le modèle retenu est tracé en gras.")

        # Duel des deux modèles : erreur de backtest de chacun
        _couleurs_modeles = {"lineaire": GAEA_CORP["brown"], "logistique": "#b8860b"}
        cartes_kpi(
            [{"icone": "🏆" if m == modele_retenu else "📏",
              "valeur": (f"{fmt_fr(v['backtest']['mae'])} pts" if v["backtest"] is not None else "n/d"),
              "label": f"Erreur de la {NOMS_MODELES[m]} (backtest)"
                       + (" · retenue" if m == modele_retenu else ""),
              "couleur": _couleurs_modeles[m]}
             for m, v in modeles.items()]
        )
        cartes_kpi(
            [{"icone": "🗓️", "valeur": fmt_fr(val, decimales=1, suffixe=" %"), "label": f"Projection {an}",
              "couleur": c}
             for (an, val), c in zip(zip(annees_futures, projections),
                                     [GAEA_CORP["accent_dark"], GAEA_CORP["accent"], "#3f5414"])]
        )

        _mae_retenu = avec_backtest.get(modele_retenu)
        if _mae_retenu is None:
            _fiabilite = "historique trop court pour tester la fiabilité"
        elif _mae_retenu < 3:
            _fiabilite = "🟢 <b>fiable</b>"
        elif _mae_retenu < 7:
            _fiabilite = "🟠 <b>à prendre avec recul</b>"
        else:
            _fiabilite = "🔴 <b>peu fiable</b>, la tendance a changé récemment"

        _retenir_projection = f"Modèle retenu : <b>la {NOMS_MODELES[modele_retenu]}</b>"
        if _mae_retenu is not None and avec_backtest.get(autre) is not None:
            _retenir_projection += (
                f", qui se trompe de <b>{_mae_retenu:.1f} points</b> sur les 5 dernières années connues, contre "
                f"{avec_backtest[autre]:.1f} pour la {NOMS_MODELES[autre]}"
            )
        _retenir_projection += (
            f". Pour <b>{avec_article(pays_pour_projection)}</b>, elle projette <b>{projections[-1]:.1f} %</b> "
            f"de renouvelables en 2050 : projection {_fiabilite}."
        )
        if modele_retenu == "lineaire" and courbes["lineaire"][-1] >= 99.9:
            _retenir_projection += " <i>La droite dépasse 100 % avant 2050 : la valeur est plafonnée.</i>"
        a_retenir(_retenir_projection)

        tableau_projection = pd.DataFrame(
            {f"{NOMS_MODELES[m][0].upper()}{NOMS_MODELES[m][1:]} (%)": courbes[m] for m in modeles}, index=annees_courbe
        )
        tableau_projection.index.name = "Année"
        bouton_telechargement_csv(tableau_projection, f"projection_{pays_pour_projection}.csv")

with onglet_objectif:
    st.subheader("Simulateur d'objectif : quelle trajectoire pour atteindre une cible ?")
    objectif("Choisir une cible de renouvelables et un horizon : l'outil calcule le rythme à tenir et le "
             "compare au rythme réel du pays.")

    with st.form("form_objectif"):
        col_pays_obj, col_annee_obj = st.columns([2, 1])
        with col_pays_obj:
            pays_objectif = st.selectbox(
                "Pays", options=pays_selectionnes, format_func=lambda p: NOMS_FR.get(p, p), key="pays_objectif"
            )
        with col_annee_obj:
            annee_cible = st.selectbox(
                "Horizon", options=[2030, 2035, 2040, 2050], index=0, key="annee_cible_objectif"
            )

        sous_df_obj = df_filtre[df_filtre["pays"] == pays_objectif].dropna(
            subset=["annee", "part_renouvelables_dans_electricite"]
        ).sort_values("annee")
        nom_pays_fr_obj = NOMS_FR.get(pays_objectif, pays_objectif)

        # ---------------------------------------------------------------
        # Tout est calculé AVANT le moindre affichage, avec des valeurs
        # par défaut sûres (None / tableaux vides) plutôt que des blocs
        # entiers sautés selon les cas -- même principe que le correctif
        # déjà appliqué ailleurs à l'erreur React "removeChild" : la
        # disposition affichée doit rester identique d'un rendu à
        # l'autre, seul le contenu (texte, valeurs, traces du graphique)
        # doit varier.
        # ---------------------------------------------------------------
        annee_actuelle_obj = None
        valeur_actuelle_obj = None
        annees_np_obj = np.array([])
        valeurs_np_obj = np.array([])

        if not sous_df_obj.empty:
            annee_actuelle_obj = int(sous_df_obj["annee"].max())
            valeur_actuelle_obj = float(
                sous_df_obj.loc[sous_df_obj["annee"] == annee_actuelle_obj, "part_renouvelables_dans_electricite"].iloc[0]
            )
            annees_np_obj = sous_df_obj["annee"].to_numpy(dtype=float)
            valeurs_np_obj = sous_df_obj["part_renouvelables_dans_electricite"].to_numpy(dtype=float)

        st.caption(
            (f"Valeur actuelle ({annee_actuelle_obj}) : {fmt_fr(valeur_actuelle_obj, 1, ' %')}. "
             if annee_actuelle_obj is not None else "Valeur actuelle : n/d. ")
            + "Objectifs indicatifs à titre d'exemple, à affiner ensuite avec le curseur : 45 % (ambitieux), "
              "70 % (transition avancée), 100 % (neutralité électrique)."
        )
        valeur_defaut_curseur = float(min(100.0, valeur_actuelle_obj + 20)) if valeur_actuelle_obj is not None else 50.0
        valeur_cible = st.slider(
            f"Objectif de part des renouvelables en {annee_cible} (%)",
            min_value=0.0, max_value=100.0,
            value=valeur_defaut_curseur,
            step=1.0, format="%.0f %%", key="valeur_cible_objectif",
        )

        # Le formulaire regroupe pays / horizon / curseur : les calculs et le
        # graphique ci-dessous ne se mettent à jour qu'au clic sur ce bouton,
        # plutôt qu'à chaque pixel glissé sur le curseur -- ce qui limite le
        # nombre de rendus successifs déclenchés en rafale, l'une des causes
        # possibles des erreurs "removeChild" (deux rendus qui se chevauchent
        # lors d'une interaction rapide).
        st.form_submit_button("🎯 Calculer la trajectoire")

    verdict, symbole = "Données insuffisantes", "⚪"
    explication = f"Pas de données disponibles pour <b>{nom_pays_fr_obj}</b> sur cet indicateur."
    rythme_historique = None
    rythme_necessaire = None
    trajectoire_actuelle_cible = None

    if annee_actuelle_obj is not None:
        with st.spinner("Calcul du rythme historique et de la trajectoire nécessaire…"):
            pente_hist, _, _ = regression_numpy(annees_np_obj, valeurs_np_obj)
        rythme_historique = pente_hist
        nb_annees_obj = annee_cible - annee_actuelle_obj

        if nb_annees_obj <= 0:
            verdict, symbole = "Horizon invalide", "⚪"
            explication = "L'horizon choisi doit être postérieur à la dernière année disponible pour ce pays."
        else:
            rythme_necessaire = (valeur_cible - valeur_actuelle_obj) / nb_annees_obj
            if rythme_historique is not None:
                trajectoire_actuelle_cible = float(
                    np.clip(valeur_actuelle_obj + rythme_historique * nb_annees_obj, 0, 100)
                )

            if valeur_cible <= valeur_actuelle_obj:
                verdict, symbole = "Objectif déjà atteint", "🟢"
                explication = (
                    f"<b>{nom_pays_fr_obj}</b> a déjà atteint {fmt_fr(valeur_actuelle_obj, 1, ' %')} de "
                    f"renouvelables en {annee_actuelle_obj}, au-dessus de l'objectif de "
                    f"{fmt_fr(valeur_cible, 1, ' %')} fixé pour {annee_cible}."
                )
            elif rythme_historique is None:
                verdict, symbole = "Historique insuffisant", "⚪"
                explication = (
                    "Pas assez de données historiques pour ce pays pour comparer à un rythme réel observé."
                )
            elif rythme_historique <= 0:
                verdict, symbole = "Hors trajectoire", "🔴"
                explication = (
                    f"<b>{nom_pays_fr_obj}</b> stagne ou recule actuellement "
                    f"({fmt_fr(rythme_historique, 2, ' points/an')}), alors qu'il faudrait progresser de "
                    f"<b>{fmt_fr(rythme_necessaire, 2, ' points/an')}</b> pour atteindre "
                    f"{fmt_fr(valeur_cible, 1, ' %')} en {annee_cible}."
                )
            else:
                ratio = rythme_necessaire / rythme_historique
                if ratio <= 1:
                    verdict, symbole = "Trajectoire suffisante", "🟢"
                    explication = (
                        f"Le rythme actuel (<b>{fmt_fr(rythme_historique, 2, ' points/an')}</b>) suffit : "
                        f"l'objectif ne demande que <b>{fmt_fr(rythme_necessaire, 2, ' points/an')}</b>."
                    )
                elif ratio <= 2:
                    verdict, symbole = "Accélération modérée nécessaire", "🟡"
                    explication = (
                        f"Il faudrait progresser à <b>{fmt_fr(rythme_necessaire, 2, ' points/an')}</b>, soit "
                        f"environ <b>{ratio:.1f}×</b> le rythme historique observé "
                        f"({fmt_fr(rythme_historique, 2, ' points/an')})."
                    )
                else:
                    verdict, symbole = "Accélération majeure nécessaire", "🔴"
                    explication = (
                        f"Il faudrait progresser à <b>{fmt_fr(rythme_necessaire, 2, ' points/an')}</b>, soit "
                        f"environ <b>{ratio:.1f}×</b> le rythme historique observé "
                        f"({fmt_fr(rythme_historique, 2, ' points/an')}) — un effort important."
                    )

    # ---------------------------------------------------------------
    # Affichage : structure fixe, quel que soit le cas ci-dessus.
    # ---------------------------------------------------------------

    cartes_kpi([
        {"icone": "📍", "valeur": fmt_fr(valeur_actuelle_obj, 1, " %"),
         "label": f"Valeur actuelle ({annee_actuelle_obj})" if annee_actuelle_obj is not None else "Valeur actuelle",
         "couleur": GAEA_CORP["accent_dark"]},
        {"icone": "🎯", "valeur": fmt_fr(valeur_cible, 1, " %"), "label": f"Objectif {annee_cible}",
         "couleur": GAEA_CORP["accent_rouge"]},
        {"icone": "📈", "valeur": fmt_fr(rythme_historique, 2, " pts/an"), "label": "Rythme historique",
         "couleur": GAEA_CORP["brown"]},
        {"icone": "🚀", "valeur": fmt_fr(rythme_necessaire, 2, " pts/an"), "label": "Rythme nécessaire",
         "couleur": "#3d346b"},
    ])

    with st.container(border=True):
        fig = go.Figure()
        if len(annees_np_obj) > 0:
            fig.add_trace(go.Scatter(
                x=annees_np_obj, y=valeurs_np_obj, mode="lines+markers", name="Historique",
                line=dict(width=3, color=GAEA_CORP["accent_dark"]), marker=dict(size=6),
            ))
        if trajectoire_actuelle_cible is not None:
            fig.add_trace(go.Scatter(
                x=[annee_actuelle_obj, annee_cible],
                y=[valeur_actuelle_obj, trajectoire_actuelle_cible],
                mode="lines+markers", name="Trajectoire au rythme actuel",
                line=dict(width=2.5, color=GAEA_CORP["brown"], dash="dot"),
                marker=dict(size=7, symbol="circle-open", line=dict(width=2)),
            ))
        if valeur_cible is not None and annee_actuelle_obj is not None and rythme_necessaire is not None:
            fig.add_trace(go.Scatter(
                x=[annee_actuelle_obj, annee_cible], y=[valeur_actuelle_obj, valeur_cible],
                mode="lines+markers", name="Trajectoire nécessaire pour l'objectif",
                line=dict(width=2.5, color=GAEA_CORP["accent_rouge"], dash="dash"),
                marker=dict(size=9, symbol="star"),
            ))
        fig = theme_plotly(fig, hauteur=430, titre_x="Année", titre_y="Part des renouvelables (%)")
        st.plotly_chart(fig, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_objectif")
        st.caption(
            "Trait plein = historique réel · pointillé marron = si le rythme actuel se poursuit · "
            "tiret rouge = rythme qu'il faudrait tenir pour atteindre l'objectif choisi."
        )

    a_retenir(f"{symbole} <b>{verdict}</b>. {explication}")

    tableau_objectif = pd.DataFrame({
        "Année": [annee_actuelle_obj, annee_cible],
        "Trajectoire actuelle (%)": [valeur_actuelle_obj, trajectoire_actuelle_cible],
        "Trajectoire nécessaire (%)": [valeur_actuelle_obj, valeur_cible],
    })
    bouton_telechargement_csv(
        tableau_objectif.set_index("Année"), f"objectif_{pays_objectif}.csv"
    )

with onglet5:
    st.subheader("Émissions de CO2 et de gaz à effet de serre")
    objectif("Comparer l'empreinte carbone des pays, son évolution dans le temps et les énergies fossiles "
             "qui la produisent.")

    # Indicateur au choix : (colonne, libellé court, unité, titre d'axe)
    INDICATEURS_EMISSIONS = {
        "CO2 par habitant": ("co2_par_habitant", "CO2 par habitant", "t", "CO2 par habitant (t)"),
        "GES par habitant": ("ges_par_habitant", "GES par habitant", "t éq. CO2", "GES par habitant (t éq. CO2)"),
        "CO2 total": ("emissions_co2", "émissions totales de CO2", "Mt", "Émissions de CO2 (Mt)"),
    }
    choix_emissions = st.segmented_control(
        "Indicateur", options=list(INDICATEURS_EMISSIONS), default="CO2 par habitant",
        key="indicateur_emissions", label_visibility="collapsed",
    ) or "CO2 par habitant"
    col_em, _, unite_em, titre_em = INDICATEURS_EMISSIONS[choix_emissions]

    if col_em not in df_filtre.columns:
        st.warning(f"Colonne {col_em} absente de la base.")
    else:
        pivot_em = df_filtre.pivot_table(index="annee", columns="pays_fr", values=col_em)
        decimales_em = 0 if unite_em == "Mt" else 1

        # Cartes : pays le plus et le moins émetteur la dernière année, et
        # évolution de la sélection depuis la première année de la période
        _retenir_em = None
        dernieres_em = pivot_em.loc[derniere_annee].dropna() if derniere_annee in pivot_em.index else pd.Series(dtype=float)
        if not dernieres_em.empty:
            pays_haut, pays_bas = dernieres_em.idxmax(), dernieres_em.idxmin()
            premieres_em = pivot_em.apply(lambda c: c.dropna().iloc[0] if c.notna().any() else np.nan)
            communs = dernieres_em.index.intersection(premieres_em.dropna().index)
            evolution = ((dernieres_em[communs].sum() / premieres_em[communs].sum() - 1) * 100
                         if len(communs) and premieres_em[communs].sum() else None)
            cartes_kpi([
                {"icone": "🏭", "valeur": f"{fmt_fr(dernieres_em[pays_haut], decimales=decimales_em)} {unite_em}",
                 "label": f"Plus émetteur · {pays_haut}", "couleur": GAEA_CORP["accent_rouge"]},
                {"icone": "🌿", "valeur": f"{fmt_fr(dernieres_em[pays_bas], decimales=decimales_em)} {unite_em}",
                 "label": f"Moins émetteur · {pays_bas}", "couleur": GAEA_CORP["accent_dark"]},
                {"icone": "📉" if (evolution or 0) < 0 else "📈",
                 "valeur": f"{evolution:+.0f} %".replace("-", "−") if evolution is not None else "n/d",
                 "label": f"Évolution de la sélection depuis {int(pivot_em.index.min())}",
                 "couleur": GAEA_CORP["brown"]},
            ])
            _retenir_em = (
                f"{choix_emissions} en {derniere_annee} : le plus haut, <b>{pays_haut}</b> "
                f"(<b>{fmt_fr(dernieres_em[pays_haut], decimales=decimales_em)} {unite_em}</b>), est "
                f"<b>{dernieres_em[pays_haut] / dernieres_em[pays_bas]:.1f} fois</b> au-dessus du plus bas, "
                f"<b>{pays_bas}</b> ({fmt_fr(dernieres_em[pays_bas], decimales=decimales_em)} {unite_em})."
                if dernieres_em[pays_bas] > 0 else None
            )
            if evolution is not None and _retenir_em:
                _retenir_em += (f" Depuis {int(pivot_em.index.min())}, la sélection a "
                                f"{'réduit' if evolution < 0 else 'augmenté'} ses émissions de "
                                f"<b>{abs(evolution):.0f} %</b>.")

        with st.container(border=True):
            fig = graphique_lignes(pivot_em, titre_y=titre_em)
            st.plotly_chart(fig, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_co2_ges")
            legende_em = f"{titre_em}, une série par pays."
            if col_em == "ges_par_habitant":
                legende_em += (" GES = tous les gaz (CO2, méthane, protoxyde d'azote…) convertis en équivalent "
                               "CO2, usage des terres compris (Our World in Data).")
            st.caption(legende_em)
        if _retenir_em:
            a_retenir(_retenir_em)
        bouton_telechargement_csv(pivot_em, f"{col_em}.csv")

    # ---- D'où vient le CO2 ? Répartition par combustible, dernière année ----
    st.markdown('<div class="gaea-section-label" style="margin-top:22px;">D\'où vient le CO2 ?</div>',
                unsafe_allow_html=True)
    objectif("Voir quelle énergie fossile pèse le plus dans les émissions de CO2 de chaque pays.")
    colonnes_sources = {"co2_charbon": "Charbon", "co2_petrole": "Pétrole", "co2_gaz": "Gaz"}
    _sources_co2 = df_filtre[df_filtre["annee"] == derniere_annee].dropna(subset=["emissions_co2"]).copy()
    _sources_co2 = _sources_co2[_sources_co2["emissions_co2"] > 0]
    if _sources_co2.empty or not all(c in _sources_co2.columns for c in colonnes_sources):
        st.caption("Pas de répartition par combustible disponible pour cette sélection.")
    else:
        # Un combustible absent de la base pour un pays est compté à zéro ;
        # « Autres » regroupe le reste (ciment, torchage…), pour que le total fasse 100 %.
        for c in colonnes_sources:
            _sources_co2[c] = _sources_co2[c].fillna(0)
        _sources_co2["co2_autres"] = (_sources_co2["emissions_co2"]
                                      - _sources_co2[list(colonnes_sources)].sum(axis=1)).clip(lower=0)
        parts = _sources_co2.set_index("pays_fr")[list(colonnes_sources) + ["co2_autres"]]
        parts = parts.div(parts.sum(axis=1), axis=0) * 100
        parts = parts.sort_values("co2_charbon")
        couleurs_sources = {"co2_charbon": "#2e2b26", "co2_petrole": GAEA_CORP["brown"],
                            "co2_gaz": "#d4a017", "co2_autres": "#c9c2b4"}
        noms_sources = dict(colonnes_sources, co2_autres="Autres (ciment, torchage…)")
        with st.container(border=True):
            fig_sources = go.Figure()
            for c in parts.columns:
                fig_sources.add_trace(go.Bar(
                    y=parts.index, x=parts[c], orientation="h", name=noms_sources[c],
                    marker=dict(color=couleurs_sources[c], line=dict(width=1.5, color="#fff")),
                    text=[f"{v:.0f} %" if v >= 7 else "" for v in parts[c]], textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(color="#fff" if c in ("co2_charbon", "co2_petrole") else "#2e2b26", size=12),
                    hovertemplate="%{y} · " + noms_sources[c] + " : %{x:.1f} %<extra></extra>",
                ))
            fig_sources = theme_plotly(fig_sources, hauteur=max(280, 110 + 52 * len(parts)),
                                       titre_x="Part des émissions de CO2 (%)", titre_y="")
            fig_sources.update_layout(barmode="stack", bargap=0.28, legend=dict(traceorder="normal"))
            fig_sources.update_xaxes(range=[0, 100], ticksuffix=" %")
            st.plotly_chart(fig_sources, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_co2_sources")
            st.caption(f"Émissions de CO2 {derniere_annee} par combustible, en % du total de chaque pays. "
                       "Pays classés du plus dépendant du charbon (en haut) au moins dépendant.")
        _plus_charbon = parts["co2_charbon"].idxmax()
        _principale = parts.mean().drop("co2_autres").idxmax()
        a_retenir(
            f"Pour la sélection, la première source de CO2 est en moyenne <b>le {noms_sources[_principale].lower()}</b>. "
            f"Pays le plus dépendant du charbon : <b>{_plus_charbon}</b> "
            f"(<b>{parts.loc[_plus_charbon, 'co2_charbon']:.0f} %</b> de son CO2)."
        )

with onglet6:
    st.subheader(f"Comparaison des pays ({derniere_annee})")
    objectif("Comparer les pays sur les indicateurs clés la même année, et ranger chacun dans un profil type.")
    _derniere_comparaison = df_filtre[df_filtre["annee"] == derniere_annee].copy()
    colonnes_comparaison = [
        c for c in ["part_renouvelables_dans_electricite", "intensite_carbone_electricite", "co2_par_habitant"]
        if c in _derniere_comparaison.columns
    ]
    if _derniere_comparaison.empty:
        st.warning("Aucune donnée pour cette année.")
    else:
        _renouv_2000 = df[df["annee"] == 2000].set_index("pays")["part_renouvelables_dans_electricite"]
        _derniere_comparaison["hausse_renouvelables_depuis_2000"] = (
            _derniere_comparaison["part_renouvelables_dans_electricite"]
            - _derniere_comparaison["pays"].map(_renouv_2000)
        )
        _derniere_comparaison["Profil"] = _derniere_comparaison.apply(classer_pays_typologie, axis=1)
        tableau_comparaison = (
            _derniere_comparaison.set_index("pays_fr")[["Profil"] + colonnes_comparaison]
            .rename(columns={
                "part_renouvelables_dans_electricite": "Renouvelables (%)",
                "intensite_carbone_electricite": "Intensité carbone (gCO2/kWh)",
                "co2_par_habitant": "CO2/habitant (t)",
            })
            .sort_values("Renouvelables (%)", ascending=False)
        )
        tableau_comparaison.index.name = "Pays"
        colonnes_chiffres = [c for c in tableau_comparaison.columns if c != "Profil"]

        # Fiches pays : rang, profil coloré et trois jauges, chacune avec un repère
        # sur la moyenne de tous les pays la même année.
        _tous_pays_annee = df[df["annee"] == derniere_annee]
        _jauges = [
            ("Renouvelables (%)", "part_renouvelables_dans_electricite", "Renouvelables", " %", 100, True),
            ("Intensité carbone (gCO2/kWh)", "intensite_carbone_electricite", "Intensité carbone", " g/kWh", 900, False),
            ("CO2/habitant (t)", "co2_par_habitant", "CO2 par habitant", " t", 20, False),
        ]
        _couleurs_profil = {
            "Très renouvelable et peu carboné": GAEA_CORP["accent_dark"],
            "Mix fossile et carboné": GAEA_CORP["accent_rouge"],
            "Transition rapide": GAEA_CORP["accent"],
            "Grand émetteur avec forte production renouvelable": "#b8860b",
            "Profil intermédiaire": GAEA_CORP["brown"],
        }
        _medailles = {0: "🥇", 1: "🥈", 2: "🥉"}
        _fiches = []
        for rang, (nom, ligne) in enumerate(tableau_comparaison.head(12).iterrows()):
            couleur = _couleurs_profil.get(ligne["Profil"], GAEA_CORP["brown"])
            barres = ""
            for colonne, col_df, libelle, unite, plafond, haut_est_bien in _jauges:
                if colonne not in tableau_comparaison.columns or pd.isna(ligne[colonne]):
                    continue
                valeur = float(ligne[colonne])
                moyenne = _tous_pays_annee[col_df].mean()
                largeur = min(valeur / plafond * 100, 100)
                mieux = (valeur >= moyenne) if haut_est_bien else (valeur <= moyenne)
                barres += (
                    f'<div class="gaea-fiche-jauge"><div class="gaea-fiche-jauge-tete"><span>{libelle}</span>'
                    f'<b>{fmt_fr(valeur, decimales=0 if plafond > 100 else 1)}{unite}</b></div>'
                    f'<div class="gaea-fiche-piste"><div class="gaea-fiche-rempli {"bien" if mieux else "moins"}" '
                    f'style="width:{largeur:.1f}%"></div>'
                    + (f'<div class="gaea-fiche-repere" style="left:{min(moyenne / plafond * 100, 100):.1f}%" '
                       f'title="Moyenne de tous les pays : {fmt_fr(moyenne)}{unite}"></div>' if pd.notna(moyenne) else "")
                    + '</div></div>'
                )
            _fiches.append(
                f'<div class="gaea-fiche" style="--profil:{couleur}">'
                f'<div class="gaea-fiche-tete"><span class="gaea-fiche-rang">{_medailles.get(rang, f"#{rang + 1}")}</span>'
                f'<div class="gaea-fiche-nom">{nom}</div></div>'
                f'<div class="gaea-fiche-profil">{ligne["Profil"]}</div>{barres}</div>'
            )
        st.markdown(f'<div class="gaea-fiches">{"".join(_fiches)}</div>', unsafe_allow_html=True)
        st.caption("Classement par part de renouvelables. Jauge verte = mieux que la moyenne de tous les pays, "
                   "bordeaux = moins bien ; le trait doré marque cette moyenne."
                   + (" Les 12 premiers pays sont affichés, le tableau ci-dessous les détaille tous."
                      if len(tableau_comparaison) > 12 else ""))

        with st.expander("Tableau détaillé", icon=":material/table_chart:", expanded=len(tableau_comparaison) > 12):
            st.dataframe(
                tableau_comparaison.style.format(lambda v: fmt_fr(v), subset=colonnes_chiffres).bar(
                    subset=["Renouvelables (%)"], color=GAEA_CORP["accent"], vmin=0, vmax=100
                ),
                width="stretch",
            )
            st.caption("Profil : grille de lecture du tableau de bord natif (seuils sur les renouvelables, "
                       "leur hausse depuis 2000, l'intensité carbone et les émissions).")

        _phrases_comparaison = []
        intensites = tableau_comparaison["Intensité carbone (gCO2/kWh)"].dropna() \
            if "Intensité carbone (gCO2/kWh)" in tableau_comparaison.columns else pd.Series(dtype=float)
        if len(intensites) >= 2:
            meilleur, pire = intensites.idxmin(), intensites.idxmax()
            _phrases_comparaison.append(
                f"Électricité la moins carbonée : <b>{meilleur}</b> (<b>{intensites[meilleur]:.0f} gCO2/kWh</b>) ; "
                f"la plus carbonée : <b>{pire}</b> ({intensites[pire]:.0f} gCO2/kWh)."
            )
        comptage = tableau_comparaison["Profil"].value_counts()
        if not comptage.empty:
            _phrases_comparaison.append(
                f"Profil le plus fréquent : <b>« {comptage.idxmax()} »</b> ({comptage.max()} pays sur "
                f"{len(tableau_comparaison)})."
            )
        if _phrases_comparaison:
            a_retenir(" ".join(_phrases_comparaison))
        bouton_telechargement_csv(tableau_comparaison, f"comparaison_pays_{derniere_annee}.csv")

with onglet_cluster:
    st.subheader("Cluster socio-économique : richesse et transition énergétique")
    st.markdown(
        "Les pays se regroupent-ils selon leur **richesse** et leur **électricité** ? Trois indicateurs : "
        "PIB par habitant (PPA, Banque mondiale), part des renouvelables et intensité carbone (Our World in Data)."
    )

    if resultat_cluster is None:
        st.warning(
            "Analyse non calculable : le fichier de PIB par habitant n'a pas été trouvé, ou ne contient pas "
            "assez de correspondances avec la base actuelle. Voir `preparer_pib_habitant.py` pour préparer ce "
            "fichier à partir de l'export brut de la Banque mondiale."
        )
    else:
        k_optimal = resultat_cluster["k_optimal"]
        points_cluster = resultat_cluster["points"]
        jeu_cluster = resultat_cluster["jeu"]
        k_min_cluster, k_max_cluster = 2, min(8, len(points_cluster) - 1)

        # 1. ACP d'abord : décrire la structure des données et interpréter les axes,
        # avant de former des groupes (démarche classique d'analyse de données).
        acp_cluster = acp_complete_np(
            points_cluster, ["log_pib", "part_renouvelables_dans_electricite", "intensite_carbone_electricite"]
        )
        st.markdown('<div class="gaea-section-label">1. Analyse en composantes principales (ACP)</div>',
                    unsafe_allow_html=True)
        objectif("Résumer les 3 indicateurs en 2 axes faciles à lire, pour voir ce qui différencie vraiment "
                 "les pays.")
        st.caption(f"3 variables centrées-réduites · {resultat_cluster['nb_pays']} pays · dernière année disponible.")
        col_eboulis, col_cercle = st.columns([1, 1.15])
        with col_eboulis:
            st.markdown("**Éboulis des valeurs propres**")
            with st.container(border=True):
                st.plotly_chart(graphique_eboulis(acp_cluster), width="stretch",
                                config=CONFIG_PLOTLY_EXPORT, key="chart_acp_eboulis")
                st.caption(fr(
                    "Valeurs propres : " + " · ".join(
                        f"Dim {i + 1} = {v:.2f}" for i, v in enumerate(acp_cluster["valeurs_propres"])
                    ) + f". On garde Dim 1 et Dim 2 ({acp_cluster['pourcentages'][:2].sum():.1f} % de la variance)."
                ))
        with col_cercle:
            st.markdown("**Cercle des corrélations**")
            with st.container(border=True):
                st.plotly_chart(graphique_cercle_correlations(acp_cluster), width="stretch",
                                config=CONFIG_PLOTLY_EXPORT, key="chart_acp_cercle")
                st.caption("Flèche proche du cercle = variable bien représentée.")
        a_retenir(texte_interpretation_acp(acp_cluster))

        st.markdown('<div class="gaea-section-label">2. Classification des pays</div>', unsafe_allow_html=True)
        st.markdown("**Choix du nombre de groupes (méthode du coude)**")
        objectif("Choisir combien de groupes former : on s'arrête quand un groupe de plus n'apporte presque "
                 "plus rien.")
        with st.container(border=True):
            fig_coude = graphique_cluster_coude(resultat_cluster)
            st.plotly_chart(fig_coude, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_cluster_coude")
            st.caption(
                f"Point bordeaux = k recommandé ({k_optimal} groupes), calculé automatiquement au coude de la courbe."
            )
        _inerties = resultat_cluster["inerties"]
        _ks = sorted(_inerties)
        if k_optimal in _inerties and k_optimal != _ks[0] and k_optimal != _ks[-1]:
            _baisse_avant = (1 - _inerties[k_optimal] / _inerties[_ks[0]]) * 100
            _baisse_apres = (1 - _inerties[_ks[-1]] / _inerties[k_optimal]) * 100 / (_ks[-1] - k_optimal)
            a_retenir(
                f"Jusqu'à <b>{k_optimal} groupes</b>, l'inertie chute de <b>{_baisse_avant:.0f} %</b> ; "
                f"au-delà, chaque groupe en plus ne la réduit plus que d'environ <b>{_baisse_apres:.0f} %</b>. "
                f"{k_optimal} groupes offrent donc le meilleur compromis entre simplicité et précision."
            )

        # Comparaison automatique coude / silhouette : les deux méthodes répondent à des
        # questions différentes (baisse d'inertie vs séparation nette entre groupes) et
        # peuvent légitimement diverger -- mieux vaut le rendre visible que de le laisser
        # deviner en changeant le curseur soi-même.
        silhouette_par_k = {
            k_test: clustering_pour_k(points_cluster, k_test)[1]
            for k_test in range(k_min_cluster, k_max_cluster + 1)
        }
        k_meilleure_silhouette = max(
            (k for k in silhouette_par_k if silhouette_par_k[k] is not None),
            key=lambda k: silhouette_par_k[k],
            default=None,
        )
        if k_meilleure_silhouette is not None and k_meilleure_silhouette != k_optimal:
            st.markdown(
                f'<div class="gaea-alerte">⚖️ Le coude recommande <b>k={k_optimal}</b>, la silhouette préfère '
                f"<b>k={k_meilleure_silhouette}</b> ({fmt_fr(silhouette_par_k[k_meilleure_silhouette], decimales=3)} "
                f"contre {fmt_fr(silhouette_par_k.get(k_optimal), decimales=3)}) : les pays forment un continuum "
                "plus que des blocs nets. Compare avec le curseur.</div>",
                unsafe_allow_html=True,
            )
        elif k_meilleure_silhouette is not None:
            st.markdown(
                f'<div class="gaea-alerte">✅ Coude et silhouette s\'accordent sur <b>k={k_optimal}</b> '
                f"(silhouette = {fmt_fr(silhouette_par_k[k_optimal], decimales=3)}).</div>",
                unsafe_allow_html=True,
            )

        # Ligne curseur + silhouette + effectif, sur le modèle de la référence R
        # (trois cases côte à côte plutôt qu'un curseur en pleine largeur).
        col_slider, col_silhouette, col_effectif = st.columns([1, 1, 1])
        with col_slider:
            st.markdown("**Nombre de groupes**")
            k_choisi = st.slider(
                "k", min_value=k_min_cluster, max_value=k_max_cluster,
                value=min(max(k_optimal, k_min_cluster), k_max_cluster), step=1,
                key="cluster_k_slider", label_visibility="collapsed",
            )
            st.caption(f"La méthode du coude recommande k={k_optimal}.")

        affectations_k, silhouette_k = clustering_pour_k(points_cluster, k_choisi)

        with col_silhouette:
            if silhouette_k is not None:
                cartes_kpi([
                    {"icone": "🎯", "valeur": fmt_fr(silhouette_k, decimales=3),
                     "label": "Silhouette", "couleur": GAEA_CORP["accent"]},
                ])
        with col_effectif:
            cartes_kpi([
                {"icone": "📊", "valeur": str(resultat_cluster["nb_pays"]),
                 "label": "Pays dans le modèle", "couleur": GAEA_CORP["brown"]},
            ])

        if silhouette_k is not None:
            if silhouette_k >= 0.4:
                qualif_silhouette = "des groupes bien séparés"
            elif silhouette_k >= 0.25:
                qualif_silhouette = "une séparation modérée entre les groupes"
            else:
                qualif_silhouette = "des groupes qui se chevauchent nettement -- à interpréter avec prudence"
            st.caption(f"Silhouette (de -1 à 1, plus c'est haut mieux c'est) : avec k={k_choisi}, {qualif_silhouette}.")

        # Dendrogramme puis projection ACP, l'un sous l'autre en pleine largeur.
        st.markdown("**Dendrogramme CAH**")
        objectif("Vérifier les groupes avec une seconde méthode : si elle retrouve les mêmes pays ensemble, "
                 "les groupes sont solides.")
        with st.container(border=True):
            racine_dendro, _hauteur_max, sous_echantillonne, fusions_dendro = calculer_dendrogramme(points_cluster)
            hauteur_coupe_k = _hauteur_coupe_np(fusions_dendro, k_choisi)
            groupe_par_feuille = _identifier_groupes_dendrogramme(racine_dendro, hauteur_coupe_k)
            fig_dendro = graphique_dendrogramme(
                racine_dendro, sous_echantillonne,
                hauteur_coupe=hauteur_coupe_k, groupe_par_feuille=groupe_par_feuille,
                noms_pays=jeu_cluster["pays"].map(NOMS_FR).fillna(jeu_cluster["pays"]).tolist(),
                groupes_kmeans=list(affectations_k),
            )
            st.plotly_chart(fig_dendro, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_cluster_dendro")
            note_echantillon = (
                f" (échantillon de 80 pays sur {resultat_cluster['nb_pays']})" if sous_echantillonne else ""
            )
            st.caption(
                f"Une feuille = un pays{note_echantillon}. Lettres = groupes de la CAH (coupe à la ligne "
                "pointillée) ; carrés = groupe k-means du pays (survol = nom)."
            )
        _feuilles = []

        def _collecter_feuilles(noeud):
            if noeud["gauche"] is None:
                _feuilles.append(noeud)
                return
            _collecter_feuilles(noeud["gauche"])
            _collecter_feuilles(noeud["droite"])
        _collecter_feuilles(racine_dendro)
        _par_groupe = {}
        for _f in _feuilles:
            _par_groupe.setdefault(groupe_par_feuille.get(_f["x"], 0), []).append(int(affectations_k[_f["indice_pays"]]))
        _accord = sum(max(_l.count(g) for g in set(_l)) for _l in _par_groupe.values()) / len(_feuilles) * 100
        _isoles = [_f for _f in _feuilles if len(_par_groupe[groupe_par_feuille.get(_f["x"], 0)]) == 1]
        _phrase_isole = ""
        if _isoles:
            _pays_isole = jeu_cluster.iloc[_isoles[0]["indice_pays"]]
            _phrase_isole = (
                f" Seul cas à part : <b>{NOMS_FR.get(_pays_isole['pays'], _pays_isole['pays'])}</b>, isolé par "
                f"la CAH ({_pays_isole['part_renouvelables_dans_electricite']:.1f} % de renouvelables, "
                f"{fmt_fr(_pays_isole['intensite_carbone_electricite'], 0)} gCO2/kWh)."
            )
        a_retenir(
            f"Les deux méthodes classent <b>{_accord:.0f} %</b> des pays de l'échantillon de la même façon : "
            f"la structure en groupes est <b>en grande partie robuste</b>, elle ne dépend pas que de l'algorithme "
            f"choisi.{_phrase_isole}"
        )

        st.markdown("**Clusters K-means (projection ACP)**")
        objectif("Situer chaque pays et son groupe sur les deux axes de l'ACP.")
        with st.container(border=True):
            dim1, dim2, variance_acp = acp_projection_np(points_cluster)
            fig_nuage = graphique_cluster_nuage_acp(jeu_cluster, dim1, dim2, variance_acp, affectations_k,
                                                    k_choisi, acp=acp_cluster)
            st.plotly_chart(fig_nuage, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_cluster_nuage")
        _i_extreme = int(np.argmax(np.asarray(dim1)))
        _pays_extreme = NOMS_FR.get(jeu_cluster.iloc[_i_extreme]["pays"], jeu_cluster.iloc[_i_extreme]["pays"])
        a_retenir(
            f"Chaque groupe occupe <b>son propre coin</b> du plan : la richesse (haut/bas) et le type d'électricité "
            f"(gauche/droite) suffisent à décrire les pays. Le point le plus à droite, <b>{_pays_extreme}</b>, "
            f"est le pays au profil électrique le plus carboné de tous."
        )

        st.markdown("**Détail par groupe**")
        objectif("Décrire le profil type de chaque groupe et ses pays les plus représentatifs.")
        d = jeu_cluster.copy()
        d["pays_fr"] = d["pays"].map(NOMS_FR).fillna(d["pays"])
        d["groupe_choisi"] = affectations_k
        # Une carte par groupe : profil déduit de sa position moyenne sur le plan de
        # l'ACP, effectif, indicateurs moyens et exemples (sans défilement horizontal).
        cartes_groupes = []
        for g in range(k_choisi):
            masque = d["groupe_choisi"] == g
            membres = d[masque]
            if membres.empty:
                continue
            centre_x = float(np.mean(np.asarray(dim1)[masque.to_numpy()]))
            centre_y = float(np.mean(np.asarray(dim2)[masque.to_numpy()]))
            profil = (f"{_cote_axe(acp_cluster, 1, 1 if centre_y >= 0 else -1).capitalize()} · "
                      f"{_cote_axe(acp_cluster, 0, 1 if centre_x >= 0 else -1)}")
            exemples = ", ".join(membres.sort_values("pib_par_habitant", ascending=False)["pays_fr"].head(6))
            couleur = COULEURS_CLUSTER[g % len(COULEURS_CLUSTER)]
            cartes_groupes.append(
                f'<div class="gaea-groupe" style="--couleur-groupe:{couleur};">'
                f'<div class="gaea-groupe-tete"><span class="gaea-groupe-pastille"></span>Groupe {g + 1}'
                f'<span class="gaea-groupe-effectif">{len(membres)} pays</span></div>'
                f'<div class="gaea-groupe-profil">{profil}</div>'
                f'<div class="gaea-groupe-stats">'
                f'<div><b>{fmt_fr(membres["pib_par_habitant"].mean(), decimales=0)} $</b><span>PIB/habitant</span></div>'
                f'<div><b>{fmt_fr(membres["part_renouvelables_dans_electricite"].mean(), decimales=1)} %</b>'
                f'<span>renouvelables</span></div>'
                f'<div><b>{fmt_fr(membres["intensite_carbone_electricite"].mean(), decimales=0)}</b>'
                f'<span>gCO2/kWh</span></div>'
                f'</div>'
                f'<div class="gaea-groupe-exemples"><span>Les plus riches :</span> {exemples}</div>'
                f'</div>'
            )
        st.markdown(f'<div class="gaea-groupes">{"".join(cartes_groupes)}</div>', unsafe_allow_html=True)
        _stats_groupes = d.groupby("groupe_choisi")[["pib_par_habitant", "intensite_carbone_electricite"]].mean()
        if len(_stats_groupes) >= 2:
            _deux_riches = _stats_groupes.sort_values("pib_par_habitant", ascending=False).head(2)
            _propre, _sale = (_deux_riches.sort_values("intensite_carbone_electricite").index[0],
                              _deux_riches.sort_values("intensite_carbone_electricite").index[1])
            _ratio = _stats_groupes.loc[_sale, "intensite_carbone_electricite"] / _stats_groupes.loc[_propre, "intensite_carbone_electricite"]
            a_retenir(
                f"<b>La richesse ne garantit pas une électricité propre</b> : les deux groupes les plus riches "
                f"(Groupe {_propre + 1} et Groupe {_sale + 1}) ont des PIB proches, mais l'électricité du "
                f"Groupe {_sale + 1} émet <b>{_ratio:.1f} fois plus</b> de CO2 par kWh. "
                "<i>Structure statistique, pas un lien de cause à effet.</i>"
            )


        bouton_telechargement_csv(
            d[["pays_fr", "pib_par_habitant", "part_renouvelables_dans_electricite",
               "intensite_carbone_electricite", "groupe_choisi"]].set_index("pays_fr"),
            "cluster_socio_energetique.csv",
        )

def _rgba(couleur_hex, alpha):
    """Couleur « #rrggbb » en rgba() transparent, pour les remplissages Plotly."""
    r, g, b = (int(couleur_hex.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


with onglet8:
    # Comme dans le tableau de bord natif, les tests 2 et 3 portent sur tous les
    # pays de la zone, et non sur les seuls pays cochés dans la barre latérale.
    _toute_la_base = vue in ("7 pays de comparaison du projet", "Monde")
    df_zone = df if _toute_la_base else df[df["pays"].map(continent_de) == vue]
    df_zone = df_zone.assign(pays_fr=df_zone["pays"].map(NOMS_FR).fillna(df_zone["pays"]))
    _nom_zone = "la base" if _toute_la_base else f"la zone « {vue} »"
    st.caption(f"Même numérotation que le tableau de bord natif : le test 1 (corrélation) est dans l'onglet "
               f"Corrélation. Les tests 2 et 3 portent sur tous les pays de {_nom_zone}, quelle que soit "
               "la sélection de pays.")

    st.subheader("Test 2 — Test t de Welch : intensité carbone selon le niveau de renouvelables")
    objectif("Vérifier que les pays à au moins 50 % de renouvelables ont bien une électricité moins carbonée.")
    # Une seule observation par pays (sa dernière année dans la période) : les
    # pays-années d'un même pays ne sont pas indépendants.
    donnees_test = (
        df_zone[df_zone["annee"].between(*periode)].sort_values("annee").groupby("pays").tail(1)
        .dropna(subset=["part_renouvelables_dans_electricite", "intensite_carbone_electricite"])
    )
    groupe1 = donnees_test.loc[donnees_test["part_renouvelables_dans_electricite"] >= 50, "intensite_carbone_electricite"].to_numpy()
    groupe2 = donnees_test.loc[donnees_test["part_renouvelables_dans_electricite"] < 50, "intensite_carbone_electricite"].to_numpy()

    st.caption(f"Groupe 1 : ≥ 50 % de renouvelables (n = {len(groupe1)}) · Groupe 2 : < 50 % (n = {len(groupe2)}).")

    t, ddl, p = welch_ttest_numpy(groupe1, groupe2)
    if t is None:
        st.warning("Pas assez de données dans un des deux groupes pour ce test, sur cette zone et cette période.")
    else:
        cartes_kpi([
            {"icone": "🟢", "valeur": fmt_fr(np.mean(groupe1), decimales=1), "label": "Moyenne Groupe 1",
             "couleur": GAEA_CORP["accent_dark"]},
            {"icone": "🔵", "valeur": fmt_fr(np.mean(groupe2), decimales=1), "label": "Moyenne Groupe 2",
             "couleur": GAEA_CORP["brown"]},
            {"icone": "📐", "valeur": fmt_fr(t, decimales=2), "label": "Statistique t (Welch)",
             "couleur": GAEA_CORP["accent_rouge"]},
            {"icone": "🎯", "valeur": "< 0,001" if p < 0.001 else fmt_fr(p, decimales=3), "label": "p-valeur unilatérale",
             "couleur": "#3d346b"},
        ])

        # Distribution des deux groupes : violon + boîte + points (un point = un pays),
        # et une flèche entre les deux moyennes pour montrer l'écart testé.
        with st.container(border=True):
            fig_welch = go.Figure()
            _groupes_welch = [
                ("Groupe 1 · ≥ 50 %", donnees_test["part_renouvelables_dans_electricite"] >= 50, GAEA_CORP["accent_dark"]),
                ("Groupe 2 · < 50 %", donnees_test["part_renouvelables_dans_electricite"] < 50, GAEA_CORP["brown"]),
            ]
            for nom_groupe, masque, couleur in _groupes_welch:
                sous = donnees_test[masque]
                fig_welch.add_trace(go.Violin(
                    x=[nom_groupe] * len(sous), y=sous["intensite_carbone_electricite"], name=nom_groupe,
                    line=dict(color=couleur, width=2), fillcolor=_rgba(couleur, 0.28), width=0.75,
                    box=dict(visible=True, width=0.18, fillcolor="rgba(255,255,255,0.9)", line=dict(color=couleur, width=2)),
                    meanline=dict(visible=True, color=GAEA_CORP["accent_rouge"], width=3),
                    points="all" if len(sous) <= 400 else "outliers", pointpos=0, jitter=0.6,
                    marker=dict(size=7, opacity=0.75, color=couleur, line=dict(width=1, color="#fff")),
                    customdata=np.stack([sous["pays_fr"], sous["annee"].astype(int),
                                         sous["part_renouvelables_dans_electricite"]], axis=-1),
                    hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                                  "%{y:.0f} gCO2/kWh · %{customdata[2]:.1f} % renouvelables<extra></extra>",
                ))
            _m1, _m2 = float(np.mean(groupe1)), float(np.mean(groupe2))
            for nom_groupe, moyenne, couleur in ((_groupes_welch[0][0], _m1, _groupes_welch[0][2]),
                                                 (_groupes_welch[1][0], _m2, _groupes_welch[1][2])):
                fig_welch.add_annotation(
                    x=nom_groupe, y=moyenne, text=f"<b>moyenne {fmt_fr(moyenne, decimales=0)}</b>",
                    showarrow=False, xshift=118, font=dict(color=couleur, size=13),
                    bgcolor="rgba(255,255,255,0.85)", bordercolor=couleur, borderwidth=1, borderpad=4,
                )
            fig_welch.add_annotation(
                x=_groupes_welch[0][0], y=_m1, ax=_groupes_welch[1][0], ay=_m2,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowsize=1.4, arrowwidth=2.5, arrowcolor=GAEA_CORP["accent_rouge"],
                text="", standoff=6, startstandoff=6,
            )
            fig_welch.add_annotation(
                x=0.5, y=(_m1 + _m2) / 2, xref="paper", yref="y", showarrow=False,
                text=f"<b>{fmt_fr(_m1 - _m2, decimales=0)} gCO2/kWh</b>",
                font=dict(color="#fff", size=14), bgcolor=GAEA_CORP["accent_rouge"], borderpad=6,
            )
            fig_welch = theme_plotly(fig_welch, hauteur=480, titre_x="", titre_y="Intensité carbone (gCO2/kWh)")
            fig_welch.update_layout(showlegend=False)
            st.plotly_chart(fig_welch, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_test_welch")
            st.caption("Un point = un pays à sa dernière année connue. Violon = répartition des valeurs, boîte = quartiles, "
                       "trait = moyenne. La flèche relie les deux moyennes comparées par le test.")

        alpha = 0.05
        difference = np.mean(groupe1) - np.mean(groupe2)
        if p < alpha and difference < 0:
            a_retenir(
                f"<b>H0 rejetée</b> (p &lt; 0,05) : au-delà de 50 % de renouvelables, l'électricité émet en moyenne "
                f"<b>{abs(difference):.0f} gCO2/kWh de moins</b> ({np.mean(groupe1):.0f} contre {np.mean(groupe2):.0f})."
            )
        else:
            a_retenir(
                f"<b>H0 non rejetée</b> (p = {p:.3f}) : sur cette zone, on ne peut pas conclure que le groupe "
                "le plus renouvelable a une électricité moins carbonée."
            )
        st.caption(fr(f"Degrés de liberté approximés (Welch-Satterthwaite) ≈ {ddl:.1f}"))
        bouton_telechargement_csv(
            donnees_test[["pays_fr", "annee", "part_renouvelables_dans_electricite", "intensite_carbone_electricite"]],
            "test2_welch_donnees.csv",
        )

    st.divider()

    st.subheader("Test 3 — Test t apparié : évolution de la part des renouvelables")
    objectif("Vérifier, pour les mêmes pays, que la part des renouvelables a réellement augmenté entre deux "
             "dates (H0 : aucune évolution).")

    periode_perso = st.checkbox(
        "Utiliser une période personnalisée (curseur de la barre latérale) plutôt que 2000-2024",
        value=False,
        key="periode_perso_test2",
    )

    if periode_perso:
        annee_debut, annee_fin = periode
    else:
        annee_debut, annee_fin = 2000, 2024

    # ---- Calcul pur, sans aucun affichage : on prépare toutes les valeurs
    # avant de dessiner quoi que ce soit, pour que la mise en page reste
    # toujours identique d'un calcul à l'autre (évite les soucis d'affichage
    # de Streamlit quand la structure de la page change trop souvent). ----
    message_erreur = None
    t2 = ddl2 = p2 = moy_diff = moy_debut_val = moy_fin_val = None
    n_pays_communs = 0

    if periode_perso and annee_debut == annee_fin:
        message_erreur = "Choisis une période de plus d'un an dans la barre latérale pour ce test."
    else:
        tab_debut = df_zone[df_zone["annee"] == annee_debut].set_index("pays")["part_renouvelables_dans_electricite"].dropna()
        tab_fin = df_zone[df_zone["annee"] == annee_fin].set_index("pays")["part_renouvelables_dans_electricite"].dropna()
        pays_communs = tab_debut.index.intersection(tab_fin.index)
        n_pays_communs = len(pays_communs)

        if n_pays_communs < 2:
            message_erreur = (
                f"Il faut au moins 2 pays avec une donnée à la fois pour {annee_debut} et {annee_fin} "
                "sur cette zone."
            )
        else:
            valeurs_debut = tab_debut.loc[pays_communs].to_numpy()
            valeurs_fin = tab_fin.loc[pays_communs].to_numpy()
            t2, ddl2, p2 = test_apparie_numpy(valeurs_debut, valeurs_fin)
            if t2 is None:
                message_erreur = "Test non calculable sur cette zone (variance nulle ou données insuffisantes)."
            else:
                moy_diff = np.mean(valeurs_fin) - np.mean(valeurs_debut)
                moy_debut_val = np.mean(valeurs_debut)
                moy_fin_val = np.mean(valeurs_fin)

    # ---- Affichage : structure toujours identique, seul le contenu change ----
    st.write(f"Période testée : **{annee_debut} → {annee_fin}**")
    st.write(f"Pays comparés (mêmes pays aux deux dates) : n = {n_pays_communs}")

    cartes_kpi([
        {"icone": "🗓️", "valeur": fmt_fr(moy_debut_val, decimales=2, suffixe=" %") if moy_debut_val is not None else "n/d",
         "label": f"Moyenne {annee_debut}", "couleur": GAEA_CORP["brown"]},
        {"icone": "🗓️", "valeur": fmt_fr(moy_fin_val, decimales=2, suffixe=" %") if moy_fin_val is not None else "n/d",
         "label": f"Moyenne {annee_fin}", "couleur": GAEA_CORP["accent_dark"]},
        {"icone": "📐", "valeur": fmt_fr(t2, decimales=3) if t2 is not None else "n/d", "label": "Statistique t (apparié)",
         "couleur": GAEA_CORP["accent_rouge"]},
        {"icone": "🎯", "valeur": ("< 0,001" if p2 < 0.001 else fmt_fr(p2, decimales=3)) if p2 is not None else "n/d",
         "label": "p-valeur unilatérale", "couleur": "#3d346b"},
    ])

    # Graphique « haltères » : pour chaque pays, un segment de la valeur de début
    # (marron) à celle de fin (vert), trié par gain ; les deux traits verticaux
    # marquent les moyennes comparées par le test. Le test porte sur toute la zone,
    # mais le graphique se limite aux pays cochés pour rester lisible.
    with st.container(border=True):
        if message_erreur:
            st.caption("Graphique indisponible pour cette sélection.")
        else:
            _apparie = pd.DataFrame({"debut": tab_debut.loc[pays_communs], "fin": tab_fin.loc[pays_communs]})
            _apparie["gain"] = _apparie["fin"] - _apparie["debut"]
            _affiches = _apparie[_apparie.index.isin(pays_selectionnes)]
            _apparie = (_affiches if not _affiches.empty else _apparie.nlargest(10, "gain")).sort_values("gain")
            _noms = [NOMS_FR.get(p, p) for p in _apparie.index]
            fig_apparie = go.Figure()
            for nom, ligne in zip(_noms, _apparie.itertuples()):
                fig_apparie.add_trace(go.Scatter(
                    x=[ligne.debut, ligne.fin], y=[nom, nom], mode="lines", showlegend=False, hoverinfo="skip",
                    line=dict(width=7, color=GAEA_CORP["accent"] if ligne.gain >= 0 else GAEA_CORP["accent_rouge"]),
                    opacity=0.35,
                ))
            fig_apparie.add_trace(go.Scatter(
                x=_apparie["debut"], y=_noms, mode="markers", name=str(annee_debut),
                marker=dict(size=14, color=GAEA_CORP["brown"], line=dict(width=2, color="#fff")),
                hovertemplate="%{y} : %{x:.1f} % en " + str(annee_debut) + "<extra></extra>",
            ))
            fig_apparie.add_trace(go.Scatter(
                x=_apparie["fin"], y=_noms, mode="markers", name=str(annee_fin),
                marker=dict(size=16, color=GAEA_CORP["accent_dark"], line=dict(width=2, color="#fff")),
                hovertemplate="%{y} : %{x:.1f} % en " + str(annee_fin) + "<extra></extra>",
            ))
            # Étiquette de gain placée après le point le plus à droite, pour ne jamais être masquée
            fig_apparie.add_trace(go.Scatter(
                x=_apparie[["debut", "fin"]].max(axis=1) + 1.5, y=_noms, mode="text", showlegend=False,
                text=[f"<b>{g:+.1f} pts</b>".replace(".", ",") for g in _apparie["gain"]], textposition="middle right",
                textfont=dict(size=12, color=[GAEA_CORP["accent_dark"] if g >= 0 else GAEA_CORP["accent_rouge"]
                                              for g in _apparie["gain"]]),
                hoverinfo="skip",
            ))
            # Étiquettes au-dessus de la zone du graphique, pour ne pas toucher le premier
            # pays : la plus petite moyenne à gauche de son trait, l'autre à droite, car
            # les deux moyennes sont proches et leurs textes se chevauchaient.
            _cote_debut, _cote_fin = (("right", "left") if moy_debut_val <= moy_fin_val else ("left", "right"))
            for moyenne, couleur, etiquette, cote in (
                (moy_debut_val, GAEA_CORP["brown"], f"moyenne {annee_debut}", _cote_debut),
                (moy_fin_val, GAEA_CORP["accent_dark"], f"moyenne {annee_fin}", _cote_fin),
            ):
                fig_apparie.add_vline(x=moyenne, line_dash="dash", line_width=2, line_color=couleur)
                # Le trait monte jusqu'à l'étiquette : elle vaut pour tous les pays, pas pour le premier.
                fig_apparie.add_shape(
                    type="line", x0=moyenne, x1=moyenne, xref="x", yref="paper", ysizemode="pixel", yanchor=1,
                    y0=0, y1=16, line=dict(color=couleur, width=2, dash="dash"),
                )
                fig_apparie.add_annotation(
                    x=moyenne, y=1, xref="x", yref="paper", xanchor=cote, yanchor="bottom", yshift=16, showarrow=False,
                    text=f"{etiquette} ({n_pays_communs} pays) : {fmt_fr(moyenne, decimales=1)} %",
                    font=dict(color=couleur, size=12),
                )
            fig_apparie = theme_plotly(fig_apparie, hauteur=max(345, 115 + 46 * len(_noms)),
                                       titre_x="Part des renouvelables (%)", titre_y="")
            fig_apparie.update_xaxes(range=[0, 112])
            # Légende tout en haut de la figure, et une bande libre dessous pour les étiquettes.
            fig_apparie.update_layout(margin=dict(t=95), legend=dict(yref="container", y=0.99, yanchor="top"))
            st.plotly_chart(fig_apparie, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_test_apparie")
            st.caption(f"Chaque ligne relie la valeur d'un pays en {annee_debut} (marron) à celle de {annee_fin} "
                       "(vert). Le test regarde si ces écarts sont, en moyenne, nettement au-dessus de zéro. "
                       f"Le test porte sur les {n_pays_communs} pays ; le graphique montre les pays sélectionnés "
                       "(à défaut, les 10 plus fortes hausses).")

    if message_erreur:
        st.warning(message_erreur)
    elif p2 < 0.05 and moy_diff > 0:
        a_retenir(
            f"<b>H0 rejetée</b> (p &lt; 0,05) : entre {annee_debut} et {annee_fin}, la part des renouvelables a "
            f"<b>réellement augmenté</b>, de <b>{moy_diff:+.1f} points</b> en moyenne pour ces {n_pays_communs} pays."
        )
    else:
        a_retenir(
            f"<b>H0 non rejetée</b> (p = {p2:.3f}) : pas de hausse significative entre {annee_debut} et "
            f"{annee_fin} sur cette zone."
        )

    if ddl2 is not None:
        st.caption(f"Degrés de liberté = {ddl2}")

    if not message_erreur and n_pays_communs > 0:
        tableau_test2 = pd.DataFrame({
            f"Valeur {annee_debut} (%)": tab_debut.loc[pays_communs],
            f"Valeur {annee_fin} (%)": tab_fin.loc[pays_communs],
        })
        tableau_test2.index.name = "Pays"
        bouton_telechargement_csv(tableau_test2, f"test3_apparie_{annee_debut}_{annee_fin}.csv")


with onglet9:
    st.subheader("Carte des indicateurs par pays")
    objectif("Voir d'un coup d'œil où en est chaque pays du monde, et rejouer l'évolution année par année (▶).")

    indicateurs_carte = {
        "Part des renouvelables dans l'électricité (%)": "part_renouvelables_dans_electricite",
        "Intensité carbone de l'électricité (gCO2/kWh)": "intensite_carbone_electricite",
        "Émissions de CO2 par habitant (t)": "co2_par_habitant",
        "Émissions de GES par habitant (t)": "ges_par_habitant",
    }
    col_carte1, col_carte2 = st.columns([2, 1])
    with col_carte1:
        libelle_indicateur = st.selectbox(
            "Indicateur", options=list(indicateurs_carte.keys()), key="carte_indicateur"
        )
    with col_carte2:
        st.write("")  # aligne verticalement avec le selectbox de la colonne de gauche

    col_indicateur = indicateurs_carte[libelle_indicateur]

    # ---- Carte animée : années de la période choisie dans la barre latérale
    # (cohérent avec le reste de l'application), curseur + bouton play
    # générés automatiquement par Plotly -- dans l'esprit du Grapher
    # d'Our World in Data. Seule la sélection de PAYS reste volontairement
    # ignorée (voir plus bas), pour garder une vue mondiale complète. ----
    donnees_carte_anim = preparer_donnees_carte_animee(df, col_indicateur)
    donnees_carte_anim = donnees_carte_anim[donnees_carte_anim["annee"].between(periode[0], periode[1])]

    if donnees_carte_anim.empty:
        st.warning("Aucune donnée disponible pour cet indicateur sur la période choisie.")
    else:
        annee_min_carte = int(donnees_carte_anim["annee"].min())
        annee_max_carte = int(donnees_carte_anim["annee"].max())
        donnees_carte_anim = donnees_carte_anim.copy()
        donnees_carte_anim["pays_fr"] = donnees_carte_anim["pays"].map(NOMS_FR).fillna(donnees_carte_anim["pays"])
        with st.container(border=True):
            # Bornes de couleur fixées sur l'ensemble de la période (2e-98e
            # centile, pour ne pas laisser un pays extrême écraser l'échelle)
            # afin que la palette reste cohérente d'une année à l'autre.
            vmin = donnees_carte_anim[col_indicateur].quantile(0.02)
            vmax = donnees_carte_anim[col_indicateur].quantile(0.98)

            fig = px.choropleth(
                donnees_carte_anim, locations="code_iso", color=col_indicateur,
                hover_name="pays_fr", animation_frame="annee",
                color_continuous_scale=["#f5f0e6", "#c9d4a8", "#8f9779", "#6b8e23", "#4d6519"],
                range_color=(vmin, vmax),
                labels={col_indicateur: libelle_indicateur, "annee": "Année"},
            )
            fig.update_layout(
                template="plotly_white", height=500,
                margin=dict(l=0, r=0, t=10, b=0),
                font=dict(family="Inter, 'Segoe UI', sans-serif", size=13, color=GAEA_CORP["text"]),
                paper_bgcolor="rgba(0,0,0,0)",
                # Projection Equal Earth (proportions réelles des continents), comme le
                # tableau de bord natif ; l'Antarctique est rogné pour gagner de la place.
                geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=False,
                         projection_type="equal earth", lataxis_range=[-58, 85]),
            )
            # La carte s'ouvre sur la dernière année (celle commentée dans
            # « À retenir ») ; le bouton lecture rejoue ensuite depuis le début.
            if fig.frames:
                fig.update(data=fig.frames[-1].data)
                fig.layout.sliders[0].active = len(fig.frames) - 1
                fig.layout.sliders[0].currentvalue.prefix = "Année : "
            # Lecture un peu plus lente que le défaut Plotly (trop rapide
            # pour suivre visuellement plusieurs décennies de données d'un
            # coup d'œil). Protégé par try/except : la structure interne du
            # bouton play peut varier selon la version de Plotly installée,
            # et ce réglage n'est qu'un confort visuel, pas une nécessité.
            try:
                fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 600
                fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 300
            except (IndexError, KeyError, TypeError):
                pass
            st.plotly_chart(fig, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_carte_choropleth")

        _carte_fin = donnees_carte_anim[donnees_carte_anim["annee"] == annee_max_carte].dropna(subset=[col_indicateur])
        _unite = " " + libelle_indicateur.rsplit("(", 1)[-1].rstrip(")") if "(" in libelle_indicateur else ""
        if not _carte_fin.empty:
            _haut = _carte_fin.loc[_carte_fin[col_indicateur].idxmax()]
            _bas = _carte_fin.loc[_carte_fin[col_indicateur].idxmin()]
            a_retenir(
                f"En {annee_max_carte}, valeur la plus élevée : <b>{_haut['pays_fr']}</b> "
                f"({fmt_fr(_haut[col_indicateur])}{_unite}) ; la plus faible : <b>{_bas['pays_fr']}</b> "
                f"({fmt_fr(_bas[col_indicateur])}{_unite}). La carte montre toujours les 206 pays de la base."
            )

        bouton_telechargement_csv(
            donnees_carte_anim.set_index("pays")[["code_iso", "annee", col_indicateur]],
            f"carte_{col_indicateur}_{annee_min_carte}_{annee_max_carte}.csv",
        )

    st.divider()
    st.subheader(f"Comparaison en barres de {len(pays_selectionnes)} pays — productions renouvelables")

    annees_dispo_carte = sorted(df["annee"].dropna().unique().astype(int), reverse=True)
    annee_carte = st.selectbox(
        "Année de comparaison", options=annees_dispo_carte, key="carte_annee",
    )

    objectif(f"Comparer la production d'électricité renouvelable des pays sélectionnés en {annee_carte}, "
             "et la part qu'y prennent le solaire et l'éolien.")

    def _valeur_ou_derniere_dispo(sous_df, colonne, annee_max):
        d = sous_df[(sous_df["annee"] <= annee_max) & sous_df[colonne].notna()].sort_values("annee")
        if d.empty:
            return None, None
        ligne = d.iloc[-1]
        return float(ligne[colonne]), int(ligne["annee"])

    lignes_barres = []
    for _p in pays_selectionnes:
        _sous = df[df["pays"] == _p]
        v_total, an_utilise = _valeur_ou_derniere_dispo(_sous, "electricite_renouvelable", annee_carte)
        v_solaire, _ = _valeur_ou_derniere_dispo(_sous, "electricite_solaire", annee_carte)
        v_eolien, _ = _valeur_ou_derniere_dispo(_sous, "electricite_eolienne", annee_carte)
        if v_total is not None:
            v_solaire = v_solaire or 0.0
            v_eolien = v_eolien or 0.0
            lignes_barres.append({
                "Pays": NOMS_FR.get(_p, _p),
                "Autres renouvelables": max(0.0, v_total - v_solaire - v_eolien),
                "Électricité solaire": v_solaire,
                "Électricité éolienne": v_eolien,
                "Renouvelable totale": v_total,
                "Année utilisée": an_utilise,
            })

    if not lignes_barres:
        st.warning("Aucune donnée disponible pour ces pays sur la période choisie.")
    else:
        tableau_barres = pd.DataFrame(lignes_barres).sort_values("Renouvelable totale", ascending=False)

        with st.container(border=True):
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=tableau_barres["Pays"], y=tableau_barres["Autres renouvelables"],
                name="Autres renouvelables", marker_color=GAEA_CORP["accent"],
            ))
            fig.add_trace(go.Bar(
                x=tableau_barres["Pays"], y=tableau_barres["Électricité solaire"],
                name="Électricité solaire", marker_color=GAEA_CORP["brown"],
            ))
            fig.add_trace(go.Bar(
                x=tableau_barres["Pays"], y=tableau_barres["Électricité éolienne"],
                name="Électricité éolienne", marker_color=GAEA_CORP["accent2"],
            ))
            fig.update_layout(barmode="stack")
            fig = theme_plotly(fig, hauteur=440, titre_y="Production d'électricité (TWh)")
            st.plotly_chart(fig, width="stretch", config=CONFIG_PLOTLY_EXPORT, key="chart_barres_empilees")
            st.caption(
                "« Autres renouvelables » = production renouvelable totale moins solaire et éolien "
                "(hydraulique, biocarburants...), pour que les trois segments s'additionnent exactement "
                "au total, sans double comptage. Suit la sélection de pays de la barre latérale."
            )

        _premier = tableau_barres.iloc[0]
        _part_sol_eol = ((_premier["Électricité solaire"] + _premier["Électricité éolienne"])
                         / _premier["Renouvelable totale"] * 100) if _premier["Renouvelable totale"] else 0
        a_retenir(
            f"Premier producteur d'électricité renouvelable : <b>{_premier['Pays']}</b> "
            f"(<b>{fmt_fr(_premier['Renouvelable totale'], 0)} TWh</b>), dont <b>{_part_sol_eol:.0f} %</b> "
            "de solaire et d'éolien."
        )
        bouton_telechargement_csv(
            tableau_barres.set_index("Pays"), f"barres_renouvelables_{annee_carte}.csv"
        )

st.markdown('<div class="gaea-section-label" style="margin-top:28px;">En savoir plus</div>',
            unsafe_allow_html=True)
_mois_fr = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
            "août", "septembre", "octobre", "novembre", "décembre"]
_jour = datetime.date.today()
_aujourdhui = f"{_jour.day} {_mois_fr[_jour.month - 1]} {_jour.year}"

with st.expander("Journal des nouveautés", icon=":material/new_releases:", expanded=True):
    _etapes = [
        ("🧭", "Dernière version", "Barre latérale repensée", [
            ("⚡", "Accès rapide", "un clic pour charger les géants mondiaux, l'Europe, les 7 pays du projet…"),
            ("📅", "Périodes rapides", "tout, depuis 2000 ou les 10 dernières années."),
            ("🎚️", "Jauge « Ta sélection »", "la part de renouvelables de tes pays face à la moyenne mondiale."),
            ("🔃", "Tri", "les pays les plus verts ou les moins verts d'abord, top 3 présélectionné."),
            ("❓", "Guide express", "les 3 étapes pour bien démarrer."),
        ]),
        ("📈", "Projection", "Droite ou courbe en S ?",
         "Les deux modèles sont ajustés puis départagés par backtest : on garde celui qui aurait le mieux "
         "prédit les 5 dernières années connues."),
        ("🎯", "Lecture", "9 onglets, une même structure",
         "Les doublons sont fusionnés (12 → 9 onglets). Chaque analyse s'ouvre sur un objectif et se termine "
         "par un encadré « À retenir »."),
        ("💰", "Cluster", "Profils socio-économiques",
         "PIB, renouvelables et intensité carbone croisés : k-means, CAH, silhouette et ACP complète "
         "(éboulis, cercle des corrélations)."),
        ("🏗️", "Fondations", "Le socle de l'application",
         "Graphiques Plotly, carte animée, nombres au format français, partage de vue par lien, "
         "exports CSV et image, installation sur téléphone."),
    ]
    st.markdown(
        '<div class="gaea-frise">' + "".join(
            f'<div class="gaea-frise-etape{" gaea-frise-nouveau" if i == 0 else ""}">'
            f'<div class="gaea-frise-point">{icone}</div>'
            f'<div class="gaea-frise-carte"><div class="gaea-frise-tag">{tag}</div>'
            f'<div class="gaea-frise-titre">{titre}</div>'
            + (f'<p>{texte}</p>' if isinstance(texte, str) else '<div class="gaea-frise-liste">' + "".join(
                f'<div><span>{ic}</span><p><b>{nom}</b> : {desc}</p></div>' for ic, nom, desc in texte
            ) + '</div>')
            + '</div></div>'
            for i, (icone, tag, titre, texte) in enumerate(_etapes)
        ) + '</div>',
        unsafe_allow_html=True,
    )

with st.expander("Méthodologie et sources", icon=":material/menu_book:", expanded=True):
    _nb_pays = fmt_fr(df["pays"].nunique(), decimales=0)
    _an_min, _an_max = int(df["annee"].min()), int(df["annee"].max())
    _onglets = ["🌱 Transition", "🔗 Corrélation", "📈 Projection", "🎯 Simulateur", "🏭 CO2 & GES",
                "🌍 Comparaison pays", "💰 Cluster", "🧪 Tests", "🗺️ Carte"]
    # Sources reprises de la bibliographie du rapport de stage
    _sources = [
        ("🌍", "Our World in Data", "https://ourworldindata.org/energy", "Base principale",
         "Fichiers Énergie et CO2/GES, qui compilent la <i>Statistical Review of World Energy</i> (Energy "
         "Institute), Ember et le Global Carbon Project."),
        ("🏦", "Banque mondiale", "https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD", "Données intégrées",
         "<i>World Development Indicators</i> : PIB par habitant en parité de pouvoir d'achat (cluster) et "
         "CO2 par secteur (EDGAR, AIE)."),
        ("🏭", "Climate Watch", "https://www.climatewatchdata.org", "Repère externe",
         "World Resources Institute : émissions de GES par pays et par secteur, sur 197 pays."),
        ("⚡", "IRENA et AIE", "https://www.irena.org/Data", "Validation",
         "<i>Renewable Capacity Statistics 2025</i>, <i>Renewables 2024</i> et <i>World Energy Outlook "
         "2024</i>, pour confronter les tendances observées."),
    ]
    _cartes_methodo = [
        ("📊", "Indicateurs",
         "<b>Part des renouvelables</b> dans l'électricité (%) · <b>intensité carbone</b> de l'électricité "
         "(gCO2/kWh) · <b>émissions de CO2 et de GES</b> par habitant."),
        ("🧮", "Méthodes",
         "Corrélation de Pearson et décalage temporel · tests t de Welch et apparié · droite et courbe en S "
         "avec backtest · ACP, k-means et CAH."),
        ("⚠️", "Limites",
         "Une corrélation ne prouve pas une causalité. Une projection prolonge une tendance, ce n'est pas une "
         "prévision. Certaines séries ont des années manquantes."),
    ]
    st.markdown(
        '<div class="gaea-methodo-bandeau">'
        f'<div><b>{_nb_pays}</b><span>pays et territoires</span></div>'
        f'<div><b>{_an_max - _an_min + 1}</b><span>ans, {_an_min}–{_an_max}</span></div>'
        f'<div><b>{len(_onglets)}</b><span>analyses</span></div>'
        '<div class="gaea-bandeau-survol" tabindex="0"><div class="gaea-bandeau-face"><b>5</b>'
        '<span>familles de méthodes</span><i>survole pour voir</i></div>'
        '<div class="gaea-bandeau-dos"><em>Corrélation</em><em>Tests t</em><em>Projection</em>'
        '<em>ACP</em><em>Classification</em></div></div></div>'
        '<div class="gaea-methodo-onglets">'
        + "".join(f"<span>{o}</span>" for o in _onglets) + '</div>'
        '<div class="gaea-sources"><div class="gaea-sources-titre">🗄️ Sources des données</div>'
        '<div class="gaea-sources-grille">' + "".join(
            f'<a class="gaea-source" href="{lien}" target="_blank"><div class="gaea-source-tete">'
            f'<span class="gaea-source-icone">{icone}</span><div><div class="gaea-source-role">{role}</div>'
            f'<div class="gaea-source-nom">{nom}</div></div></div><p>{texte}</p></a>'
            for icone, nom, lien, role, texte in _sources
        ) + '</div></div>'
        '<div class="gaea-methodo-grille">' + "".join(
            f'<div class="gaea-methodo-carte"><div class="gaea-methodo-icone">{icone}</div>'
            f'<div class="gaea-methodo-titre">{titre}</div><p>{texte}</p></div>'
            for icone, titre, texte in _cartes_methodo
        ) + '</div>'
        f'<div class="gaea-methodo-note">🕒 Mis à jour le <b>{_aujourdhui}</b> · '
        "complément Streamlit du tableau de bord HTML du sous-projet Trends "
        "(gaea21), réalisé avec Pandas, NumPy et Plotly.</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="gaea-pied">'
    '<div class="gaea-pied-titre">Trends · gaea21</div>'
    '<div class="gaea-pied-texte">Version Streamlit (Pandas · NumPy · Plotly) du sous-projet « Énergies '
    'renouvelables et GES ». Elle complète le tableau de bord HTML natif, livrable de référence.</div>'
    '<div class="gaea-pied-source">Données : <a href="https://ourworldindata.org/" target="_blank">Our World in '
    'Data</a>, <a href="https://data.worldbank.org/" target="_blank">Banque mondiale</a>, Climate Watch, '
    'IRENA et AIE · 206 pays et territoires · 1990–2024</div>'
    '</div>',
    unsafe_allow_html=True,
)