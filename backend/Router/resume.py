from fastapi.routing import APIRouter


router = APIRouter(
    prefix="/resume",
    tags=["resume"]
)


@router.post("/upload")
def resume_upload():
    pass

@router.post("/analize/{resume_id}")
def resume_analize(resume_id:int):
    pass


@router.post("/update/{old_resume_id}")
def resume_update(old_resume_id:int):
    pass

