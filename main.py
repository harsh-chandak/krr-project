from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse
import os
import clingo

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def homepage():
    return """
    <html>
      <head>
        <title>Clingo Solver – Warehouse Planner</title>
        <style>
          body { font-family: monospace; background: #121212; color: #e0e0e0; padding: 2rem; }
          button { margin: 0.5rem; padding: 0.5rem 1rem; background: #007acc; color: white; border: none; border-radius: 4px; cursor: pointer; }
          pre { background: #1e1e1e; padding: 1rem; border-radius: 5px; margin-top: 1rem; overflow-x: auto; }
          h1, h2, h3 { color: #f9d342; }
          p { max-width: 800px; margin-bottom: 1rem; }
        </style>
      </head>
      <body>
        <h1>📦 Automated Warehouse Planner (Clingo + ASP)</h1>

        <p>
          This web interface allows you to solve instances of the <strong>Automated Warehouse Scenario</strong>,
          a logistics-inspired planning problem modeled using <strong>Answer Set Programming (ASP)</strong>.
        </p>

        <p>
          In this problem, autonomous robots must pick up product shelves and deliver them to picking stations
          in a grid-based warehouse. The challenge is to find an efficient plan — a sequence of robot actions
          (like <em>move</em>, <em>pickup</em>, <em>deliver</em>) — that fulfills all customer orders while minimizing
          the total number of time steps (makespan).
        </p>

        <p>
          Each instance is encoded as a <code>.asp</code> file (Answer Set Program). When you click a button below, the server
          uses the <strong>Clingo</strong> solver to compute the optimal sequence of actions under hard constraints like:
          no robot collisions, valid shelf handling, and correct delivery conditions.
        </p>

        <h2>Try a Scenario</h2>
        <div id="buttons">
          <button onclick="solve('inst1')">inst1</button>
          <button onclick="solve('inst2')">inst2</button>
          <button onclick="solve('inst3')">inst3</button>
          <button onclick="solve('inst4')">inst4</button>
          <button onclick="solve('inst5')">inst5</button>
        </div>

        <h3>🔍 Solver Output</h3>
        <pre id="result">// Result will appear here</pre>

        <details>
          <summary style="cursor:pointer; font-weight: bold;">📖 How to read the output</summary>
          <p>The output is a set of atoms (facts) representing a valid solution:</p>
          <ul>
            <li><code>move(robot1, 1, 2, 3)</code> – At time step 1, robot1 moves to position (2, 3).</li>
            <li><code>pickup(robot1, shelf5)</code> – Robot picks up shelf5 at its location.</li>
            <li><code>deliver(robot1, station2)</code> – Robot delivers shelf5 to station2.</li>
            <li><code>shelf_at(shelf5, 2, 3)</code> – Shelf5 is initially at position (2, 3).</li>
            <li><code>goal(station2, shelf5)</code> – Shelf5 needs to be delivered to station2.</li>
          </ul>
          <p>
            These steps together form a valid plan. If you see <code>No answer sets found</code>, there is no valid solution
            for that scenario.
          </p>
        </details>

        <script>
          async function solve(instance) {
            const resultBox = document.getElementById("result");
            resultBox.textContent = "Solving " + instance + "...";

            try {
              const res = await fetch(`/solve?file=${instance}`);
              const json = await res.json();

              resultBox.textContent = `// Raw Output:\n${json.raw}\n\n// Human-readable:\n${json.human}`;
            } catch (err) {
              resultBox.textContent = "Error: " + err;
            }
          }
        </script>
      </body>
    </html>
    """

@app.get("/solve", response_class=JSONResponse)
def solve(file: str = Query(...), extra_args: str = Query("")):
    file_path = os.path.join("simpleInstances", f"{file}.asp")

    if not os.path.isfile(file_path):
        return JSONResponse({"error": f"File '{file}' not found."}, status_code=404)

    try:
        ctl = clingo.Control(arguments=extra_args.split() if extra_args else [])
        ctl.load(file_path)
        ctl.ground([("base", [])])

        models = []

        def on_model(model):
            models.append(str(model))

        ctl.solve(on_model=on_model)

        if not models:
            return {"raw": "No answer sets found.", "human": "❌ No valid solution found for this scenario."}

        raw_output = models[0]
        facts = raw_output.split()
        human_lines = []

        for fact in facts:
            if "init(object(robot" in fact:
                id = fact.split(",")[1]
                x, y = fact.split("pair(")[1].rstrip("))").split(",")
                human_lines.append(f"🤖 Robot {id} is located at ({x}, {y})")
            elif "init(object(product" in fact and "on" in fact:
                id = fact.split(",")[1]
                x, y = fact.split("pair(")[1].rstrip("))").split(",")
                human_lines.append(f"📦 Product {id} is located on shelf at ({x}, {y})")
            elif "init(object(pickingStation" in fact:
                id = fact.split(",")[1]
                x, y = fact.split("pair(")[1].rstrip("))").split(",")
                human_lines.append(f"🛒 Picking Station {id} is at ({x}, {y})")
            elif "init(object(order" in fact and "pickingStation" in fact:
                order_id = fact.split(",")[1]
                station_id = fact.split(",")[2].split(")")[0]
                human_lines.append(f"📬 Order {order_id} should be delivered to Picking Station {station_id}")
            elif "init(object(order" in fact and "line" in fact:
                order_id = fact.split(",")[1]
                x, y = fact.split("pair(")[1].rstrip("))").split(",")
                human_lines.append(f"📄 Order {order_id} includes product at ({x}, {y})")
            # Add more rule parsing as needed

        return {
            "raw": raw_output,
            "human": "\n".join(human_lines) if human_lines else "No interpretable facts found."
        }

    except Exception as e:
        return JSONResponse({"error": f"Internal error: {str(e)}"}, status_code=500)