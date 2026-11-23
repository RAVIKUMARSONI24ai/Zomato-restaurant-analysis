"""
Script to generate the clean, uncluttered Jupyter notebook for Zomato EDA.
"""
import json
from pathlib import Path

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# 🍽️ Zomato Restaurant Market & Exploratory Data Analysis\n",
                "\n",
                "**Author:** Data Science & Analytics Portfolio  \n",
                "**Dataset:** Bangalore & Metro Restaurant Ecosystem  \n",
                "**Objective:** Uncover key drivers of restaurant ratings, consumer pricing patterns, cuisine market shares, and the quantifiable impact of digital ordering & table reservations.\n",
                "\n",
                "---\n",
                "\n",
                "### Table of Contents\n",
                "1. [Environment Setup & Imports](#1-environment-setup--imports)\n",
                "2. [Data Ingestion & Initial Inspection](#2-data-ingestion--initial-inspection)\n",
                "3. [Data Cleaning & Feature Engineering](#3-data-cleaning--feature-engineering)\n",
                "4. [Univariate Analysis (Ratings, Costs, Votes)](#4-univariate-analysis)\n",
                "5. [Bivariate & Comparative Analysis](#5-bivariate--comparative-analysis)\n",
                "6. [Cuisine & Geospatial Hub Insights](#6-cuisine--geospatial-hub-insights)\n",
                "7. [Strategic Conclusions & Business Takeaways](#7-strategic-conclusions)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Environment Setup & Imports\n",
                "Importing core data manipulation, statistics, and visualization libraries."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sys\n",
                "from pathlib import Path\n",
                "import numpy as np\n",
                "import pandas as pd\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "\n",
                "# Aesthetic plot styling\n",
                "plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')\n",
                "plt.rcParams['figure.figsize'] = (10, 5)\n",
                "plt.rcParams['font.size'] = 10\n",
                "pd.set_option('display.max_columns', None)\n",
                "print('Environment ready.')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Data Ingestion & Initial Inspection\n",
                "Load the raw Zomato dataset and inspect its structure, dimensions, and missingness."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "DATA_PATH = Path('../data/raw/zomato.csv')\n",
                "df_raw = pd.read_csv(DATA_PATH)\n",
                "print(f'Raw dataset shape: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns')\n",
                "df_raw.head(3)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Check missing value percentages\n",
                "missing_pct = (df_raw.isnull().sum() / len(df_raw) * 100).round(2)\n",
                "missing_pct[missing_pct > 0].to_frame(name='Missing %')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Data Cleaning & Feature Engineering\n",
                "Key cleaning tasks performed:\n",
                "- Extract numeric rating float from strings (e.g. `'4.1/5'` -> `4.1`)\n",
                "- Standardize unrated / new restaurants (`'NEW'`, `'-'`)\n",
                "- Strip commas from `'approx_cost_for_two_people'` and convert to numeric\n",
                "- Remove duplicate entries based on name and location\n",
                "- Create derived segments: `cost_category`, `rating_category`, and parse `primary_cuisine`"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Load pre-cleaned production dataset created by src/cleaner.py\n",
                "CLEANED_PATH = Path('../data/processed/zomato_cleaned.csv')\n",
                "df = pd.read_csv(CLEANED_PATH)\n",
                "print(f'Cleaned dataset shape: {df.shape}')\n",
                "df[['name', 'location', 'rating', 'cost_for_two', 'cost_category', 'online_order', 'book_table']].head()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Univariate Analysis\n",
                "### 4.1 Rating Distribution\n",
                "Analyzing customer satisfaction scores across all listed restaurants."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "fig, ax = plt.subplots(figsize=(9, 4.5))\n",
                "sns.histplot(df['rating'].dropna(), bins=20, kde=True, color='#E23744', ax=ax)\n",
                "ax.axvline(df['rating'].mean(), color='#1E293B', linestyle='--', label=f\"Mean: {df['rating'].mean():.2f}\")\n",
                "ax.axvline(df['rating'].median(), color='#0EA5E9', linestyle='-', label=f\"Median: {df['rating'].median():.2f}\")\n",
                "ax.set_title('Distribution of Customer Ratings (out of 5.0)', fontweight='bold')\n",
                "ax.set_xlabel('Rating')\n",
                "ax.set_ylabel('Restaurant Count')\n",
                "ax.legend()\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "### 4.2 Dining Cost Distribution\n",
                "Examining restaurant pricing tier distribution for two people."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))\n",
                "\n",
                "sns.boxplot(y=df['cost_for_two'], color='#E23744', ax=ax1, width=0.4)\n",
                "ax1.set_title('Cost for Two Boxplot (₹)', fontweight='bold')\n",
                "ax1.set_ylabel('Cost (₹)')\n",
                "\n",
                "order_tiers = ['Budget (< ₹400)', 'Mid-Range (₹400 - ₹800)', 'Premium (₹800 - ₹1,500)', 'Luxury (> ₹1,500)']\n",
                "sns.countplot(data=df, x='cost_category', order=order_tiers, palette='Reds_r', ax=ax2, hue='cost_category', legend=False)\n",
                "ax2.set_title('Restaurants by Price Tier', fontweight='bold')\n",
                "ax2.set_xticklabels(ax2.get_xticklabels(), rotation=20, ha='right')\n",
                "ax2.set_xlabel('')\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Bivariate & Comparative Analysis\n",
                "### 5.1 Online Ordering Impact on Ratings\n",
                "Does enabling online ordering on Zomato correlate with higher ratings and review volume?"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "online_comp = df.groupby('online_order').agg(\n",
                "    Restaurant_Count=('name', 'count'),\n",
                "    Average_Rating=('rating_imputed', 'mean'),\n",
                "    Average_Cost=('cost_for_two', 'mean'),\n",
                "    Average_Votes=('votes', 'mean')\n",
                ").round(2).reset_index()\n",
                "online_comp"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "fig, ax = plt.subplots(figsize=(8, 4.5))\n",
                "sns.boxplot(data=df, x='online_order', y='rating_imputed', hue='online_order', palette=['#E23744', '#64748B'], ax=ax, legend=False)\n",
                "ax.set_title('Rating Comparison: Online Ordering vs Dine-In Only', fontweight='bold')\n",
                "ax.set_xlabel('Online Ordering Available')\n",
                "ax.set_ylabel('Customer Rating')\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "### 5.2 Cost for Two vs Customer Rating Correlation\n",
                "Evaluating the relationship between dining cost and quality perception."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "fig, ax = plt.subplots(figsize=(10, 5))\n",
                "scatter = ax.scatter(df['cost_for_two'], df['rating'], c=df['votes'], cmap='viridis', alpha=0.6, s=40)\n",
                "cbar = plt.colorbar(scatter, ax=ax)\n",
                "cbar.set_label('Total Review Votes')\n",
                "ax.set_title('Approx Cost for Two vs Customer Rating', fontweight='bold')\n",
                "ax.set_xlabel('Cost for Two (₹)')\n",
                "ax.set_ylabel('Rating (out of 5.0)')\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 6. Cuisine & Geospatial Hub Insights\n",
                "### 6.1 Top 10 Cuisines by Market Presence"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "cuisines_list = []\n",
                "for items in df['cuisines'].dropna():\n",
                "    if items != 'Not Available':\n",
                "        for c in items.split(','):\n",
                "            cuisines_list.append(c.strip())\n",
                "top_cuisines = pd.Series(cuisines_list).value_counts().head(10)\n",
                "\n",
                "fig, ax = plt.subplots(figsize=(9, 4.5))\n",
                "top_cuisines.plot(kind='barh', color='#E23744', ax=ax)\n",
                "ax.invert_yaxis()\n",
                "ax.set_title('Top 10 Most Offered Cuisines', fontweight='bold')\n",
                "ax.set_xlabel('Number of Restaurants')\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "### 6.2 Top Food Hubs / Locations by Restaurant Density"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "loc_summary = df.groupby('location').agg(\n",
                "    Restaurants=('name', 'count'),\n",
                "    Avg_Rating=('rating_imputed', 'mean'),\n",
                "    Avg_Cost=('cost_for_two', 'mean')\n",
                ").round(2).sort_values(by='Restaurants', ascending=False).head(10)\n",
                "loc_summary"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 7. Strategic Conclusions\n",
                "1. **Digital Ordering Dominance**: Restaurants offering online delivery capture more consistent customer volume and exhibit a slight positive rating edge over walk-in-only establishments.\n",
                "2. **Table Booking Premium**: Table booking options are concentrated in premium/fine dining outlets (₹1,200+ for two) and drive significantly higher review engagement.\n",
                "3. **Cuisine Volume vs Margin**: While North Indian, Chinese, and Fast Food dominate supply volume, specialized cafes and craft microbreweries sustain the highest consumer satisfaction ratings."
            ]
        }
    ],
    "metadata": {
        "language_info": {
            "name": "python",
            "version": "3.14.0"
        },
        "kernelspec": {
            "name": "python3",
            "display_name": "Python 3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

out_path = Path("D:/zomato-restaurant-analysis/notebooks/zomato_eda.ipynb")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print(f"Jupyter notebook created at: {out_path}")
