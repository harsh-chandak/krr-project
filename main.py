from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse
import os
import clingo

from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def homepage():
    return """
    <html>
      <head>
        <title>Clingo Solver</title>
        <style>
          body { font-family: monospace; background: #121212; color: #e0e0e0; padding: 2rem; }
          button { margin: 0.5rem; padding: 0.5rem 1rem; background: #007acc; color: white; border: none; border-radius: 4px; cursor: pointer; }
          pre { background: #1e1e1e; padding: 1rem; border-radius: 5px; margin-top: 1rem; overflow-x: auto; }
        </style>
      </head>
      <body>
        <h1>Select an Instance to Solve</h1>
        <div id="buttons">
          <button onclick="solve('inst1')">inst1</button>
          <button onclick="solve('inst2')">inst2</button>
          <button onclick="solve('inst3')">inst3</button>
          <button onclick="solve('inst4')">inst4</button>
          <button onclick="solve('inst5')">inst5</button>
        </div>
        <pre id="result">// result will appear here</pre>

        <script>
          async function solve(instance) {
            const resultBox = document.getElementById("result");
            resultBox.textContent = "Solving " + instance + "...";

            try {
              const res = await fetch(`/solve?file=${instance}`);
              const text = await res.text();
              resultBox.textContent = text;
            } catch (err) {
              resultBox.textContent = "Error: " + err;
            }
          }
        </script>
      </body>
    </html>
    """
