# add_missing_ticket_types.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app
from app.database import db
from app.models import Match, TicketType

app = create_app()
with app.app_context():
    matches = Match.query.filter_by(is_ticketed=True).all()
    for match in matches:
        if not match.ticket_types:
            print(f"Adding ticket types to {match.home_team} vs {match.away_team}")
            ticket_types = [
                {"name": "Standard", "price": 50.00, "capacity": 100},
                {"name": "VIP", "price": 150.00, "capacity": 20},
                {"name": "VVIP", "price": 300.00, "capacity": 5},
            ]
            for tt_data in ticket_types:
                tt = TicketType(
                    match_id=match.id,
                    name=tt_data['name'],
                    price=tt_data['price'],
                    capacity=tt_data['capacity']
                )
                db.session.add(tt)
            db.session.commit()
    print("Done.")