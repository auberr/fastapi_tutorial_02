import json
import pathlib
from typing import List, Union

from fastapi import FastAPI, Response, Depends, HTTPException, Query
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

def get_session():
    with Session(engine) as session:
        yield session

@app.get('/tracks/', response_model=List[Track])
def tracks(session: Session = Depends(get_session)):
    # select * from
    stmt = select(TrackModel)
    result = session.exec(stmt).all()
    return result

@app.get('/tracks/{track_id}', response_model=Union[Track, str])
def track(track_id: int, response: Response, session: Session = Depends(get_session)):
    # find the track with the given ID, or None if it does not exists
    track = session.get(TrackModel, track_id)
    if track is None:
        response.status_code = 404
        return "Track not found"
    return track

@app.post('/tracks/', response_model=Track, status_code=201)
def create_track(track: TrackModel, session: Session = Depends(get_session)):
    session.add(track)
    session.commit()
    session.refresh(track)
    return track
    


@app.put('/tracks/{track_id}/', response_model=Union[Track, str])
def track(track_id: int, updated_track: Track, response: Response, session: Session = Depends(get_session)):
    # find the track with the given ID, or None if it does not exists
    track = session.get(TrackModel, track_id)

    if track is None:
        response.status_code = 404
        return "Track not found"
    
    track_dict=updated_track.dict(exclude_unset=True)
    for key, val in track_dict.items():
        setattr(track, key, val)
    
    session.add(track)
    session.commit()
    session.refresh(track)
    return track


@app.delete('/tracks/{track_id}/')
def delete_track(track_id: int, response: Response, session: Session = Depends(get_session)):
    # find the track with the given ID, or None if it does not exists
    track = session.get(TrackModel, track_id)

    if track is None:
        response.status_code = 404
        return "Track not found"
    
    session.delete(track)
    session.commit()

    return Response(status_code=200)

@app.get('/')
def health_check():
    return {'Hello':'World'}
