"""
Honkai: Star Rail Text Search API
崩坏：星穹铁道文本搜索API

This FastAPI application provides a search interface for dialog lines from Honkai: Star Rail game.
Users can search for specific dialog lines by speaker, text content, or unique ID.
The application supports pagination and context retrieval for better user experience.

这个FastAPI应用程序为崩坏：星穹铁道游戏的对话行提供搜索接口。
用户可以通过发言者、文本内容或唯一ID搜索特定的对话行。
该应用程序支持分页和上下文检索，以提供更好的用户体验。

Features / 功能:
- Search dialog by speaker(s) / 通过发言者搜索对话
- Search dialog by text content / 通过文本内容搜索对话
- Retrieve dialog by unique ID / 通过唯一ID检索对话
- Get context around specific dialog lines / 获取特定对话行的上下文
- Pagination support / 支持分页
- RESTful API interface / RESTful API接口

Author / 作者: modenicheng
Version / 版本: 1.0.0
"""

from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from h11 import Response
from sqlmodel import or_
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from yarl import Query
from models import *

from pathlib import Path
import os
# 确保静态文件目录存在
static_dir = Path("webpage/dist")
if not static_dir.exists():
    exit_code = os.system("cd webpage && yarn build")
    if exit_code != 0:
        raise Exception(
            "Failed to build static files. Please check your environment.")

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
    """Initialize the database and create tables on application startup.
    在应用程序启动时初始化数据库并创建表。
    
    This function is called automatically when the FastAPI application starts up.
    It ensures that all necessary database tables are created and ready for use.
    
    当FastAPI应用程序启动时，此函数会自动调用。
    它确保所有必要的数据库表都已创建并可供使用。
    """
    create_db_and_tables()


@app.get("/api/openapi/")
async def openapi():
    """Redirect to the OpenAPI documentation page.
    重定向到OpenAPI文档页面。

    This endpoint redirects users to the OpenAPI documentation page, where they can find detailed information about the API endpoints and their usage.
    该端点将用户重定向到OpenAPI文档页面，用户可以在该页面找到有关API端点和其用法的信息。
    """
    return RedirectResponse(url="/openapi.json")


@app.get("/api/speakers/")
async def speakers(offset: int = 0,
                   limit: int = 200,
                   query: str | None = None,
                   session: Session = Depends(get_session)):
    """Get a list of unique speakers in the dialog database.
        获取对话数据库中所有唯一发言者的列表。

    This endpoint returns a list of unique speakers in the dialog database, which can be used as filters for searching dialog lines.
    该端点返回对话数据库中所有唯一发言者的列表，这些发言者可以作为搜索对话行的筛选条件。
    
    Args:
        offset (int, optional): Pagination offset. Defaults to 0.
                               分页偏移量。默认为0。
        limit (int, optional): Pagination limit. Defaults to 200.
                              分页限制。默认为200。
                              
    Returns:
        List[str]: A list of unique speakers in the dialog database.
                   对话数据库中所有唯一发言者的列表。
    """
    if query:
        statement = select(Dialog.speaker).distinct().where(
            Dialog.speaker.like(f"%{query}%"))
    else:
        statement = select(Dialog.speaker).distinct()
    statement = statement.offset(offset).limit(limit)
    result = session.exec(statement).all()
    total = session.exec(select(func.count(Dialog.speaker.distinct()))).one()
    return JSONResponse({
        "data":
        result,
        "total":
        total
    })


