from app.database import SessionLocal
from app.models import News, Video, Gallery, GalleryImage, User, Tag, news_tags
from datetime import datetime, timedelta
import random

db = SessionLocal()

# Get admin user
admin = db.query(User).filter(User.username == "admin").first()
if not admin:
    print("Admin user not found! Run init_db.py first.")
    exit()

print("=" * 60)
print("Inserting Media Data (News, Videos, Galleries)")
print("=" * 60)

# ============ NEWS DATA (30 items across 3 years) ============
news_items = [
    # 2024 News
    {"title": "Chipolopolo Begin World Cup Qualifiers with Convincing Win", "content": "The Zambia national football team started their FIFA World Cup qualifying campaign on a high note, defeating their opponents 3-0 at the National Heroes Stadium in Lusaka. Patson Daka opened the scoring in the 23rd minute, followed by goals from Fashion Sakala and an own goal. Coach Avram Grant praised the team's discipline and tactical awareness.", "excerpt": "Zambia's Chipolopolo started their FIFA World Cup qualifying campaign with an emphatic 3-0 victory.", "featured_image": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800", "published_at": datetime.now() - timedelta(days=2)},
    {"title": "Copper Queens Make History, Qualify for WAFCON Semifinals", "content": "The Zambia Women's National Team, the Copper Queens, have made history by reaching the WAFCON semifinals for the first time. Captain Barbra Banda led from the front with two spectacular goals in the quarterfinal match. The team displayed remarkable resilience and tactical brilliance throughout the tournament.", "excerpt": "Copper Queens create history by reaching WAFCON semifinals for the first time.", "featured_image": "https://images.unsplash.com/photo-1520437358207-323b43b50729?w=800", "published_at": datetime.now() - timedelta(days=5)},
    {"title": "ZESCO United Clinch Record-Extending League Title", "content": "ZESCO United have secured their 10th Super League title after a dominant season. The Ndola-based giants finished the campaign with a 15-point lead over second place. Coach Numba Mumamba credited the team's consistency and depth for the achievement.", "excerpt": "ZESCO United celebrate their record-extending 10th Super League title.", "featured_image": "https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9?w=800", "published_at": datetime.now() - timedelta(days=10)},
    {"title": "Patson Daka Named Zambian Footballer of the Year", "content": "Leicester City striker Patson Daka has been crowned Zambian Footballer of the Year for the third consecutive year. The 26-year-old scored 15 goals for his club and contributed crucial strikes for the national team.", "excerpt": "Patson Daka wins Zambian Footballer of the Year for third straight year.", "featured_image": "https://images.unsplash.com/photo-1519643381401-22c77e60520e?w=800", "published_at": datetime.now() - timedelta(days=15)},
    {"title": "FAZ Announces Major Sponsorship Deal", "content": "The Football Association of Zambia has announced a landmark sponsorship agreement with a leading global brand. The multi-year deal will inject significant funds into grassroots development, youth academies, and women's football.", "excerpt": "FAZ secures landmark multi-year sponsorship deal.", "featured_image": "https://images.unsplash.com/photo-1522778526097-ce0a22ceb253?w=800", "published_at": datetime.now() - timedelta(days=20)},
    {"title": "Barbra Banda Scores Hat-Trick in NWSL Match", "content": "Copper Queens captain Barbra Banda continued her red-hot form in the NWSL, scoring a brilliant hat-trick for Orlando Pride. The Zambian international has now scored 10 goals in her last 8 matches.", "excerpt": "Barbra Banda scores sensational hat-trick in NWSL.", "featured_image": "https://images.unsplash.com/photo-1499092346589-b9b6be3e94b2?w=800", "published_at": datetime.now() - timedelta(days=25)},
    {"title": "Nkana FC Appoints New Head Coach", "content": "Nkana FC has announced the appointment of a new head coach ahead of the new season. The experienced tactician brings a wealth of knowledge from his time in South African football.", "excerpt": "Nkana FC appoints experienced new head coach.", "featured_image": "https://images.unsplash.com/photo-1560087637-69c1bd0232c2?w=800", "published_at": datetime.now() - timedelta(days=30)},
    {"title": "Zambia U-20 Team Qualifies for AFCON Finals", "content": "The Zambia Under-20 national team has secured qualification for the AFCON U-20 finals after a thrilling 2-1 aggregate victory. The young Chipolopolo showed remarkable composure in the second leg.", "excerpt": "Zambia U-20 national team books ticket to AFCON U-20 finals.", "featured_image": "https://images.unsplash.com/photo-1511886929837-354d827aae26?w=800", "published_at": datetime.now() - timedelta(days=35)},
    {"title": "Power Dynamos Unveil New Training Facility", "content": "Power Dynamos have opened a new training facility at their Arthur Davies Stadium complex. The facility includes three pitches, a gymnasium, medical center, and players' lounge.", "excerpt": "Power Dynamos unveil new state-of-the-art training facility.", "featured_image": "https://images.unsplash.com/photo-1521537634581-0fced2ded2e9?w=800", "published_at": datetime.now() - timedelta(days=40)},
    {"title": "Women's Super League Attracts Record Crowds", "content": "The Women's Super League has witnessed record attendances this season, with over 5,000 fans attending the Lusaka derby. The growing popularity reflects increased investment and media coverage.", "excerpt": "Women's Super League attracts record crowds.", "featured_image": "https://images.unsplash.com/photo-1579954115545-a95591f28bfc?w=800", "published_at": datetime.now() - timedelta(days=45)},
    
    # 2025 News
    {"title": "Chipolopolo Drops in FIFA Rankings", "content": "Zambia's national team has dropped three places in the latest FIFA World Rankings following mixed results in recent friendlies. The team now sits at 88th globally and 15th in Africa.", "excerpt": "Chipolopolo drops in FIFA rankings.", "featured_image": "https://images.unsplash.com/photo-1575361203360-fb1a6c3bd172?w=800", "published_at": datetime.now() - timedelta(days=60)},
    {"title": "Green Eagles FC Pull Off Major Upset", "content": "Underdogs Green Eagles FC pulled off a stunning 2-1 victory against defending champions in the Super League. The Kabwe-based side showed remarkable determination, scoring the winner in the 89th minute.", "excerpt": "Green Eagles FC pull off major upset.", "featured_image": "https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=800", "published_at": datetime.now() - timedelta(days=65)},
    {"title": "Lusaka Derby Ends in Dramatic Draw", "content": "The highly anticipated Lusaka derby between ZANACO FC and Lusaka Dynamos ended in a 2-2 draw with both teams exchanging goals in an action-packed second half.", "excerpt": "Lusaka derby ends in dramatic 2-2 draw.", "featured_image": "https://images.unsplash.com/photo-1522778119026-d647f0596c67?w=800", "published_at": datetime.now() - timedelta(days=70)},
    {"title": "Futsal National Team Prepares for Championship", "content": "The Zambia Futsal national team has begun residential camp ahead of the COSAFA Futsal Championship. The squad features a mix of experienced players and exciting youngsters.", "excerpt": "Zambia Futsal national team intensifies preparations.", "featured_image": "https://images.unsplash.com/photo-1518609878373-06d740f60d1b?w=800", "published_at": datetime.now() - timedelta(days=75)},
    {"title": "Promising Youngster Trials with European Club", "content": "A 17-year-old Zambian prospect has been invited for a two-week trial with a top European club. The attacking midfielder impressed scouts during the U-17 AFCON qualifiers.", "excerpt": "Zambian teenage sensation secures trial opportunity.", "featured_image": "https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=800", "published_at": datetime.now() - timedelta(days=80)},
    
    # 2026 News
    {"title": "Referee Janny Sikazwe Retires", "content": "Legendary Zambian referee Janny Sikazwe has announced his retirement after 20 years of distinguished service. The 45-year-old officiated at two FIFA World Cups and multiple AFCON tournaments.", "excerpt": "Zambian referee Janny Sikazwe retires after illustrious career.", "featured_image": "https://images.unsplash.com/photo-1533401567289-6b81ad8e3bc0?w=800", "published_at": datetime.now() - timedelta(days=90)},
    {"title": "ABSA Cup Quarterfinal Draw Conducted", "content": "The draw for the ABSA Cup quarterfinals has been conducted, setting up exciting matchups. The remaining eight teams include four Super League sides and lower division surprises.", "excerpt": "ABSA Cup quarterfinal draw sets up exciting matchups.", "featured_image": "https://images.unsplash.com/photo-1511886929837-354d827aae26?w=800", "published_at": datetime.now() - timedelta(days=95)},
    {"title": "FAZ Launches Grassroots Development Program", "content": "FAZ has launched a comprehensive grassroots development program targeting 10,000 children across all provinces. The initiative includes coach education, equipment distribution, and talent identification.", "excerpt": "FAZ launches ambitious grassroots development program.", "featured_image": "https://images.unsplash.com/photo-1519923041107-e4dcf9a95636?w=800", "published_at": datetime.now() - timedelta(days=100)},
    {"title": "Copper Queens Captain Inspires Young Girls", "content": "Copper Queens captain Barbra Banda hosted a football clinic for 200 young girls in Lusaka, sharing her journey and encouraging participation in sports.", "excerpt": "Copper Queens captain Barbra Banda inspires young girls.", "featured_image": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800", "published_at": datetime.now() - timedelta(days=105)},
    {"title": "Mufulira Wanderers Secure Survival", "content": "Mufulira Wanderers secured their Super League survival with a dramatic 94th-minute winner against relegation rivals. The goal sparked wild celebrations at Shinde Stadium.", "excerpt": "Mufulira Wanderers escape relegation.", "featured_image": "https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9?w=800", "published_at": datetime.now() - timedelta(days=110)},
    {"title": "Chipolopolo Captain Addresses Media", "content": "Chipolopolo captain addressed the media ahead of crucial World Cup qualifiers, expressing confidence in the team's preparation. He called on fans to rally behind the squad.", "excerpt": "Chipolopolo captain calls for fan support.", "featured_image": "https://images.unsplash.com/photo-1522778526097-ce0a22ceb253?w=800", "published_at": datetime.now() - timedelta(days=115)},
    {"title": "FAZ Partners with Tech Company", "content": "FAZ has announced a partnership with a leading technology company to digitize football administration. The project includes electronic match reporting and player registration.", "excerpt": "FAZ partners with technology company.", "featured_image": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800", "published_at": datetime.now() - timedelta(days=120)},
    {"title": "Former Referee Appointed as Match Commissioner", "content": "Former international referee has been appointed as a match commissioner by FAZ. The experienced official will oversee Super League matches and ensure compliance.", "excerpt": "Former FIFA referee takes up match commissioner role.", "featured_image": "https://images.unsplash.com/photo-1533401567289-6b81ad8e3bc0?w=800", "published_at": datetime.now() - timedelta(days=125)},
    {"title": "Zambia to Host Regional Youth Tournament", "content": "Zambia has been selected to host the COSAFA U-17 Youth Championship next year. The tournament will take place in Lusaka and Ndola, featuring eight Southern African nations.", "excerpt": "Zambia selected to host COSAFA U-17 Youth Championship.", "featured_image": "https://images.unsplash.com/photo-1518609878373-06d740f60d1b?w=800", "published_at": datetime.now() - timedelta(days=130)},
    {"title": "Red Arrows Maintain Perfect Start", "content": "Red Arrows have won their first five matches of the Super League season, establishing an early lead at the top of the table. The air force side has conceded only two goals.", "excerpt": "Red Arrows maintain perfect start to Super League season.", "featured_image": "https://images.unsplash.com/photo-1522778119026-d647f0596c67?w=800", "published_at": datetime.now() - timedelta(days=135)},
    {"title": "Charity Shield Raises Funds", "content": "The annual Charity Shield match raised over 500,000 Kwacha for community development projects. The match between league champions and cup winners drew a large crowd.", "excerpt": "Charity Shield raises over 500,000 Kwacha for community projects.", "featured_image": "https://images.unsplash.com/photo-1521537634581-0fced2ded2e9?w=800", "published_at": datetime.now() - timedelta(days=140)},
    {"title": "Young Chipolopolo Ready for AFCON", "content": "The Under-20 national team is ready for the challenge of the upcoming AFCON tournament, with coach expressing confidence. The team has undergone intensive training.", "excerpt": "Young Chipolopolo confident ahead of AFCON U-20 tournament.", "featured_image": "https://images.unsplash.com/photo-1511886929837-354d827aae26?w=800", "published_at": datetime.now() - timedelta(days=145)},
    {"title": "Nkana Legend Honored by Club", "content": "Former Nkana FC captain was honored by the club for his 15 years of service and contribution to Zambian football. A testimonial match was organized between Nkana legends.", "excerpt": "Nkana FC honors club legend.", "featured_image": "https://images.unsplash.com/photo-1560087637-69c1bd0232c2?w=800", "published_at": datetime.now() - timedelta(days=150)},
]

news_count = 0
for item in news_items:
    slug = item["title"].lower().replace(" ", "-").replace("'", "").replace("?", "")
    # Check if exists
    existing = db.query(News).filter(News.slug == slug).first()
    if not existing:
        news = News(
            title=item["title"],
            slug=slug,
            content=item["content"],
            excerpt=item["excerpt"],
            featured_image=item["featured_image"],
            author_id=admin.id,
            published_at=item["published_at"],
            is_published=True
        )
        db.add(news)
        news_count += 1

db.commit()
print(f"✅ Added {news_count} news articles")

# ============ VIDEOS ============
videos = [
    {"title": "Chipolopolo Highlights - World Cup Qualifier", "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "description": "Highlights from Zambia's World Cup qualifying match", "duration": "4:32", "published_at": datetime.now() - timedelta(days=10)},
    {"title": "Copper Queens Interview - Barbra Banda", "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "description": "Exclusive interview with Copper Queens captain", "duration": "8:15", "published_at": datetime.now() - timedelta(days=20)},
    {"title": "Super League Match of the Week", "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "description": "Full match highlights from the Super League", "duration": "6:45", "published_at": datetime.now() - timedelta(days=30)},
    {"title": "FAZ Technical Workshop", "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "description": "Coaching development workshop highlights", "duration": "3:50", "published_at": datetime.now() - timedelta(days=45)},
    {"title": "Youth Football Development Program", "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "description": "Showcasing grassroots football initiatives", "duration": "5:20", "published_at": datetime.now() - timedelta(days=60)},
]

video_count = 0
for video_data in videos:
    youtube_id = video_data["youtube_url"].split("v=")[-1].split("&")[0]
    existing = db.query(Video).filter(Video.youtube_id == youtube_id).first()
    if not existing:
        video = Video(
            title=video_data["title"],
            youtube_url=video_data["youtube_url"],
            youtube_id=youtube_id,
            thumbnail_url=f"https://img.youtube.com/vi/{youtube_id}/hqdefault.jpg",
            description=video_data["description"],
            duration=video_data["duration"],
            published_at=video_data["published_at"],
            is_published=True
        )
        db.add(video)
        video_count += 1

db.commit()
print(f"✅ Added {video_count} videos")

# ============ GALLERIES ============
galleries = [
    {"title": "Chipolopolo vs Ghana Match Day", "description": "Photos from the World Cup qualifier match", "cover_image": "https://images.unsplash.com/photo-1522778119026-d647f0596c67?w=800", "event_date": datetime.now().date() - timedelta(days=15)},
    {"title": "Copper Queens Training Session", "description": "Behind the scenes at Copper Queens training camp", "cover_image": "https://images.unsplash.com/photo-1520437358207-323b43b50729?w=800", "event_date": datetime.now().date() - timedelta(days=25)},
    {"title": "Super League Awards Gala", "description": "Annual Super League awards ceremony", "cover_image": "https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=800", "event_date": datetime.now().date() - timedelta(days=40)},
    {"title": "FAZ Congress 2025", "description": "Annual General Meeting of FAZ", "cover_image": "https://images.unsplash.com/photo-1521537634581-0fced2ded2e9?w=800", "event_date": datetime.now().date() - timedelta(days=55)},
    {"title": "Youth Football Festival", "description": "Annual youth football celebration event", "cover_image": "https://images.unsplash.com/photo-1518609878373-06d740f60d1b?w=800", "event_date": datetime.now().date() - timedelta(days=70)},
]

gallery_count = 0
for gallery_data in galleries:
    gallery = Gallery(
        title=gallery_data["title"],
        description=gallery_data["description"],
        cover_image=gallery_data["cover_image"],
        event_date=gallery_data["event_date"],
        is_published=True
    )
    db.add(gallery)
    db.flush()
    
    # Add sample images for each gallery
    for i in range(1, 4):
        image = GalleryImage(
            gallery_id=gallery.id,
            image_url=f"https://images.unsplash.com/photo-1522778119026-d647f0596c67?w=400&img={i}",
            caption=f"Photo {i} from {gallery_data['title']}",
            order=i
        )
        db.add(image)
    gallery_count += 1

db.commit()
print(f"✅ Added {gallery_count} galleries with images")

print("\n" + "=" * 60)
print("🎉 MEDIA DATA INSERTION COMPLETE! 🎉")
print("=" * 60)
print(f"Summary:")
print(f"  - News articles: {news_count}")
print(f"  - Videos: {video_count}")
print(f"  - Galleries: {gallery_count}")

db.close()