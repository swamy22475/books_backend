from pydantic import BaseModel, Field
from typing import Optional, List, Union

class AcademicSectionBase(BaseModel):
    name: str
    class_id: int = Field(alias="classId")
    category: Optional[str] = None
    capacity: Optional[Union[int, str]] = None
    teacher_id: Optional[Union[int, str]] = Field(None, alias="teacherId")
    note: Optional[str] = None
    academic_status: Optional[str] = Field("Active", alias="academicStatus")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

class AcademicSectionCreate(AcademicSectionBase):
    pass

class AcademicSectionUpdate(BaseModel):
    name: Optional[str] = None
    class_id: Optional[int] = Field(None, alias="classId")
    category: Optional[str] = None
    capacity: Optional[Union[int, str]] = None
    teacher_id: Optional[Union[int, str]] = Field(None, alias="teacherId")
    note: Optional[str] = None
    academic_status: Optional[str] = Field(None, alias="academicStatus")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

class AcademicSection(AcademicSectionBase):
    id: int
    tenant_id: str

    class Config:
        from_attributes = True
        populate_by_name = True
        allow_population_by_field_name = True

class AcademicClassBase(BaseModel):
    name: str
    numeric: Optional[Union[int, str]] = None
    teacher_id: Optional[Union[int, str]] = Field(None, alias="teacherId")
    note: Optional[str] = None
    academic_status: Optional[str] = Field("Active", alias="academicStatus")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

class AcademicClassCreate(AcademicClassBase):
    pass

class AcademicClassUpdate(BaseModel):
    name: Optional[str] = None
    numeric: Optional[Union[int, str]] = None
    teacher_id: Optional[Union[int, str]] = Field(None, alias="teacherId")
    note: Optional[str] = None
    academic_status: Optional[str] = Field(None, alias="academicStatus")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

class AcademicClass(AcademicClassBase):
    id: int
    tenant_id: str
    sections: List[AcademicSection] = []

    class Config:
        from_attributes = True
        populate_by_name = True
        allow_population_by_field_name = True
