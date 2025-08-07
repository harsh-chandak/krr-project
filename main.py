from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse
import subprocess
import os

app = FastAPI()

@app.get("/solve", response_class=PlainTextResponse)
def solve(
    file: str = Query(..., description="Name of the .asp file without extension"),
    extra_args: str = Query("", description="Optional extra arguments for clingo")
):
    file_path = os.path.join("simpleInstances", f"{file}.asp")

    if not os.path.isfile(file_path):
        return PlainTextResponse(f"Error: File '{file_path}' not found.", status_code=404)

    try:
        result = subprocess.run(
            ["clingo", file_path] + extra_args.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        output = result.stdout.decode() or result.stderr.decode()
        return output
    except Exception as e:
        return f"Error running clingo: {str(e)}"
