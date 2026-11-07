"""
Mock data catalogue and customer reviews for the e-commerce backend.
Contains realistic, verified data across Belts, Shoes, Wallets, and Jackets.
"""

from typing import List, Dict, Any

# Initial mock review database (3 to 5 reviews per product)
RAW_REVIEWS: List[Dict[str, Any]] = [
    # PROD001: Classic Reversible Leather Belt (Belts)
    {
        "review_id": "REV001",
        "product_id": "PROD001",
        "reviewer_name": "Aarav Sharma",
        "rating": 5.0,
        "comment": "Exceptional genuine leather quality. Love the reversible swivel buckle mechanism, works with both formal black and brown shoes.",
        "review_date": "2024-01-15",
        "verified_purchase": True,
    },
    {
        "review_id": "REV002",
        "product_id": "PROD001",
        "reviewer_name": "Rohan Mehra",
        "rating": 4.5,
        "comment": "Very sturdy belt. Buckle rotates smoothly. Fits true to size, perfect for everyday office wear.",
        "review_date": "2024-02-02",
        "verified_purchase": True,
    },
    {
        "review_id": "REV003",
        "product_id": "PROD001",
        "reviewer_name": "Vikram Patel",
        "rating": 4.0,
        "comment": "Good durable leather at this discount price. A bit stiff initially but softened nicely within a week.",
        "review_date": "2024-02-20",
        "verified_purchase": False,
    },
    {
        "review_id": "REV004",
        "product_id": "PROD001",
        "reviewer_name": "Ananya Roy",
        "rating": 4.5,
        "comment": "Bought this as a birthday gift for my husband. Premium packaging and elegant finish.",
        "review_date": "2024-03-05",
        "verified_purchase": True,
    },

    # PROD002: Formal Full-Grain Leather Dress Belt (Belts)
    {
        "review_id": "REV005",
        "product_id": "PROD002",
        "reviewer_name": "Aditya Nair",
        "rating": 5.0,
        "comment": "True full-grain leather with clean edge stitching. Matches tailored formal trousers perfectly.",
        "review_date": "2024-01-22",
        "verified_purchase": True,
    },
    {
        "review_id": "REV006",
        "product_id": "PROD002",
        "reviewer_name": "Sameer Joshi",
        "rating": 4.0,
        "comment": "Top-notch craftsmanship from Woodland. The brushed brass buckle gives a vintage touch.",
        "review_date": "2024-02-18",
        "verified_purchase": True,
    },
    {
        "review_id": "REV007",
        "product_id": "PROD002",
        "reviewer_name": "Kunal Sen",
        "rating": 4.5,
        "comment": "Very comfortable and durable. Sizing is accurate and the leather doesn't crease easily.",
        "review_date": "2024-03-12",
        "verified_purchase": True,
    },

    # PROD003: Heavy-Duty Casual Canvas Webbed Belt (Belts)
    {
        "review_id": "REV008",
        "product_id": "PROD003",
        "reviewer_name": "Karan Malhotra",
        "rating": 4.5,
        "comment": "Military-grade sturdy canvas strap. Quick-release metal buckle is super convenient for cargo pants.",
        "review_date": "2024-01-10",
        "verified_purchase": True,
    },
    {
        "review_id": "REV009",
        "product_id": "PROD003",
        "reviewer_name": "Pooja Hegde",
        "rating": 4.0,
        "comment": "Nice casual look for jeans. The belt length is easy to trim down if required.",
        "review_date": "2024-02-14",
        "verified_purchase": True,
    },
    {
        "review_id": "REV010",
        "product_id": "PROD003",
        "reviewer_name": "Nikhil Rao",
        "rating": 3.5,
        "comment": "Solid canvas material, but the buckle is a bit heavier than I expected. Good value overall.",
        "review_date": "2024-03-01",
        "verified_purchase": False,
    },
    {
        "review_id": "REV011",
        "product_id": "PROD003",
        "reviewer_name": "Rahul Verma",
        "rating": 4.0,
        "comment": "Breathable and flexible. Great for outdoor trekking and casual weekend wear.",
        "review_date": "2024-03-19",
        "verified_purchase": True,
    },

    # PROD004: Handcrafted Italian Leather Automatic Buckle Belt (Belts)
    {
        "review_id": "REV012",
        "product_id": "PROD004",
        "reviewer_name": "Varun Kapoor",
        "rating": 5.0,
        "comment": "The micro-adjustable ratchet mechanism is fantastic! No more stretched hole marks.",
        "review_date": "2024-01-29",
        "verified_purchase": True,
    },
    {
        "review_id": "REV013",
        "product_id": "PROD004",
        "reviewer_name": "Siddharth Jain",
        "rating": 4.5,
        "comment": "Luxury feel and sleek satin buckle. Tommy Hilfiger delivered premium quality.",
        "review_date": "2024-02-15",
        "verified_purchase": True,
    },
    {
        "review_id": "REV014",
        "product_id": "PROD004",
        "reviewer_name": "Arjun Singhal",
        "rating": 4.5,
        "comment": "Perfect fit every time thanks to the click track. Highly recommended for suits.",
        "review_date": "2024-03-09",
        "verified_purchase": True,
    },

    # PROD005: Braided Stretch Elastic Woven Belt (Belts)
    {
        "review_id": "REV015",
        "product_id": "PROD005",
        "reviewer_name": "Manish Tiwari",
        "rating": 4.0,
        "comment": "Super stretchy and comfortable when sitting for long hours. No predetermined holes needed.",
        "review_date": "2024-01-08",
        "verified_purchase": True,
    },
    {
        "review_id": "REV016",
        "product_id": "PROD005",
        "reviewer_name": "Deepak Ahuja",
        "rating": 3.5,
        "comment": "Good stretch belt for chinos and golf shorts. Elastic is firm enough to hold up well.",
        "review_date": "2024-02-11",
        "verified_purchase": True,
    },
    {
        "review_id": "REV017",
        "product_id": "PROD005",
        "reviewer_name": "Gaurav Sen",
        "rating": 4.5,
        "comment": "Loved the navy woven pattern and leather trims. Great casual accessory.",
        "review_date": "2024-03-02",
        "verified_purchase": False,
    },

    # PROD006: Vintage Distress Leather Cowboy Belt (Belts)
    {
        "review_id": "REV018",
        "product_id": "PROD006",
        "reviewer_name": "Harshvardhan Rana",
        "rating": 5.0,
        "comment": "Authentic rustic distressed leather with heavy brass buckle. Looks even better with age.",
        "review_date": "2024-01-19",
        "verified_purchase": True,
    },
    {
        "review_id": "REV019",
        "product_id": "PROD006",
        "reviewer_name": "Devendra Bisht",
        "rating": 4.5,
        "comment": "Thick, genuine cowhide leather. Pairs brilliantly with heavy raw denim jeans.",
        "review_date": "2024-02-23",
        "verified_purchase": True,
    },
    {
        "review_id": "REV020",
        "product_id": "PROD006",
        "reviewer_name": "Prateek Goel",
        "rating": 4.0,
        "comment": "Robust quality as expected from Woodland. A bit heavy, but built to last years.",
        "review_date": "2024-03-14",
        "verified_purchase": True,
    },

    # PROD007: Air Stride Lightweight Running Shoes (Shoes)
    {
        "review_id": "REV021",
        "product_id": "PROD007",
        "reviewer_name": "Tanmay Bhattacharya",
        "rating": 5.0,
        "comment": "Extremely comfortable black running shoes! Cushioning absorbs pavement shocks effortlessly.",
        "review_date": "2024-01-12",
        "verified_purchase": True,
    },
    {
        "review_id": "REV022",
        "product_id": "PROD007",
        "reviewer_name": "Sneha Kulkarni",
        "rating": 4.5,
        "comment": "Breathable mesh upper keeps feet cool during morning 5k runs. Very lightweight.",
        "review_date": "2024-02-04",
        "verified_purchase": True,
    },
    {
        "review_id": "REV023",
        "product_id": "PROD007",
        "reviewer_name": "Rishabh Das",
        "rating": 4.5,
        "comment": "Great arch support and stylish jet black profile. Wear them to the gym and casual outings.",
        "review_date": "2024-02-28",
        "verified_purchase": True,
    },
    {
        "review_id": "REV024",
        "product_id": "PROD007",
        "reviewer_name": "Amit Saxena",
        "rating": 4.0,
        "comment": "Good grip on wet tarmac. Fits snugly, maybe order half a size up if you have wide feet.",
        "review_date": "2024-03-21",
        "verified_purchase": False,
    },

    # PROD008: Oxford Handcrafted Formal Derby Leather Shoes (Shoes)
    {
        "review_id": "REV025",
        "product_id": "PROD008",
        "reviewer_name": "Suresh Menon",
        "rating": 5.0,
        "comment": "Classic formal black leather shoes with rich gloss. Perfect for weddings and board meetings.",
        "review_date": "2024-01-18",
        "verified_purchase": True,
    },
    {
        "review_id": "REV026",
        "product_id": "PROD008",
        "reviewer_name": "Rajesh Nambiar",
        "rating": 4.5,
        "comment": "Padded inner sole makes standing all day comfortable. Excellent value from Bata.",
        "review_date": "2024-02-12",
        "verified_purchase": True,
    },
    {
        "review_id": "REV027",
        "product_id": "PROD008",
        "reviewer_name": "Abhishek Tandon",
        "rating": 4.0,
        "comment": "Sleek silhouette, high shine finish. Needs a couple of days of breaking in.",
        "review_date": "2024-03-08",
        "verified_purchase": True,
    },

    # PROD009: All-Weather Rugged Trekking Boots (Shoes)
    {
        "review_id": "REV028",
        "product_id": "PROD009",
        "reviewer_name": "Vivek Oberoi",
        "rating": 5.0,
        "comment": "Took these on a 7-day Himalayan trek. Waterproof leather and deep lug rubber sole held up flawlessly.",
        "review_date": "2024-01-25",
        "verified_purchase": True,
    },
    {
        "review_id": "REV029",
        "product_id": "PROD009",
        "reviewer_name": "Chirag Sethi",
        "rating": 4.5,
        "comment": "Outstanding ankle protection and slip resistance on loose rocks. Heavy duty Woodland beast.",
        "review_date": "2024-02-19",
        "verified_purchase": True,
    },
    {
        "review_id": "REV030",
        "product_id": "PROD009",
        "reviewer_name": "Karthik Raman",
        "rating": 4.0,
        "comment": "Extremely rugged and durable boots. Great insulation against cold ground.",
        "review_date": "2024-03-15",
        "verified_purchase": True,
    },

    # PROD010: Classic Canvas Everyday Skate Sneakers (Shoes)
    {
        "review_id": "REV031",
        "product_id": "PROD010",
        "reviewer_name": "Ayush Mishra",
        "rating": 4.5,
        "comment": "Super stylish white sneakers for college. Canvas is soft and breathable.",
        "review_date": "2024-01-05",
        "verified_purchase": True,
    },
    {
        "review_id": "REV032",
        "product_id": "PROD010",
        "reviewer_name": "Meera Krishnan",
        "rating": 4.0,
        "comment": "Unbeatable price for such versatile casual shoes. Looks great with denim skirts and shorts.",
        "review_date": "2024-01-30",
        "verified_purchase": True,
    },
    {
        "review_id": "REV033",
        "product_id": "PROD010",
        "reviewer_name": "Tushar Anand",
        "rating": 3.5,
        "comment": "Good everyday walking shoes. Sole could be slightly softer, but great value under 1200.",
        "review_date": "2024-02-24",
        "verified_purchase": False,
    },
    {
        "review_id": "REV034",
        "product_id": "PROD010",
        "reviewer_name": "Rohan Gupta",
        "rating": 4.0,
        "comment": "Clean minimalist look. Vulcanized rubber sole provides dependable traction.",
        "review_date": "2024-03-17",
        "verified_purchase": True,
    },

    # PROD011: Slip-On Memory Foam Walking Loafers (Shoes)
    {
        "review_id": "REV035",
        "product_id": "PROD011",
        "reviewer_name": "Ashok Chawla",
        "rating": 4.5,
        "comment": "Most comfortable slip-on shoes for senior citizens. Memory foam feels like walking on clouds.",
        "review_date": "2024-01-14",
        "verified_purchase": True,
    },
    {
        "review_id": "REV036",
        "product_id": "PROD011",
        "reviewer_name": "Geeta Sundaram",
        "rating": 4.0,
        "comment": "Easy to put on without bending down. Flexible sole and lightweight fabric.",
        "review_date": "2024-02-09",
        "verified_purchase": True,
    },
    {
        "review_id": "REV037",
        "product_id": "PROD011",
        "reviewer_name": "Pawan Kalyan",
        "rating": 3.5,
        "comment": "Comfortable for daily grocery trips. Hope Bata restocks this model soon.",
        "review_date": "2024-03-01",
        "verified_purchase": True,
    },

    # PROD012: Pro Velocity Breathable Cushion Road Trainers (Shoes)
    {
        "review_id": "REV038",
        "product_id": "PROD012",
        "reviewer_name": "Farhan Akhtar",
        "rating": 5.0,
        "comment": "Top-tier marathon trainers. Incredible energy return on every stride. Nike nailed this.",
        "review_date": "2024-01-27",
        "verified_purchase": True,
    },
    {
        "review_id": "REV039",
        "product_id": "PROD012",
        "reviewer_name": "Ishan Sharma",
        "rating": 4.5,
        "comment": "Breathable mesh keeps feet completely dry. Ultra comfortable black sports shoes.",
        "review_date": "2024-02-17",
        "verified_purchase": True,
    },
    {
        "review_id": "REV040",
        "product_id": "PROD012",
        "reviewer_name": "Mayank Agarwal",
        "rating": 4.5,
        "comment": "Responsive cushion foam and stylish neon accent. High performance running gear.",
        "review_date": "2024-03-11",
        "verified_purchase": True,
    },

    # PROD013: RFID Blocking Slim Bifold Leather Wallet (Wallets)
    {
        "review_id": "REV041",
        "product_id": "PROD013",
        "reviewer_name": "Shubham Dave",
        "rating": 5.0,
        "comment": "Genuinely slim front pocket wallet. Fits 8 cards and cash without bulging. Tested RFID at subway turnstile, works!",
        "review_date": "2024-01-09",
        "verified_purchase": True,
    },
    {
        "review_id": "REV042",
        "product_id": "PROD013",
        "reviewer_name": "Ankit Bhardwaj",
        "rating": 4.5,
        "comment": "Buttery soft leather texture and neat stitching. Very convenient quick-access thumb slot.",
        "review_date": "2024-01-31",
        "verified_purchase": True,
    },
    {
        "review_id": "REV043",
        "product_id": "PROD013",
        "reviewer_name": "Pranav Hegde",
        "rating": 4.5,
        "comment": "Unmatched value at 749. Matte black finish looks very executive and neat.",
        "review_date": "2024-02-21",
        "verified_purchase": True,
    },
    {
        "review_id": "REV044",
        "product_id": "PROD013",
        "reviewer_name": "Alok Srivastava",
        "rating": 4.0,
        "comment": "Compact and lightweight. Holds currency notes flat without folding multiple times.",
        "review_date": "2024-03-16",
        "verified_purchase": False,
    },

    # PROD014: Minimalist Front Pocket Aluminum Cardholder Wallet (Wallets)
    {
        "review_id": "REV045",
        "product_id": "PROD014",
        "reviewer_name": "Zayn Qureshi",
        "rating": 5.0,
        "comment": "The pop-up card ejector mechanism is so satisfying! Aerospace grade aluminum feels ultra modern.",
        "review_date": "2024-01-21",
        "verified_purchase": True,
    },
    {
        "review_id": "REV046",
        "product_id": "PROD014",
        "reviewer_name": "Tarun Bansal",
        "rating": 4.5,
        "comment": "No more bulky leather wallets. Gunmetal finish is scratch-resistant and sleek.",
        "review_date": "2024-02-16",
        "verified_purchase": True,
    },
    {
        "review_id": "REV047",
        "product_id": "PROD014",
        "reviewer_name": "Devansh Pandey",
        "rating": 4.0,
        "comment": "Cards stay securely held even when shaken upside down. High tech minimalist carry.",
        "review_date": "2024-03-10",
        "verified_purchase": True,
    },

    # PROD015: Hunter Vintage Distress Tri-Fold Leather Wallet (Wallets)
    {
        "review_id": "REV048",
        "product_id": "PROD015",
        "reviewer_name": "Brijesh Tiwari",
        "rating": 4.5,
        "comment": "Classic Woodland rugged character. Ample slots for coins, IDs, cards, and receipts.",
        "review_date": "2024-01-16",
        "verified_purchase": True,
    },
    {
        "review_id": "REV049",
        "product_id": "PROD015",
        "reviewer_name": "Girish Naidu",
        "rating": 4.0,
        "comment": "Heavy duty leather that smells authentic. A bit thick when fully loaded, but very durable.",
        "review_date": "2024-02-08",
        "verified_purchase": True,
    },
    {
        "review_id": "REV050",
        "product_id": "PROD015",
        "reviewer_name": "Harish Rawat",
        "rating": 4.5,
        "comment": "Ochre tan patina develops beautifully after couple weeks of pocket wear.",
        "review_date": "2024-03-04",
        "verified_purchase": False,
    },

    # PROD016: Executive Long Zipper Travel Clutch Wallet (Wallets)
    {
        "review_id": "REV051",
        "product_id": "PROD016",
        "reviewer_name": "Divya Pillai",
        "rating": 4.5,
        "comment": "Holds passport, boarding pass, phone, and foreign currency with total ease.",
        "review_date": "2024-01-24",
        "verified_purchase": True,
    },
    {
        "review_id": "REV052",
        "product_id": "PROD016",
        "reviewer_name": "Sunita Rao",
        "rating": 4.0,
        "comment": "Sturdy metal zipper doesn't snag. Premium leather grain texture.",
        "review_date": "2024-02-13",
        "verified_purchase": True,
    },
    {
        "review_id": "REV053",
        "product_id": "PROD016",
        "reviewer_name": "Neelam Mehra",
        "rating": 3.5,
        "comment": "Great travel accessory for business trips. Waiting for Allen Solly to restock.",
        "review_date": "2024-03-07",
        "verified_purchase": True,
    },

    # PROD017: Eco-Friendly Cork Slim Bi-Fold Wallet (Wallets)
    {
        "review_id": "REV054",
        "product_id": "PROD017",
        "reviewer_name": "Shruti Iyer",
        "rating": 5.0,
        "comment": "Surprised by how durable and water-resistant Portuguese natural cork fabric is! 100% vegan.",
        "review_date": "2024-01-11",
        "verified_purchase": True,
    },
    {
        "review_id": "REV055",
        "product_id": "PROD017",
        "reviewer_name": "Madhav Menon",
        "rating": 4.5,
        "comment": "Super lightweight, weighs almost nothing. Sustainable fashion at a reasonable price.",
        "review_date": "2024-02-05",
        "verified_purchase": True,
    },
    {
        "review_id": "REV056",
        "product_id": "PROD017",
        "reviewer_name": "Simran Kaur",
        "rating": 4.0,
        "comment": "Unique wood grain texture gets compliments every time I take it out to pay.",
        "review_date": "2024-03-18",
        "verified_purchase": True,
    },

    # PROD018: Carbon Fiber Textured Magnetic Money Clip Wallet (Wallets)
    {
        "review_id": "REV057",
        "product_id": "PROD018",
        "reviewer_name": "Yashwant Singhania",
        "rating": 4.5,
        "comment": "Strong neodymium magnet holds up to 15 currency notes tightly. Carbon fiber look is slick.",
        "review_date": "2024-01-28",
        "verified_purchase": True,
    },
    {
        "review_id": "REV058",
        "product_id": "PROD018",
        "reviewer_name": "Kailash Chand",
        "rating": 4.0,
        "comment": "Slim and comfortable in front jeans pocket. Good quality by Red Tape.",
        "review_date": "2024-02-22",
        "verified_purchase": True,
    },
    {
        "review_id": "REV059",
        "product_id": "PROD018",
        "reviewer_name": "Rohit Lal",
        "rating": 3.5,
        "comment": "Very functional. The magnetic clip has good tension and doesn't demagnetize cards.",
        "review_date": "2024-03-13",
        "verified_purchase": False,
    },

    # PROD019: Biker Faux Leather Asymmetric Zip Jacket (Jackets)
    {
        "review_id": "REV060",
        "product_id": "PROD019",
        "reviewer_name": "Kabir Mathur",
        "rating": 5.0,
        "comment": "Instant style upgrade! Heavy metallic zippers, notched lapels, and sleek black finish.",
        "review_date": "2024-01-13",
        "verified_purchase": True,
    },
    {
        "review_id": "REV061",
        "product_id": "PROD019",
        "reviewer_name": "Dhruv Sehgal",
        "rating": 4.5,
        "comment": "Looks like real leather without the cruelty or high price tag. Comfortable fit with a hoodie underneath.",
        "review_date": "2024-02-06",
        "verified_purchase": True,
    },
    {
        "review_id": "REV062",
        "product_id": "PROD019",
        "reviewer_name": "Sanjay Dutt",
        "rating": 4.5,
        "comment": "Great wind resistance on bike rides. Cut is modern and flattering.",
        "review_date": "2024-02-26",
        "verified_purchase": True,
    },
    {
        "review_id": "REV063",
        "product_id": "PROD019",
        "reviewer_name": "Ishaan Khatter",
        "rating": 4.0,
        "comment": "Solid quality biker jacket. Hardware feels heavy and premium.",
        "review_date": "2024-03-20",
        "verified_purchase": False,
    },

    # PROD020: Sherpa Lined Trucker Denim Jacket (Jackets)
    {
        "review_id": "REV064",
        "product_id": "PROD020",
        "reviewer_name": "Ranveer Bedi",
        "rating": 5.0,
        "comment": "The quintessential Levi's winter jacket. Sherpa fleece lining keeps you seriously cozy in 10-degree cold.",
        "review_date": "2024-01-20",
        "verified_purchase": True,
    },
    {
        "review_id": "REV065",
        "product_id": "PROD020",
        "reviewer_name": "Jaspreet Singh",
        "rating": 4.5,
        "comment": "Heavyweight denim outer shell with authentic stonewash fade. Timeless wardrobe staple.",
        "review_date": "2024-02-10",
        "verified_purchase": True,
    },
    {
        "review_id": "REV066",
        "product_id": "PROD020",
        "reviewer_name": "Manan Desai",
        "rating": 4.5,
        "comment": "Snug fit, insulated sleeves, and deep welt pockets. Absolutely worth the price.",
        "review_date": "2024-03-06",
        "verified_purchase": True,
    },

    # PROD021: Ultralight Packable Down Winter Puffer Jacket (Jackets)
    {
        "review_id": "REV067",
        "product_id": "PROD021",
        "reviewer_name": "Pooja Hegde",
        "rating": 5.0,
        "comment": "Packs down into a tiny travel pouch! Kept me warm during Manali trip without adding any bulk.",
        "review_date": "2024-01-07",
        "verified_purchase": True,
    },
    {
        "review_id": "REV068",
        "product_id": "PROD021",
        "reviewer_name": "Aakash Chopra",
        "rating": 4.5,
        "comment": "Excellent thermal insulation and windbreak. Allen Solly crafted a very premium down jacket.",
        "review_date": "2024-01-26",
        "verified_purchase": True,
    },
    {
        "review_id": "REV069",
        "product_id": "PROD021",
        "reviewer_name": "Ritu Varshney",
        "rating": 4.0,
        "comment": "Nice matte olive shade. Zipper runs smoothly and chin guard prevents chafing.",
        "review_date": "2024-02-15",
        "verified_purchase": False,
    },
    {
        "review_id": "REV070",
        "product_id": "PROD021",
        "reviewer_name": "Raghav Juyal",
        "rating": 4.5,
        "comment": "Featherlight yet warm. Great for morning winter jogs and casual wear.",
        "review_date": "2024-03-03",
        "verified_purchase": True,
    },

    # PROD022: All-Weather Windcheater Hooded Bomber Jacket (Jackets)
    {
        "review_id": "REV071",
        "product_id": "PROD022",
        "reviewer_name": "Bipin Rawat",
        "rating": 4.5,
        "comment": "Lightweight windproof nylon shield. Dries instantly after light drizzle. Puma quality.",
        "review_date": "2024-01-17",
        "verified_purchase": True,
    },
    {
        "review_id": "REV072",
        "product_id": "PROD022",
        "reviewer_name": "Sachin Tendulkar",
        "rating": 4.0,
        "comment": "Breathable mesh lining inside prevents sweat buildup during running.",
        "review_date": "2024-02-07",
        "verified_purchase": True,
    },
    {
        "review_id": "REV073",
        "product_id": "PROD022",
        "reviewer_name": "Vicky Kaushal",
        "rating": 3.5,
        "comment": "Sporty athletic design and elasticated cuffs. Currently out of stock, grab when available.",
        "review_date": "2024-03-01",
        "verified_purchase": True,
    },

    # PROD023: Water-Resistant Outdoor Utility Field Jacket (Jackets)
    {
        "review_id": "REV074",
        "product_id": "PROD023",
        "reviewer_name": "Abhay Deol",
        "rating": 5.0,
        "comment": "Heavyweight military grade cotton canvas with water-repellent wax coating. 6 functional utility pockets.",
        "review_date": "2024-01-23",
        "verified_purchase": True,
    },
    {
        "review_id": "REV075",
        "product_id": "PROD023",
        "reviewer_name": "Karan Johar",
        "rating": 4.5,
        "comment": "Woodland outdoor gear at its finest. Rugged, stylish, and built to survive rough wilderness.",
        "review_date": "2024-02-14",
        "verified_purchase": True,
    },
    {
        "review_id": "REV076",
        "product_id": "PROD023",
        "reviewer_name": "Gautam Gambhir",
        "rating": 4.0,
        "comment": "Adjustable waist drawstrings give a great tailored silhouette. Warm and sturdy.",
        "review_date": "2024-03-12",
        "verified_purchase": True,
    },

    # PROD024: Varsity Wool Blend Ribbed Collar Bomber Jacket (Jackets)
    {
        "review_id": "REV077",
        "product_id": "PROD024",
        "reviewer_name": "Ayushmann Khurrana",
        "rating": 5.0,
        "comment": "Classic collegiate American retro styling. Wool blend torso with vegan leather contrast sleeves.",
        "review_date": "2024-01-30",
        "verified_purchase": True,
    },
    {
        "review_id": "REV078",
        "product_id": "PROD024",
        "reviewer_name": "Kartik Aaryan",
        "rating": 4.5,
        "comment": "Heavy snap buttons and thick striped rib knit collar. Super warm and statement piece.",
        "review_date": "2024-02-25",
        "verified_purchase": True,
    },
    {
        "review_id": "REV079",
        "product_id": "PROD024",
        "reviewer_name": "Shahid Kapoor",
        "rating": 4.0,
        "comment": "Premium luxury feel from Tommy Hilfiger. Fits nicely across shoulders.",
        "review_date": "2024-03-17",
        "verified_purchase": True,
    },
    {
        "review_id": "REV080",
        "product_id": "PROD005",
        "reviewer_name": "Rajat Saxena",
        "rating": 2.0,
        "comment": "What a brilliant design! Elastic stretched out permanently after two days. Great if you enjoy pulling up your pants every five minutes.",
        "review_date": "2024-03-22",
        "verified_purchase": True,
    },
    {
        "review_id": "REV081",
        "product_id": "PROD019",
        "reviewer_name": "Karan Mehra",
        "rating": 1.5,
        "comment": "Lightning fast delivery, took only 3 weeks to arrive! And the 'genuine' faux leather feels like cheap cardboard. Truly amazing quality.",
        "review_date": "2024-03-25",
        "verified_purchase": True,
    },
    {
        "review_id": "REV082",
        "product_id": "PROD003",
        "reviewer_name": "Manav Chopra",
        "rating": 2.0,
        "comment": "Buckle is heavy as an anchor and constantly unclasps while walking. Total waste of money.",
        "review_date": "2024-03-28",
        "verified_purchase": True,
    },
]

