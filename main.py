from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse
import os
import clingo

app = FastAPI()

@app.get("/solve", response_class=PlainTextResponse)
def solve(file: str = Query(...), extra_args: str = Query("")):
    file_path = os.path.join("simpleInstances", f"{file}.asp")

    if not os.path.isfile(file_path):
        return PlainTextResponse(f"File '{file}' not found.", status_code=404)

    try:
        ctl = clingo.Control(arguments=extra_args.split() if extra_args else [])
        ctl.load(file_path)
        ctl.ground([("base", [])])

        output = []

        def on_model(model):
            output.append(str(model))

        ctl.solve(on_model=on_model)

        return "\n".join(output) if output else "No answer sets found."

    except Exception as e:
        return f"Error: {str(e)}"
