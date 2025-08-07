from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import PlainTextResponse
import subprocess

app = FastAPI()

@app.post("/solve", response_class=PlainTextResponse)
async def solve(file: UploadFile, extra_args: str = Form("")):
    content = await file.read()

    with open("input.asp", "wb") as f:
        f.write(content)

    try:
        result = subprocess.run(
            ["clingo", "input.asp"] + extra_args.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        return result.stdout.decode() or result.stderr.decode()
    except Exception as e:
        return f"Error: {str(e)}"
