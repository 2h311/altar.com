import hashlib
from pathlib import Path
from typing import Union

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import FastAPI, Request, Response, HTTPException

import svgwrite


app = FastAPI(docs_url=None, redoc_url=None, openapi_url="/openapi")
app.mount("/assets", StaticFiles(directory=Path("templates") / "assets"), name="assets")
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
        color = f"#{color}"

    fields = list()
    for i in range(66):
        fields.append(field_data[:3])  # get first 3 bits
        field_data = field_data[3:]  # then remove them

    field_fill = list()
    for field in fields:
        # conver bits to list (010 -> [0, 1, 0])
        bit_list = list(field)

        # sum all bits
        # bit_sum = int(bit_list[0]) + int(bit_list[1]) +  int(bit_list[2])
        bit_sum = sum(map(int, bit_list))
        if bit_sum <= 1:
            field_fill.append(False)
        elif bit_sum >= 2:
            field_fill.append(True)

    # x, y, x-limit (see comments above) (max: 11, 11, 6)
    usable_grid_size = [5, 5, 3]

    # credits to chatGPT lol, didn't know this existed
    dwg = svgwrite.Drawing("identicon.svg", profile="tiny")

    if background:
        if background == "light":
            background = "#ffffff"
        elif background == "dark":
            background = "#212121"
        else:
            background = f"#{background}"

        try:
            dwg.add(dwg.rect((0, 0), (size, size), fill=background))  # fill background
        except TypeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid background color - only pass on HEX colors without the '#' prefix or 'light'/'dark'",
            )
    # Size of each identicon cell
    cell_size = size / usable_grid_size[0]

    # iterate through y
    for i in range(usable_grid_size[1]):
        row_list = list()

        # iterate through x
        for j in range(usable_grid_size[2]):
            # i (row) * x (size, e.g. 11) + j (column index) -> list index
            if field_fill[i * usable_grid_size[2] + j] == True:
                # calculate cell position
                x = j * cell_size
                y = i * cell_size

                # Draw cell rectangle with the assigned color
                try:
                    dwg.add(dwg.rect((x, y), (cell_size, cell_size), fill=color))
                except TypeError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid fill color - only pass on HEX colors without the '#' prefix",
                    )
            else:
                pass
            # make a separate list for reversing
            row_list.append(field_fill[i * usable_grid_size[2] + j])

        # reverse the list & remove the first element (the middle one / x-limit)
        row_list_reversed = list(reversed(row_list))[1:]

        # make a separate index for the reversed list since k is not an index like j
        row_list_index = 0

        for k in row_list_reversed:
            if k == True:
                # Calculate cell position
                x = (row_list_index + usable_grid_size[2]) * cell_size
                y = i * cell_size

                # Draw cell rectangle with the assigned color
                try:
                    dwg.add(dwg.rect((x, y), (cell_size, cell_size), fill=color))
                except TypeError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid fill color - only pass on HEX colors without the '#' prefix",
                    )
            else:
                pass
            row_list_index += 1

    # Get the SVG as a string
    svg_string = dwg.tostring()
    # Set the response type to SVG
    return Response(content=svg_string, media_type="image/svg+xml")
