from fastapi.responses import JSONResponse


def resp_handler(msg: str, data=None, response_status_code=200):
    return JSONResponse(
        status_code=response_status_code,
        content={"success": True, "message": msg, "data": data},
    )