# Raw catalogue definitions (24 realistic items across Belts, Shoes, Wallets, Jackets)
RAW_PRODUCTS: List[Dict[str, Any]] = [
    # --- Category: Belts (6 items) ---
    {
        "product_id": "PROD001",
        "name": "Classic Reversible Leather Belt",
        "category": "Belts",
        "brand": "Wildhorn",
        "description": "Crafted from 100% genuine full-grain leather, this reversible belt seamlessly switches between formal matte black and rich dark brown with a durable rotatable zinc-alloy buckle.",
        "original_price": 1999.0,
        "price": 999.0,
        "currency": "INR",
        "available_sizes": ["32", "34", "36", "38"],
        "available_colors": ["Black", "Dark Brown"],
        "stock_quantity": 15,
    },
    {
        "product_id": "PROD002",
        "name": "Formal Full-Grain Leather Dress Belt",
        "category": "Belts",
        "brand": "Woodland",
        "description": "Hand-stitched executive formal leather belt featuring an antique brushed brass buckle and beveled edge styling, ideal for corporate trousers and boardroom suits.",
        "original_price": 2499.0,
        "price": 1749.0,
        "currency": "INR",
        "available_sizes": ["30", "32", "34", "36"],
        "available_colors": ["Tan", "Black"],
        "stock_quantity": 4,  # low_stock
    },
    {
        "product_id": "PROD003",
        "name": "Heavy-Duty Casual Canvas Webbed Belt",
        "category": "Belts",
        "brand": "Levi's",
        "description": "Military-inspired tactical webbing belt crafted with high-density breathable canvas fabric and a quick-release matte steel slider buckle for rugged outdoor wear.",
        "original_price": 1299.0,
        "price": 899.0,
        "currency": "INR",
        "available_sizes": ["Free Size"],
        "available_colors": ["Olive Green", "Navy Blue", "Khaki"],
        "stock_quantity": 22,
    },
    {
        "product_id": "PROD004",
        "name": "Handcrafted Italian Leather Automatic Buckle Belt",
        "category": "Belts",
        "brand": "Tommy Hilfiger",
        "description": "Sophisticated ratchet belt featuring high-grade Italian leather and a smooth automatic slide locking buckle with no strap holes, ensuring exact micro-adjustability.",
        "original_price": 3999.0,
        "price": 2799.0,
        "currency": "INR",
        "available_sizes": ["32", "34", "36"],
        "available_colors": ["Black", "Cognac"],
        "stock_quantity": 2,  # low_stock
    },
    {
        "product_id": "PROD005",
        "name": "Braided Stretch Elastic Woven Belt",
        "category": "Belts",
        "brand": "Allen Solly",
        "description": "Ultra-flexible braided elastic belt trimmed with genuine leather tabs and nickel-free buckle, providing effortless stretch comfort for chinos and golf shorts.",
        "original_price": 1499.0,
        "price": 1049.0,
        "currency": "INR",
        "available_sizes": ["M", "L", "XL"],
        "available_colors": ["Navy", "Beige", "Charcoal"],
        "stock_quantity": 0,  # out_of_stock
    },
    {
        "product_id": "PROD006",
        "name": "Vintage Distress Leather Cowboy Belt",
        "category": "Belts",
        "brand": "Woodland",
        "description": "Sturdy oil-pullup rugged leather belt with raw distressed edge finish and engraved heavy harness buckle, engineered to pair with vintage denim.",
        "original_price": 2799.0,
        "price": 1959.0,
        "currency": "INR",
        "available_sizes": ["34", "36", "38"],
        "available_colors": ["Rustic Brown"],
        "stock_quantity": 12,
    },

    # --- Category: Shoes (6 items) ---
    {
        "product_id": "PROD007",
        "name": "Air Stride Lightweight Running Shoes",
        "category": "Shoes",
        "brand": "Puma",
        "description": "Ergonomically engineered athletic running shoes featuring responsive EVA foam midsoles, breathable mesh upper, and shock-absorbing rubber outsoles for daily running.",
        "original_price": 4499.0,
        "price": 2699.0,
        "currency": "INR",
        "available_sizes": ["7", "8", "9", "10", "11"],
        "available_colors": ["Jet Black", "Cool Grey"],
        "stock_quantity": 18,
    },
    {
        "product_id": "PROD008",
        "name": "Oxford Handcrafted Formal Derby Leather Shoes",
        "category": "Shoes",
        "brand": "Bata",
        "description": "Timeless formal derby shoes built with polished calfskin leather, comfortable cushioned insoles, and anti-skid rubber heels for long office days.",
        "original_price": 3499.0,
        "price": 2449.0,
        "currency": "INR",
        "available_sizes": ["7", "8", "9", "10"],
        "available_colors": ["Black", "Mahogany Brown"],
        "stock_quantity": 3,  # low_stock
    },
    {
        "product_id": "PROD009",
        "name": "All-Weather Rugged Trekking Boots",
        "category": "Shoes",
        "brand": "Woodland",
        "description": "Heavy-duty outdoor mountaineering boots with water-resistant nubuck leather, padded ankle collars, and deep-grooved traction soles for difficult hiking trails.",
        "original_price": 5999.0,
        "price": 4199.0,
        "currency": "INR",
        "available_sizes": ["8", "9", "10"],
        "available_colors": ["Camel Khaki", "Olive"],
        "stock_quantity": 9,
    },
    {
        "product_id": "PROD010",
        "name": "Classic Canvas Everyday Skate Sneakers",
        "category": "Shoes",
        "brand": "Red Tape",
        "description": "Low-top retro casual sneakers made with reinforced organic cotton canvas, padded footbeds, and vulcanized rubber waffle outsoles.",
        "original_price": 2999.0,
        "price": 1199.0,
        "currency": "INR",
        "available_sizes": ["6", "7", "8", "9", "10"],
        "available_colors": ["White", "Navy Blue"],
        "stock_quantity": 25,
    },
    {
        "product_id": "PROD011",
        "name": "Slip-On Memory Foam Walking Loafers",
        "category": "Shoes",
        "brand": "Bata",
        "description": "Effortless casual loafers with step-in elastic side gussets, arch-support memory foam cushioning, and ultra-flexible lightweight soles for maximum walking ease.",
        "original_price": 2299.0,
        "price": 1599.0,
        "currency": "INR",
        "available_sizes": ["7", "8", "9"],
        "available_colors": ["Charcoal", "Dark Brown"],
        "stock_quantity": 0,  # out_of_stock
    },
    {
        "product_id": "PROD012",
        "name": "Pro Velocity Breathable Cushion Road Trainers",
        "category": "Shoes",
        "brand": "Nike",
        "description": "High-performance long-distance road trainers engineered with dual-density foam technology, high-traction rubber pods, and dynamic lockdown lacing.",
        "original_price": 6999.0,
        "price": 4899.0,
        "currency": "INR",
        "available_sizes": ["8", "9", "10", "11"],
        "available_colors": ["Black & Neon", "Pure White"],
        "stock_quantity": 5,  # low_stock
    },

    # --- Category: Wallets (6 items) ---
    {
        "product_id": "PROD013",
        "name": "RFID Blocking Slim Bifold Leather Wallet",
        "category": "Wallets",
        "brand": "Wildhorn",
        "description": "Compact front-pocket bi-fold wallet featuring certified RFID blocking inner lining, 8 card slots, quick-access thumb notch, and twin currency compartments.",
        "original_price": 1499.0,
        "price": 749.0,
        "currency": "INR",
        "available_sizes": ["Standard"],
        "available_colors": ["Matte Black", "Vintage Brown"],
        "stock_quantity": 30,
    },
    {
        "product_id": "PROD014",
        "name": "Minimalist Front Pocket Aluminum Cardholder Wallet",
        "category": "Wallets",
        "brand": "Tommy Hilfiger",
        "description": "Futuristic slim metal card case constructed from anodized aerospace-grade aluminum, offering mechanical card ejection trigger and silicone cash band.",
        "original_price": 2999.0,
        "price": 1999.0,
        "currency": "INR",
        "available_sizes": ["Slim"],
        "available_colors": ["Gunmetal", "Silver"],
        "stock_quantity": 4,  # low_stock
    },
    {
        "product_id": "PROD015",
        "name": "Hunter Vintage Distress Tri-Fold Leather Wallet",
        "category": "Wallets",
        "brand": "Woodland",
        "description": "Rustic tri-fold leather wallet with coin snap pocket, transparent driver license window, and reinforced double-stitched perimeter seams.",
        "original_price": 1999.0,
        "price": 1399.0,
        "currency": "INR",
        "available_sizes": ["Standard"],
        "available_colors": ["Ochre Tan", "Dark Brown"],
        "stock_quantity": 14,
    },
    {
        "product_id": "PROD016",
        "name": "Executive Long Zipper Travel Clutch Wallet",
        "category": "Wallets",
        "brand": "Allen Solly",
        "description": "Spacious full-zip organizer wallet designed to carry boarding passes, passports, smartphones, multiple currencies, and 12 credit cards during global travel.",
        "original_price": 2499.0,
        "price": 1699.0,
        "currency": "INR",
        "available_sizes": ["Large"],
        "available_colors": ["Classic Black"],
        "stock_quantity": 0,  # out_of_stock
    },
    {
        "product_id": "PROD017",
        "name": "Eco-Friendly Cork Slim Bi-Fold Wallet",
        "category": "Wallets",
        "brand": "Wildhorn",
        "description": "Sustainable vegan bi-fold wallet made from premium harvest cork oak bark, offering natural water resistance, tear resistance, and ultra-lightweight carry.",
        "original_price": 1299.0,
        "price": 899.0,
        "currency": "INR",
        "available_sizes": ["Standard"],
        "available_colors": ["Natural Brown", "Cedar"],
        "stock_quantity": 8,
    },
    {
        "product_id": "PROD018",
        "name": "Carbon Fiber Textured Magnetic Money Clip Wallet",
        "category": "Wallets",
        "brand": "Red Tape",
        "description": "Slimline pocket wallet with high-tech carbon fiber textured exterior and a powerful neodymium magnetic clip for securing folded paper banknotes securely.",
        "original_price": 1699.0,
        "price": 999.0,
        "currency": "INR",
        "available_sizes": ["Compact"],
        "available_colors": ["Stealth Black"],
        "stock_quantity": 2,  # low_stock
    },

    # --- Category: Jackets (6 items) ---
    {
        "product_id": "PROD019",
        "name": "Biker Faux Leather Asymmetric Zip Jacket",
        "category": "Jackets",
        "brand": "H&M",
        "description": "Edgy rock-and-roll moto biker jacket featuring durable heavyweight faux leather, asymmetric front zipper closure, snap-down notch lapels, and quilted shoulder patches.",
        "original_price": 5999.0,
        "price": 3999.0,
        "currency": "INR",
        "available_sizes": ["S", "M", "L", "XL"],
        "available_colors": ["Midnight Black"],
        "stock_quantity": 11,
    },
    {
        "product_id": "PROD020",
        "name": "Sherpa Lined Trucker Denim Jacket",
        "category": "Jackets",
        "brand": "Levi's",
        "description": "Iconic vintage trucker jacket constructed from heavy 14oz non-stretch denim, lined with ultra-warm plush sherpa fleece on torso and collar with insulated quilted sleeves.",
        "original_price": 6499.0,
        "price": 4499.0,
        "currency": "INR",
        "available_sizes": ["M", "L", "XL", "XXL"],
        "available_colors": ["Stonewash Blue", "Washed Black"],
        "stock_quantity": 3,  # low_stock
    },
    {
        "product_id": "PROD021",
        "name": "Ultralight Packable Down Winter Puffer Jacket",
        "category": "Jackets",
        "brand": "Allen Solly",
        "description": "Thermal-efficient 650 fill-power duck down puffer jacket with water-resistant ripstop nylon shell that easily compresses into its own matching travel cinch bag.",
        "original_price": 4999.0,
        "price": 2999.0,
        "currency": "INR",
        "available_sizes": ["S", "M", "L", "XL"],
        "available_colors": ["Navy Blue", "Olive Green", "Burgundy"],
        "stock_quantity": 16,
    },
    {
        "product_id": "PROD022",
        "name": "All-Weather Windcheater Hooded Bomber Jacket",
        "category": "Jackets",
        "brand": "Puma",
        "description": "Sporty wind-resistant hooded jacket engineered with quick-dry nylon, breathable internal mesh lining, secure zipped pockets, and ribbed cuffs and hem.",
        "original_price": 3999.0,
        "price": 2399.0,
        "currency": "INR",
        "available_sizes": ["M", "L", "XL"],
        "available_colors": ["Steel Grey", "Black"],
        "stock_quantity": 0,  # out_of_stock
    },
    {
        "product_id": "PROD023",
        "name": "Water-Resistant Outdoor Utility Field Jacket",
        "category": "Jackets",
        "brand": "Woodland",
        "description": "Heavy military-style expedition field coat crafted with coated water-repellent canvas, concealed zip with storm flap, internal drawstring waist, and 6 cargo pockets.",
        "original_price": 7499.0,
        "price": 5249.0,
        "currency": "INR",
        "available_sizes": ["M", "L", "XL"],
        "available_colors": ["Khaki Green", "Desert Tan"],
        "stock_quantity": 7,
    },
    {
        "product_id": "PROD024",
        "name": "Varsity Wool Blend Ribbed Collar Bomber Jacket",
        "category": "Jackets",
        "brand": "Tommy Hilfiger",
        "description": "Retro collegiate varsity jacket featuring rich wool-blend body, vegan leather sleeves, striped elasticized ribbed knit trims, and snap-button front placket.",
        "original_price": 8999.0,
        "price": 6299.0,
        "currency": "INR",
        "available_sizes": ["S", "M", "L"],
        "available_colors": ["Navy & White", "Crimson & Cream"],
        "stock_quantity": 5,  # low_stock
    },
]


