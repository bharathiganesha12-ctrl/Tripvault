
from database.extensions import db
from database.models import Destination, User
from services.auth_service import create_user


SAMPLE_DESTINATIONS = [
    {
        "name": "Santorini, Greece", "country": "Greece", "continent": "Europe",
        "category": "romantic", "price": 1299, "duration": 7, "best_time": "May – October",
        "rating": 4.9, "review_count": 428,
        "description": "Iconic blue domes, volcanic beaches, and stunning sunsets over the Aegean Sea.",
        "image_url": "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=600&q=80",
    },
    {
        "name": "Bali, Indonesia", "country": "Indonesia", "continent": "Asia",
        "category": "adventure", "price": 899, "duration": 10, "best_time": "Apr – Oct",
        "rating": 4.8, "review_count": 612,
        "description": "Lush rice terraces, ancient temples, and world-class surf breaks.",
        "image_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&q=80",
    },
    {
        "name": "Paris, France", "country": "France", "continent": "Europe",
        "category": "cultural", "price": 1499, "duration": 6, "best_time": "Apr – Jun, Sep – Nov",
        "rating": 4.9, "review_count": 891,
        "description": "The City of Light — art, cuisine, and the timeless Eiffel Tower.",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600&q=80",
    },
    {
        "name": "Maldives", "country": "Maldives", "continent": "Asia",
        "category": "luxury", "price": 2199, "duration": 8, "best_time": "Nov – Apr",
        "rating": 5.0, "review_count": 305,
        "description": "Overwater bungalows, crystal lagoons, and pristine coral reefs.",
        "image_url": "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=600&q=80",
    },
    {
        "name": "Tokyo, Japan", "country": "Japan", "continent": "Asia",
        "category": "cultural", "price": 1099, "duration": 9, "best_time": "Mar – May, Sep – Nov",
        "rating": 4.8, "review_count": 744,
        "description": "Where ancient temples meet neon-lit skylines and Michelin-starred ramen.",
        "image_url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&q=80",
    },
    {
        "name": "Machu Picchu, Peru", "country": "Peru", "continent": "Americas",
        "category": "adventure", "price": 1349, "duration": 8, "best_time": "May – Sep",
        "rating": 4.7, "review_count": 389,
        "description": "The Lost City of the Incas, perched high in the Andes Mountains.",
        "image_url": "https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=600&q=80",
    },
    {
        "name": "Cape Town, South Africa", "country": "South Africa", "continent": "Africa",
        "category": "wildlife", "price": 999, "duration": 9, "best_time": "Oct – Apr",
        "rating": 4.7, "review_count": 267,
        "description": "Table Mountain, Cape Point, and the Big Five — an African icon.",
        "image_url": "https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=600&q=80",
    },
    {
        "name": "New York, USA", "country": "USA", "continent": "Americas",
        "category": "cultural", "price": 1199, "duration": 6, "best_time": "Apr – Jun, Sep – Nov",
        "rating": 4.7, "review_count": 1023,
        "description": "Times Square, Central Park, and world-class museums — the city that never sleeps.",
        "image_url": "https://images.unsplash.com/photo-1534430480872-3498386e7856?w=600&q=80",
    },
    {
        "name": "Amalfi Coast, Italy", "country": "Italy", "continent": "Europe",
        "category": "romantic", "price": 1599, "duration": 7, "best_time": "Apr – Oct",
        "rating": 4.9, "review_count": 453,
        "description": "Cliffside villages, turquoise sea, and the world's finest limoncello.",
        "image_url": "https://images.unsplash.com/photo-1533587851505-d119e13fa0d7?w=600&q=80",
    },
    {
        "name": "Sydney, Australia", "country": "Australia", "continent": "Oceania",
        "category": "beach", "price": 1449, "duration": 8, "best_time": "Sep – Nov, Mar – May",
        "rating": 4.8, "review_count": 532,
        "description": "Opera House, Bondi Beach, and the vibrant harbour city of the Southern Hemisphere.",
        "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80",
    },
    {
        "name": "Phuket, Thailand", "country": "Thailand", "continent": "Asia",
        "category": "beach", "price": 749, "duration": 10, "best_time": "Nov – Apr",
        "rating": 4.6, "review_count": 688,
        "description": "Crystal-clear bays, night markets, and legendary Thai hospitality.",
        "image_url": "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=600&q=80",
    },
    {
        "name": "Amsterdam, Netherlands", "country": "Netherlands", "continent": "Europe",
        "category": "cultural", "price": 1099, "duration": 5, "best_time": "Apr – Sep",
        "rating": 4.7, "review_count": 398,
        "description": "Canal houses, world-class art, and the best cycling culture in Europe.",
        "image_url": "https://images.unsplash.com/photo-1534430480872-3498386e7856?w=600&q=80",
    },
    {
        "name": "Dubai, UAE", "country": "United Arab Emirates", "continent": "Asia",
        "category": "luxury", "price": 1199, "duration": 6, "best_time": "Nov – Mar",
        "rating": 4.8, "review_count": 578,
        "description": "Skyline views, desert adventures, and unforgettable Arabian hospitality.",
        "image_url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&q=80",
    },
    {
        "name": "Swiss Alps, Switzerland", "country": "Switzerland", "continent": "Europe",
        "category": "adventure", "price": 1799, "duration": 8, "best_time": "Dec – Mar, Jun – Sep",
        "rating": 4.9, "review_count": 341,
        "description": "Snow-capped peaks, scenic railways, and alpine villages made for slow travel.",
        "image_url": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=600&q=80",
    },
    {
        "name": "Cairo, Egypt", "country": "Egypt", "continent": "Africa",
        "category": "cultural", "price": 849, "duration": 7, "best_time": "Oct – Apr",
        "rating": 4.6, "review_count": 286,
        "description": "Ancient pyramids, Nile sunsets, and thousands of years of living history.",
        "image_url": "https://images.unsplash.com/photo-1503177119275-0aa32b3a9368?w=600&q=80",
    },
    {
        "name": "Istanbul, Türkiye", "country": "Türkiye", "continent": "Europe",
        "category": "cultural", "price": 799, "duration": 6, "best_time": "Apr – Jun, Sep – Oct",
        "rating": 4.7, "review_count": 433,
        "description": "A captivating bridge of continents, spice markets, mosques, and Bosphorus views.",
        "image_url": "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=600&q=80",
    },
    {
        "name": "Reykjavik, Iceland", "country": "Iceland", "continent": "Europe",
        "category": "adventure", "price": 1549, "duration": 7, "best_time": "Sep – Mar",
        "rating": 4.8, "review_count": 255,
        "description": "Chase the Northern Lights, soak in geothermal lagoons, and explore volcanic landscapes.",
        "image_url": "https://images.unsplash.com/photo-1504893524553-b855bce32c67?w=600&q=80",
    },
    {
        "name": "Rio de Janeiro, Brazil", "country": "Brazil", "continent": "Americas",
        "category": "beach", "price": 1049, "duration": 8, "best_time": "Dec – Mar",
        "rating": 4.7, "review_count": 367,
        "description": "Golden beaches, samba nights, and panoramic views from Sugarloaf Mountain.",
        "image_url": "https://images.unsplash.com/photo-1483729558449-99ef09a8c325?w=600&q=80",
    },
    {
        "name": "Queenstown, New Zealand", "country": "New Zealand", "continent": "Oceania",
        "category": "adventure", "price": 1899, "duration": 10, "best_time": "Dec – Feb, Jun – Aug",
        "rating": 4.9, "review_count": 219,
        "description": "A playground of fjords, mountains, bungee jumps, and crystal-clear lakes.",
        "image_url": "https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=600&q=80",
    },
    {
        "name": "Lisbon, Portugal", "country": "Portugal", "continent": "Europe",
        "category": "cultural", "price": 899, "duration": 6, "best_time": "Mar – Oct",
        "rating": 4.8, "review_count": 504,
        "description": "Hillside trams, tiled streets, Atlantic light, and a brilliant food scene.",
        "image_url": "https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=600&q=80",
    },
    {
        "name": "Seychelles", "country": "Seychelles", "continent": "Africa",
        "category": "beach", "price": 1999, "duration": 8, "best_time": "Apr – May, Oct – Nov",
        "rating": 4.9, "review_count": 188,
        "description": "Granite coves, warm turquoise water, and quiet island escapes in the Indian Ocean.",
        "image_url": "https://images.unsplash.com/photo-1589979481223-deb893043163?w=600&q=80",
    },
    {
        "name": "Marrakech, Morocco", "country": "Morocco", "continent": "Africa",
        "category": "cultural", "price": 749, "duration": 5, "best_time": "Mar – May, Sep – Nov",
        "rating": 4.7, "review_count": 312,
        "description": "Colourful souks, riads, desert horizons, and the energy of Jemaa el-Fnaa.",
        "image_url": "https://images.unsplash.com/photo-1597212618440-806262de4f6b?w=600&q=80",
    },
    {
        "name": "Vancouver, Canada", "country": "Canada", "continent": "Americas",
        "category": "wildlife", "price": 1299, "duration": 8, "best_time": "May – Sep",
        "rating": 4.8, "review_count": 276,
        "description": "Mountains, ocean, forests, and one of North America's most walkable cities.",
        "image_url": "https://images.unsplash.com/photo-1559511260-66a654ae982a?w=600&q=80",
    },
    {
        "name": "Kerala, India", "country": "India", "continent": "Asia",
        "category": "relaxation", "price": 699, "duration": 7, "best_time": "Oct – Mar",
        "rating": 4.8, "review_count": 451,
        "description": "Backwaters, spice gardens, palm-lined beaches, and restorative slow living.",
        "image_url": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=600&q=80",
    },
    {
        "name": "Prague, Czechia", "country": "Czechia", "continent": "Europe",
        "category": "romantic", "price": 849, "duration": 5, "best_time": "Apr – Jun, Sep – Oct",
        "rating": 4.7, "review_count": 391,
        "description": "Storybook bridges, castle views, and atmospheric old-town evenings.",
        "image_url": "https://images.unsplash.com/photo-1519677100203-a0e668c92439?w=600&q=80",
    },
    {
        "name": "Galápagos Islands, Ecuador", "country": "Ecuador", "continent": "Americas",
        "category": "wildlife", "price": 2299, "duration": 9, "best_time": "Jun – Dec",
        "rating": 5.0, "review_count": 147,
        "description": "Walk among remarkable wildlife and discover pristine volcanic islands.",
        "image_url": "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=600&q=80",
    },
]


def seed_db(app):
    
    with app.app_context():
        # Destinations
        # Add missing records as the catalogue grows; this is safe to run on
        # an existing local database and during a Render deploy.
        existing_names = {d.name for d in Destination.query.with_entities(Destination.name).all()}
        missing = [d for d in SAMPLE_DESTINATIONS if d['name'] not in existing_names]
        for d in missing:
            db.session.add(Destination(**d))
        if missing:
            db.session.commit()
        print(f'  Destination catalogue ready: {Destination.query.count()} places ({len(missing)} added).')

        # Demo admin
        if not User.query.filter_by(email='admin@tripvault.com').first():
            admin = create_user('Admin', 'User', 'admin@tripvault.com', 'Admin@1234')
            admin.is_admin = True
            db.session.commit()
            print('  Created admin account: admin@tripvault.com / Admin@1234')

        # Demo regular user
        if not User.query.filter_by(email='john@example.com').first():
            create_user('John', 'Traveller', 'john@example.com', 'John@1234')
            print('  Created demo user: john@example.com / John@1234')

        print('Seed complete.')