@app.get("/api/dialog/")
async def dialog(
    idx: int | None = None,
    speakers: str | None = None,
    speaker: str | None = None,  # deprecated, use speakers instead
    text: str | None = None,
    include_neighbors: bool = False,  # deprecated, use context instead
    context: bool = False,
    offset: int = 0,
    limit: int = 200,
    session: Session = Depends(get_session)):
    """Search dialog in HSR (Honkai: Star Rail) by using speakers and keywords
    在崩坏：星穹铁道中通过发言者和关键词搜索对话
    
    This endpoint allows users to search for dialog lines in the game database with flexible filtering options.
    该端点允许用户使用灵活的筛选选项在游戏数据库中搜索对话行。
    
    Args:
        idx (int | None, optional): The unique id of a single line. Defaults to None.
                                   单行对话的唯一标识ID。默认为None。
        speakers (str | None, optional): Specific speakers of the dialog. For multiple speakers: `speaker1//speaker2//` .etc. Defaults to None.
                                       对话的特定发言者。多个发言者请使用格式：`发言者1//发言者2//`等。默认为None。
        speaker (str | None, optional): Specific single speaker. DEPRECATED. Defaults to None.
                                      特定单个发言者。已弃用，请使用speakers参数。默认为None。
        include_neighbors (bool, optional): If `include_neighbors` is True, the return will be a set of successive dialog. DEPRECATED, use `context` instead. Defaults to False.
                                          如果为True，返回结果将包含连续的对话集合。已弃用，请使用context参数。默认为False。
        context (bool, optional): Same to `include_neighbors`. Defaults to False.
                                 与`include_neighbors`功能相同。如果为True，返回结果将包含连续的对话集合。默认为False。
        offset (int, optional): Pagination offset. Defaults to 0.
                               分页偏移量。默认为0。
        limit (int, optional): Pagination limit. Defaults to 200.
                              分页限制。默认为200。
        session (Session, optional): This is an internal argument. DO NOT PASS IT IN. Defaults to Depends(get_session).
                                   这是一个内部参数。请勿传递此参数。默认为Depends(get_session)。

    Raises:
        HTTPException: 400 - Bad Request when context is True but idx is None.
                      404 - Not Found when the requested dialog idx does not exist.
                      422 - Unprocessable Entity when request parameters are invalid.
                      500 - Internal Server Error for unexpected issues.
        HTTPException: 400 - 当context为True但idx为None时的错误请求。
                      404 - 当请求的对话ID不存在时的未找到错误。
                      422 - 当请求参数无效时的不可处理实体错误。
                      500 - 意外问题的内部服务器错误。

    Returns:
        JSON Object: A list of matched dialog lines. Each line is a JSON object with the following fields:
            `index`: The index of the line in the database.
            `idx`: The unique id of the line.
            `speaker`: The speaker of the line.
            `text`: The text of the line.
        JSON对象：匹配的对话列表。每个对话都是一个JSON对象，包含以下字段：
            `index`: 该对话在数据库中的索引。
            `idx`: 该对话的唯一ID。
            `speaker`: 该对话的发言者。
            `text`: 该对话的文本内容。
    """

    statement = select(Dialog)
    if speakers is not None:
        querys = speakers.split("//")

    statement = select(Dialog)
    if speakers is not None:
        querys = speakers.split("//")
        statement = statement.where(
            or_(*[Dialog.speaker.like(f"%{q}%") for q in querys]))
    elif speaker is not None:
        statement = statement.where(Dialog.speaker.like(f"%{speaker}%"))

    if text is not None:
        querys = text.split("//")
        statement = statement.where(
            or_(*[Dialog.text.like(f"%{q}%") for q in querys]))

    if idx is not None and (include_neighbors or context):
        current_dialog = session.exec(
            select(Dialog).where(Dialog.idx == idx)).first()
        if current_dialog is None:
            raise HTTPException(status_code=404, detail="Dialog not found")

        all_idx = session.exec(select(Dialog.idx)).all()
        target_idxs = find_continuous_subarray(list(all_idx), idx)
        statement = statement.where(Dialog.idx.in_(target_idxs))

    elif (context or include_neighbors) and idx == None:
        raise HTTPException(status_code=400,
                            detail="include_neighbors or context require idx")

    elif idx is not None:
        statement = statement.where(Dialog.idx == idx)
    
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()
    
    # 应用分页
    statement = statement.offset(offset).limit(limit)
    result = session.exec(statement).all()
    
    return JSONResponse({
        "data": [item.model_dump() for item in result],
        "total": total
    })


# PLACE STATIC FILES HERE, to avoid 404 error
# mount static vue site. REQUIRE: yarn build in webpage dir
app.mount("/",
          StaticFiles(directory=str(static_dir), html=True),
          name="webpage")


def find_continuous_subarray(arr: List[int], target: int) -> List[int]:
    """
    Find the longest continuous integer subarray containing target in a sorted non-contiguous array.
    在已排序的不连续数组中找到包含目标值的最长连续整数子数组。
    
    This function identifies continuous sequences within a sorted array that may have gaps,
    and returns the longest continuous sequence that contains the target value.
    该函数识别可能存在间隔的已排序数组中的连续序列，并返回包含目标值的最长连续序列。
    
    Args:
        arr (List[int]): A sorted list of integers that may have gaps between values.
                        可能存在值之间间隔的已排序整数列表。
        target (int): The integer value to find within a continuous subarray.
                     要在连续子数组中找到的整数值。
    
    Returns:
        List[int]: The longest continuous subarray containing the target value.
                  Returns an empty list if the target is not found in the array.
                  包含目标值的最长连续子数组。如果目标值不在数组中，则返回空列表。
    
    Examples:
        >>> find_continuous_subarray([1, 2, 5, 6, 7, 10], 6)
        [5, 6, 7]
        
        >>> find_continuous_subarray([1, 3, 5, 7], 4)
        []
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
    """Entry point for running the application directly.
    直接运行应用程序的入口点。
    
    This block executes when the script is run directly (not when imported as a module).
    It starts the uvicorn server to serve the FastAPI application.
    
    当脚本直接运行时（而不是作为模块导入时），此块会执行。
    它启动uvicorn服务器来提供FastAPI应用程序。
    
    The server will be accessible at http://localhost:8000 when run locally.
    在本地运行时，服务器可通过http://localhost:8000访问。
    """
    uvicorn.run(app, host="0.0.0.0", port=8000)
