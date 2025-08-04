from typing import List
from fastapi import FastAPI, Depends, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from models import *

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/dialog/")
async def dialog(idx: int | None = None,
                 speaker: str | None = None,
                 text: str | None = None,
                 offset: int = 0,
                 limit: int = 200,
                 include_neighbors: bool = False,
                 session: Session = Depends(get_session)):

    statement = select(Dialog)
    if speaker is not None:
        statement = statement.where(Dialog.speaker.like(f"%{speaker}%"))
    if text is not None:
        statement = statement.where(Dialog.text.like(f"%{text}%"))

    if idx is not None and include_neighbors:
        current_dialog = session.exec(
            select(Dialog).where(Dialog.idx == idx)).first()
        if current_dialog is None:
            raise HTTPException(status_code=404, detail="Dialog not found")

        all_idx = session.exec(select(Dialog.idx)).all()
        target_idxs = find_continuous_subarray(list(all_idx), idx)
        statement = statement.where(Dialog.idx.in_(target_idxs))

    elif idx is not None:
        statement = statement.where(Dialog.idx == idx)

    # 应用分页
    statement = statement.offset(offset).limit(limit)

    results = session.exec(statement).all()
    return results


def find_continuous_subarray(arr: List[int], target: int) -> List[int]:
    """
    在已排序的不连续数组 arr 中找到包含 target 的最长连续整数子数组。
    若 target 不存在，返回空列表。
    """
    if not arr:
        return []

    # 先把所有连续区间切开
    ranges = []  # 每个元素是一个连续区间
    start = arr[0]
    for i in range(1, len(arr)):
        if arr[i] != arr[i - 1] + 1:
            ranges.append(list(range(start, arr[i - 1] + 1)))
            start = arr[i]
    # 补上最后一个区间
    ranges.append(list(range(start, arr[-1] + 1)))

    # 找到包含 target 的区间
    for r in ranges:
        if target in r:
            return r
    return []


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1145)
