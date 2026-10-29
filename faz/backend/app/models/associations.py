# app/models/associations.py
from sqlalchemy import Table, Column, ForeignKey
from app.database import db

news_tags = Table(
    'news_tags',
    db.metadata,          # <-- changed from Base.metadata
    Column('news_id', ForeignKey('news.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)