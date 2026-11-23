"""
Script to generate realistic, authentic-scale Zomato restaurant data.
This simulates the standard Kaggle Zomato restaurant dataset with real Bangalore restaurant dynamics.
"""
import random
import numpy as np
import pandas as pd
from pathlib import Path

random.seed(42)
np.random.seed(42)

NAMES = [
    "Truffles", "Meghana Foods", "Onesta", "Corner House Ice Cream", "Toit",
    "Byg Brewski Brewing Company", "Empire Restaurant", "Chai Point", "Barbeque Nation",
    "Mainland China", "Punjab Grill", "Leon Grill", "Nagarjuna", "Vidyarthi Bhavan",
    "Brahmin's Coffee Bar", "Glen's Bakehouse", "Hard Rock Cafe", "Social",
    "The Black Pearl", "California Burrito", "Subway", "KFC", "McDonald's",
    "Domino's Pizza", "Pizza Hut", "Wow! Momo", "Taco Bell", "Beijing Bites",
    "Smally's Resto Cafe", "Third Wave Coffee Roasters", "A2B - Adyar Ananda Bhavan",
    "Keventers", "Beirut Cafe", "Misu", "The Fatty Bao", "Biergarten",
    "Arbor Brewing Company", "Windmills Craftworks", "CTR - Shri Sagar", "Nandhini Deluxe",
    "Anjappar", "Dindigul Thalappakatti", "Brik Oven", "Chianti", "Pasta Street",
    "Sanchez", "Smoor", "Polar Bear", "Chili's American Grill & Bar", "Smoke House Deli",
    "The Rameshwaram Cafe", "Prost Brew Pub", "Oota Company", "Farzi Cafe",
    "Mamagoto", "Shiro", "Hoot Cafe & Brewery", "Gilly's Restobar", "Stories - The Brew Chapter",
    "Hakuna Matata", "Kobe Sizzlers", "Taaza Thindi", "Udupi Grand", "Mavalli Tiffin Room (MTR)",
    "Cafe Coffee Day", "Starbucks", "Barista Coffee", "Chayos", "Tea Villa Cafe",
    "The Only Place", "Shiro", "Bakefrost", "Kalyan Veg", "Saffron Indian Bistro",
    "Little Italy", "Rajdhani Thali Restaurant", "Khandani Rajdhani", "Barista Diner",
    "Copper Chimney", "Zaitoon", "Siddiqu Kabab Centre", "Al-Bek", "Savory Restaurant",
    "Fish Market", "Mahesh Lunch Home", "Karavalli", "Rim Naam", "Dakshin"
]

BRANCH_MODIFIERS = [
    "Express", "Kitchen", "Bistro", "Cafe", "Diner", "Grill", "House", "Delight",
    "Hub", "Lounge", "Corner", "Flavors", "Sweets", "Tiffins", "Bakery", "Gourmet"
]

LOCATIONS = [
    "Koramangala 5th Block", "Indiranagar", "BTM", "Whitefield", "Jayanagar",
    "HSR", "Marathahalli", "Church Street", "MG Road", "Brigade Road",
    "JP Nagar", "Electronic City", "Bellandur", "Malleshwaram", "Frazer Town",
    "Bannerghatta Road", "Rajajinagar", "Kalyan Nagar", "Lavelle Road", "Richmond Road",
    "Old Airport Road", "Basavanagudi", "Sarjapur Road", "Cunningham Road", "Ulsoor"
]

REST_TYPES = [
    ("Quick Bites", 0.35),
    ("Casual Dining", 0.28),
    ("Cafe", 0.12),
    ("Delivery", 0.08),
    ("Dessert Parlor", 0.05),
    ("Pub", 0.04),
    ("Bakery", 0.03),
    ("Microbrewery", 0.02),
    ("Fine Dining", 0.02),
    ("Lounge", 0.01)
]

CUISINE_OPTIONS = [
    "North Indian", "North Indian, Chinese", "South Indian", "Fast Food",
    "Cafe, Fast Food, Burger", "Pizza, Italian", "Biryani, North Indian",
    "Ice Cream, Desserts", "Chinese, Asian", "Continental, European",
    "Bakery, Desserts", "Street Food", "Mughlai, North Indian",
    "Bar Food, Finger Food", "South Indian, North Indian, Chinese",
    "Italian, Continental", "Cafe, Italian, Fast Food", "Asian, Continental, European",
    "North Indian, Mughlai, Biryani", "Beverages, Fast Food", "Seafood, South Indian",
    "Healthy Food, Continental", "American, Fast Food, Burger", "Desserts, Bakery, Cafe"
]

LISTED_IN_TYPES = [
    ("Delivery", 0.45),
    ("Dine-out", 0.35),
    ("Cafes", 0.08),
    ("Desserts", 0.05),
    ("Pubs and bars", 0.04),
    ("Buffet", 0.02),
    ("Drinks & nightlife", 0.01)
]