def _build_consistent_catalog() -> List[Dict[str, Any]]:
    """
    Compiles catalogue data ensuring complete mathematical and domain consistency:
    1. discount_percentage = round(((original_price - price) / original_price) * 100, 2)
    2. availability_status strictly mapped from stock_quantity:
       - stock_quantity > 5: in_stock
       - 1 <= stock_quantity <= 5: low_stock
       - stock_quantity == 0: out_of_stock
    3. review_count and average rating dynamically calculated from associated reviews.
    """
    # Group reviews by product_id
    reviews_by_product: Dict[str, List[Dict[str, Any]]] = {}
    for r in RAW_REVIEWS:
        pid = r["product_id"]
        reviews_by_product.setdefault(pid, []).append(r)

    processed_products: List[Dict[str, Any]] = []

    for item in RAW_PRODUCTS:
        product_copy = dict(item)
        pid = product_copy["product_id"]
        orig = product_copy["original_price"]
        curr = product_copy["price"]

        # Ensure discount percentage is mathematically exact
        if orig > 0:
            discount = round(((orig - curr) / orig) * 100, 2)
        else:
            discount = 0.0
        product_copy["discount_percentage"] = discount

        # Determine availability_status strictly from stock_quantity
        qty = product_copy["stock_quantity"]
        if qty > 5:
            status = "in_stock"
        elif 1 <= qty <= 5:
            status = "low_stock"
        else:
            status = "out_of_stock"
        product_copy["availability_status"] = status

        # Compute rating and review count from review database
        prod_reviews = reviews_by_product.get(pid, [])
        review_count = len(prod_reviews)
        if review_count > 0:
            avg_rating = round(sum(rev["rating"] for rev in prod_reviews) / review_count, 1)
        else:
            avg_rating = 5.0
        product_copy["rating"] = avg_rating
        product_copy["review_count"] = review_count

        processed_products.append(product_copy)

    return processed_products


# Global in-memory datasets
PRODUCTS: List[Dict[str, Any]] = _build_consistent_catalog()
REVIEWS: List[Dict[str, Any]] = list(RAW_REVIEWS)

# Lookups for O(1) retrieval
PRODUCTS_BY_ID: Dict[str, Dict[str, Any]] = {p["product_id"]: p for p in PRODUCTS}
REVIEWS_BY_PRODUCT_ID: Dict[str, List[Dict[str, Any]]] = {}
for r in REVIEWS:
    REVIEWS_BY_PRODUCT_ID.setdefault(r["product_id"], []).append(r)
