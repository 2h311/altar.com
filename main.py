import hashlib
from typing import Union

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import FastAPI, Request, Response, HTTPException

import svgwrite


app = FastAPI(docs_url=None, redoc_url=None, openapi_url="/openapi")
app.mount("/assets", StaticFiles(directory="templates" "asset"), name="assets")
templates = Jinja2Templates(directory="templates")


def binarize(string: str) -> str:
    hash = hashlib.sha256(bytes(string, "utf-8")).hexdigest()
    decimal_value = int(hash, 16)
    binary_string = bin(decimal_value)[2:]
    # increase string length to 256 if not long enough
    while len(binary_string) < 256:
        binary_string = f"0{binary_string}"
    return binary_string


@app.get("/", response_class=HTMLResponse)
def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/docs")
def get_docs():
    return RedirectResponse(
        "https://github.com/berrysauce/altar/blob/master/README.md#settings",
        status_code=302,
    )


@app.get("/generate")
def get_identicon(
    data: str, color: str | None = None, background: str | None = None, size: int = 250
):
    binarized = binarize(data)
    color_data, field_data = binarized[:58], binarized[58:]

    if not color:
        segment_length = 6  # length of each segment
        color_map = {
            0: "#5bc0eb",  # blue - my fav :)
            1: "#fde74c",  # yellow
            2: "#9bc53d",  # green
            3: "#e55934",  # red
            4: "#fa7921",  # orange
        }

        # get the first 6 bits of the color data
        color_data_segment = color_data[:segment_length]
        # convert the segment from binary to decimal
        decimal_value = int(color_data_segment, 2)
        # use hashlib to generate a hash value based on the segment
        hash_value = hashlib.md5(str(decimal_value).encode()).hexdigest()
        # convert the hash value to an integer
        hash_integer = int(hash_value, 16)
        # map the integer value to an index within the range of available colors
        color_index = hash_integer % len(color_map)
        # get the color based on the index
        color = color_map[color_index]
    else:
        ...
