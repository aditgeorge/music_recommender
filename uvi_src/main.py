from typing import Optional
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
import pymongo
import json
import yaml
app = FastAPI()
myclient = pymongo.MongoClient("mongodb://mongo-server:27017")
mydb = myclient["mydatabase"]
v2db=myclient["v2database"]
v2col=v2db["user"]
mycol = mydb["myusers"]
song_meta=[{}]
with open("song_meta.json") as f:
    song_meta=json.load(f)
topsongs=[144663, 116573, 357367, 366786, 654757, 133143, 349492, 675115, 463173, 42155]

@app.put("/users")
async def put_users(uid:str, passwd:str):
    chk = mycol.find_one({"cid":uid})
    if(chk is None):
        mycol.insert_one({"cid":uid,"passwd":passwd,"name":"", "playlist":[],"rec_songs":topsongs})
        return {"result":"SUCCESS"}
    else:
        a = mycol.update_one({"cid":uid},{"$set":{"passwd":passwd}})
        chk2 = mycol.find_one({"cid":uid})
        if(chk2 is not None):
            return {"result":"SUCCESS"}
        else:
            return {"result": "FAILED"}

@app.delete("/users")
async def del_users(uid:str):
    chk = mycol.find_one({"cid":uid})
    if (chk is not None):
        mycol.delete_one({"cid":uid})
        return {"result": "SUCCESS"}
    else:
        return {"result": "FAILED"}

@app.get("/users")
async def get_users():
    userlist = []
    iterfind = mycol.find({},{"_id":0})
    for x in iterfind:
        userlist.append(x)
    return userlist

@app.get("/users/_count_")
async def get_count():
    countd=mycol.count()
    return {"count": countd}

@app.put("/users/{userid}/playlist/{songid}")
async def put_song(userid:str, songid:str):
    chk = mycol.find_one({"cid":userid})
    if(chk is not None):
        newplaylist=chk.get("playlist")
        songexists=False
        for d in song_meta:
            if (str(d["id"])==songid):
                songexists=True
        if(songexists):
            if songid in newplaylist:
                return {"result":"FAILED"}
            else:
                newplaylist.append(songid)
                a = mycol.update_one({"cid":userid},{"$set":{"playlist":newplaylist}})
                return {"result":"SUCCESS"}
        else:
            return {"result":"FAILED"}
    else:
        return {"result": "FAILED"}

@app.get("/users/{userid}/recommendations")
async def get_usersongs(userid:str):
    user=mycol.find_one({"cid":userid},{"_id":0,"passwd":0,"playlist":0})
    if (user is not None):
        result={}
        result["uid"]=user["cid"]
        result["songs"]=user["rec_songs"]
        return result
    else:
        return {"result":"FAILED"}

@app.get("/users/{userid}/playlist")
async def get_usersongs(userid:str):
    user=mycol.find_one({"cid":userid},{"_id":0,"passwd":0,"rec_songs":0})
    if (user is not None):
        result={}
        result["uid"]=user["cid"]
        result["playlist"]=user["playlist"]
        return result
    else:
        return {"result":"FAILED"}

# V2 Code-----------------------------------------------------
@app.post("/v2/customers/{userid}")
async def post_users2(userid:str):
    chk = mycol.find_one({"cid":userid})
    if(chk is None):
        mycol.insert_one({"cid":userid,"passwd":"","name":"", "playlist":[],"rec_songs":topsongs})
        chk2=mycol.find_one({"cid":userid})
        return {"result":"SUCCESS","customer ID":chk2["cid"]}
    else:
        return {"result": "FAILED", "message":"duplicate "+userid}

@app.put("/v2/customers/{userid}")
async def put_users2(userid:str, name:str):
    chk = mycol.find_one({"cid":userid})
    if(chk is not None):
        mycol.update_one({"cid":userid},{"$set":{"cid":userid,"name":name}})
        chk2 = mycol.find_one({"cid":userid})
        if(chk2 is not None):
            return {"result":"SUCCESS","customer ID":chk2["cid"],"name":chk2["name"]}
        else:
            return {"result": "FAILED","message":"Error in Update function"}
    else:
        return {"result": "FAILED", "message":userid+" not found"}

@app.get("/v2/customers/{userid}")
async def get_user2(userid:str):
    chk = mycol.find_one({"cid":userid})
    if(chk is not None):
        return {"result":"SUCCESS","customer ID":chk["cid"],"name":chk["name"]}
    else:
        return {"result":"FAILED", "message":userid+" not found"}

@app.delete("/v2/customers/{userid}")
async def del_user2(userid:str):
    chk = mycol.find_one({"cid":userid})
    if (chk is not None):
        mycol.delete_one({"cid":userid})
        return {"result": "SUCCESS","customer ID":userid}
    else:
        return {"result": "FAILED", "message":userid+" not found"}

@app.post("/v2/customers/{userid}/listened/{songid}")
async def post_song2(userid:str, songid:str):
    chk=mycol.find_one({"cid":userid})
    if(chk is not None):
        song_exists=False
        for d in song_meta:
            if(str(d["id"])==songid):
                song_exists=True
        if(song_exists):
            newplaylist=chk["playlist"]
            if(songid in newplaylist):
                return {"result":"FAILED","message":songid+ " already exists in playlist of "+userid}
            else:
                newplaylist.append(songid)
                mycol.update_one({"cid":userid},{"$set":{"playlist":newplaylist}})
                chk2=mycol.find_one({"cid":userid})
                return {"result":"SUCCESS","customer":chk2["cid"],"songs":chk2["playlist"]}
        else:
            return {"result":"FAILED", "message":songid+" doesn't exist in song_meta.json"}
    else:
        return {"result":"FAILED","message":userid+" not found"}

@app.get("/v2/customers/{userid}/listened")
async def get_songs2(userid:str):
    chk=mycol.find_one({"cid":userid})
    if(chk is not None):
        return {"customer":chk["cid"], "songs":chk["playlist"]}
    else:
        return {"result":"FAILED", "message":userid+ " not found"}

@app.delete("/v2/customers/{userid}/listened/{songid}")
async def del_song2(userid:str, songid:str):
    chk=mycol.find_one({"cid":userid})
    if(chk is not None):
        newplaylist=chk["playlist"]
        if(songid in newplaylist):
            newplaylist.remove(songid)
            mycol.update_one({"cid":userid},{"$set":{"playlist":newplaylist}})
            chk2=mycol.find_one({"cid":userid})
            return {"result":"SUCCESS", "customer":chk2["cid"],"songs":chk2["playlist"]}
        else:
            return {"result":"FAILED", "message": songid+" not found in "+userid+"'s playlist"}
    else:
        return {"result":"FAILED", "message":userid+" not found"}

@app.get("/v2/songs/{songid}")
async def get_song2(songid:str):
    result=None
    for d in song_meta:
        if(str(d["id"])==songid):
            result=d

    if(result is not None):
        return {"song_id":result["id"],"album_id":result["album_id"],"artists":result["artist_id_basket"]}
    else:
        return {"result":"FAILED", "message": songid+" not found in song_meta.json"}

@app.get("/v2/customers/{userid}/suggestion")
async def get_suggestions2(userid:str):
    chk=mycol.find_one({"cid":userid})
    if (chk is not None):
        return {"customer":chk["cid"], "songs":chk["rec_songs"]}
    else:
        return {"result":"FAILED", "message":userid+" not found"}
@app.get("/v2/")
async def get_manual():
    with open("api_manual.yaml") as f:
        api_manual=yaml.safe_load(f)
        return api_manual