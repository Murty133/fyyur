from app import Artist, Venue, Show, db

data = [
    Show(
        artist_id=1,
        venue_id=1,
        start_time="2019-05-21T21:30:00.000Z"
    ),
    Show(
        artist_id=2,
        venue_id=3,
        start_time="2019-06-15T23:00:00.000Z"
    ),
    Show(
        artist_id=3,
        venue_id=3,
        start_time="2035-04-01T20:00:00.000Z"
    ),
    Show(
        artist_id=3,
        venue_id=3,
        start_time="2035-04-08T20:00:00.000Z"
    ),
    Show(
        artist_id=3,
        venue_id=3,
        start_time="2035-04-015T20:00:00.000Z"
    )
]

for d in data:
    db.session.add(d)
db.session.commit()