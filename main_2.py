import json
import pathlib
from typing import List, Union

from fastapi import FastAPI, Response
from sqlmodel import Session, select

from models import Track
from database import TrackModel, engine

app = FastAPI()

data = []

@app.on_event("startup")
async def startup_event():
    DATAFILE = pathlib.Path() / 'data' / 'tracks.json'
    session = Session(engine)

    stmt = select(TrackModel)
    result = session.exec(stmt).first()

    if result is None:
        with open(DATAFILE, 'r') as f:
            tracks = json.load(f)
            for track in tracks:
                session.add(TrackModel(**track))
        session.commit()
    session.close()
    # with open(datapath, 'r') as f:
    #     tracks = json.load(f)
    #     for track in tracks:
    #         data.append(Track(**track).dict())


@app.get('/tracks/', response_model=List[Track])
def tracks():
    # select * from
    with Session(engine) as session:
        stmt = select(TrackModel)
        result = session.exec(stmt).all()
        return result

@app.get('/tracks/{track_id}', response_model=Union[Track, str])
def track(track_id: int, response: Response):
    # find the track with the given ID, or None if it does not exists
    track = None
    for t in data:
        if t['id'] == track_id:
            track = t
            break

    if track is None:
        response.status_code = 404
        return "Track not found"
    return track

@app.post('/tracks/', response_model=Track, status_code=201)
def create_track(track: Track):
    track_dict = track.dict()
    track_dict['id'] = max(data, key=lambda x: x['id']).get('id') + 1
    data.append(track_dict)
    return track_dict


@app.put('/tracks/{track_id}/', response_model=Union[Track, str])
def track(track_id: int, updated_track: Track, response: Response):
    # find the track with the given ID, or None if it does not exists
    track = None
    for t in data:
        if t['id'] == track_id:
            track = t
            break

    if track is None:
        response.status_code = 404
        return "Track not found"
    
    for key, val in updated_track.dict().items():
        if key != 'id':
            track[key] = val
    return track


@app.delete('/tracks/{track_id}/')
def track(track_id: int, response: Response):
    # find the track with the given ID, or None if it does not exists
    track_index = None
    for idx, t in enumerate(data):
        if t['id'] == track_id:
            track_index = idx
            break

    if track_index is None:
        response.status_code = 404
        return "Track not found"
    
    del data[track_index]

    return Response(status_code=200)

@app.get('/')
def health_check():
    return {'Hello':'World'}