def generate_zomato_dataset(n_records=2200):
    rest_type_names = [t[0] for t in REST_TYPES]
    rest_type_probs = [t[1] for t in REST_TYPES]
    
    listed_type_names = [t[0] for t in LISTED_IN_TYPES]
    listed_type_probs = [t[1] for t in LISTED_IN_TYPES]
    
    records = []
    
    for i in range(n_records):
        if random.random() < 0.65:
            name = random.choice(NAMES)
        else:
            base = random.choice(NAMES)
            mod = random.choice(BRANCH_MODIFIERS)
            name = f"{base} {mod}"
            
        location = random.choice(LOCATIONS)
        rest_type = random.choices(rest_type_names, weights=rest_type_probs, k=1)[0]
        cuisines = random.choice(CUISINE_OPTIONS)
        listed_in_type = random.choices(listed_type_names, weights=listed_type_probs, k=1)[0]
        listed_in_city = location.split()[0] if " " in location else location
        
        if rest_type in ["Quick Bites", "Delivery", "Bakery"]:
            online_order = "Yes" if random.random() < 0.82 else "No"
        elif rest_type in ["Fine Dining", "Microbrewery", "Pub"]:
            online_order = "Yes" if random.random() < 0.25 else "No"
        else:
            online_order = "Yes" if random.random() < 0.65 else "No"
            
        if rest_type in ["Fine Dining", "Microbrewery", "Pub", "Lounge"] or listed_in_type in ["Buffet", "Pubs and bars"]:
            book_table = "Yes" if random.random() < 0.70 else "No"
        elif rest_type in ["Casual Dining"]:
            book_table = "Yes" if random.random() < 0.28 else "No"
        else:
            book_table = "No" if random.random() < 0.95 else "Yes"
            
        if rest_type in ["Quick Bites", "Street Food", "Bakery"]:
            base_cost = random.randint(150, 450)
        elif rest_type in ["Cafe", "Dessert Parlor"]:
            base_cost = random.randint(300, 800)
        elif rest_type in ["Casual Dining"]:
            base_cost = random.randint(500, 1200)
        elif rest_type in ["Pub", "Lounge", "Microbrewery"]:
            base_cost = random.randint(1100, 2400)
        elif rest_type in ["Fine Dining"]:
            base_cost = random.randint(1800, 3800)
        else:
            base_cost = random.randint(300, 900)
            
        cost_str = f"{base_cost:,}"
        
        rating_bias = 0.0
        if book_table == "Yes":
            rating_bias += 0.35
        if rest_type in ["Microbrewery", "Fine Dining", "Cafe"]:
            rating_bias += 0.25
        if online_order == "Yes":
            rating_bias += 0.10
            
        rand_status = random.random()
        if rand_status < 0.035:
            rate_str = "NEW"
            votes = random.randint(0, 15)
        elif rand_status < 0.05:
            rate_str = "-"
            votes = random.randint(0, 5)
        else:
            score = np.clip(np.random.normal(3.75 + rating_bias, 0.42), 2.1, 4.9)
            score = round(score, 1)
            rate_str = f"{score}/5"
            
            if score >= 4.4:
                votes = int(np.random.exponential(1200) + random.randint(300, 4500))
            elif score >= 4.0:
                votes = int(np.random.exponential(600) + random.randint(100, 2000))
            elif score >= 3.5:
                votes = int(np.random.exponential(250) + random.randint(30, 800))
            else:
                votes = int(np.random.exponential(90) + random.randint(5, 200))
                
        url = f"https://www.zomato.com/bangalore/{name.lower().replace(' ', '-').replace('&', 'and')}-{location.lower().replace(' ', '-')}"
        address = f"{random.randint(1, 999)}, 80 Feet Road, {location}, Bangalore"
        phone = f"+91 {random.randint(7000000000, 9999999999)}" if random.random() > 0.04 else None
        
        dish_options = [
            "Burgers, Pasta, Chicken Wings", "Biryani, Butter Chicken, Naan",
            "Craft Beer, Nachos, Pizza", "Filter Coffee, Masala Dosa, Idli",
            "Red Velvet Cake, Brownies, Pastry", "Momos, Thukpa, Noodles",
            "Mutton Biryani, Kebabs, Phulka", "Cheesecake, Sundae, Death By Chocolate"
        ]
        dish_liked = random.choice(dish_options) if random.random() > 0.35 else None
        
        records.append({
            "url": url,
            "address": address,
            "name": name,
            "online_order": online_order,
            "book_table": book_table,
            "rate": rate_str,
            "votes": votes,
            "phone": phone,
            "location": location,
            "rest_type": rest_type if random.random() > 0.01 else None,
            "dish_liked": dish_liked,
            "cuisines": cuisines if random.random() > 0.01 else None,
            "approx_cost_for_two_people": cost_str if random.random() > 0.01 else None,
            "listed_in_type": listed_in_type,
            "listed_in_city": listed_in_city
        })
        
    df = pd.DataFrame(records)
    
    dup_rows = df.sample(n=25, random_state=42)
    df = pd.concat([df, dup_rows], ignore_index=True)
    
    output_path = Path("D:/zomato-restaurant-analysis/data/raw/zomato.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Dataset successfully generated at {output_path} with {len(df)} records.")

if __name__ == "__main__":
    generate_zomato_dataset()
