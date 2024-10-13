from app import app
from models import db, Guests, Episodes, Appearances, appearances_tables
from faker import Faker
import random

with app.app_context():
    Guests.query.delete()
    Episodes.query.delete()
    Appearances.query.delete()
    db.session.query(appearances_tables).delete()

    faker = Faker()
    Faker.seed(0)

    episodes = []

    for x in range(30):
        episode = Episodes(
            date = faker.date(),
            number = random.randint(0,100),
        )

        db.session.add(episode)
        episodes.append(episode)
    
    db.session.add_all(episodes)

    guests = []

    for _ in range(50):
        guest = Guests(
            name = faker.name(),
            occupation = faker.job(),
        )

        db.session.add(guest)
        guests.append(guest)

    db.session.add_all(guests)

    appearances = []

    for episode in episodes:
        for _ in range(random.randint(0,5)):
            guest = random.choice(guests)
            if episode not in guest.episodes:
                guest.episodes.append(episode)

            appearance = Appearances(
                rating = random.randint(0,5),
                guest = guest,
                episode = episode,
            )

            db.session.add(appearance)

            appearances.append(appearance)

    db.session.add_all(appearances)
    db.session.commit()