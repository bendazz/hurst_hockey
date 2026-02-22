from typing import Optional
from sqlmodel import SQLModel, Field


class Bio(SQLModel, table=True):
	Number: Optional[int] = Field(default=None, description="Jersey number")
	Player: Optional[str] = Field(default=None, description="Full name")
	FirstName: str = Field(primary_key=True)
	LastName: str = Field(primary_key=True)
	Position: Optional[str] = None
	Height: Optional[str] = None
	Weight: Optional[str] = None
	Class: Optional[str] = None
	Hometown: Optional[str] = None
	HighSchool: Optional[str] = None

class Stats(SQLModel, table=True):
	Number: Optional[int] = Field(default=None, description="Jersey number")
	FirstName: str = Field(primary_key=True, foreign_key="bio.FirstName")
	LastName: str = Field(primary_key=True, foreign_key="bio.LastName")
	GP: Optional[int] = None
	G: Optional[int] = None
	A: Optional[int] = None
	PTS: Optional[int] = None
	SH: Optional[int] = None
	SH_PCT: Optional[float] = None
	plus_minus: Optional[int] = None
	PPG: Optional[int] = None
	SHG: Optional[int] = None
	FG: Optional[int] = None
	GWG: Optional[int] = None
	GTG: Optional[int] = None
	OTG: Optional[int] = None
	HTG: Optional[int] = None
	UAG: Optional[int] = None
	PN_PIM: Optional[str] = Field(default=None, description="Penalty - PIM (raw)")
	MIN: Optional[int] = None
	MAJ: Optional[int] = None
	OTH: Optional[int] = None
	BLK: Optional[int] = None