from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time



class Bases(BaseModel):
    id:Optional[int] = None
    name:str
    chaves:str
    user_id : int 


    class Config:
        from_attributes = True

class Infos(BaseModel):
    id:Optional[int] = None
    infos:str
    base_id:int
    
    class Config:
        from_attributes = True



