import random
import json
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

app = dash.Dash(
    __name__,
    title="Sorting Visualizer",
    external_stylesheets=[dbc.themes.DARKLY]
)
server = app.server

# ── Vibrant Modern Colors ───────────────────────────────────────────────────
COL = {
    "default": "#6366F1",  # Neon Indigo
    "compare": "#F43F5E",  # Coral / Pink Glow
    "swap": "#F59E0B",     # Vibrant Amber
    "sorted": "#10B981",   # Bright Emerald Green
    "pivot": "#A855F7",    # Bright Purple
}

COMPLEXITY = {
    "bubble": {"time": "O(n²)", "space": "O(1)"},
    "selection": {"time": "O(n²)", "space": "O(1)"},
    "insertion": {"time": "O(n²)", "space": "O(1)"},
    "quick": {"time": "O(n log n)", "space": "O(log n)"},
    "merge": {"time": "O(n log n)", "space": "O(n)"},
}

# ── Step Generator ──────────────────────────────────────────────────────────
def generate_steps(arr, algo):
    arr = arr[:]
    n = len(arr)
    colors = ["default"] * n
    steps = []
    cmp = [0]
    swp = [0]

    def snapshot():
        steps.append((arr[:], colors[:], cmp[0], swp[0]))

    if algo == "bubble":
        for i in range(n - 1):
            for j in range(n - i - 1):
                colors[j] = colors[j + 1] = "compare"
                cmp[0] += 1
                snapshot()

                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    colors[j] = colors[j + 1] = "swap"
                    swp[0] += 1
                    snapshot()

                colors[j] = colors[j + 1] = "default"
            colors[n - 1 - i] = "sorted"
        colors[0] = "sorted"
        snapshot()

    elif algo == "selection":
        for i in range(n - 1):
            min_idx = i
            colors[i] = "pivot"

            for j in range(i + 1, n):
                colors[j] = "compare"
                cmp[0] += 1
                snapshot()

                if arr[j] < arr[min_idx]:
                    if min_idx != i:
                        colors[min_idx] = "default"
                    min_idx = j
                    colors[j] = "pivot"
                else:
                    colors[j] = "default"

            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                colors[i] = colors[min_idx] = "swap"
                swp[0] += 1
                snapshot()

            colors[min_idx] = "default"
            colors[i] = "sorted"

        colors[n - 1] = "sorted"
        snapshot()

    elif algo == "insertion":
        colors[0] = "sorted"
        for i in range(1, n):
            key = arr[i]
            j = i - 1
            colors[i] = "compare"
            snapshot()

            while j >= 0 and arr[j] > key:
                cmp[0] += 1
                arr[j + 1] = arr[j]
                colors[j + 1] = "swap"
                colors[j] = "compare"
                swp[0] += 1
                snapshot()
                colors[j + 1] = "sorted"
                j -= 1

            arr[j + 1] = key
            colors[j + 1] = "sorted"
            snapshot()

    elif algo == "quick":
        def partition(lo, hi):
            pivot = arr[hi]
            colors[hi] = "pivot"
            i = lo - 1

            for j in range(lo, hi):
                colors[j] = "compare"
                cmp[0] += 1
                snapshot()

                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
                    colors[i] = colors[j] = "swap"
                    swp[0] += 1
                    snapshot()
                    colors[i] = "default"

                colors[j] = "default"

            arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
            colors[i + 1] = "sorted"
            colors[hi] = "default"
            swp[0] += 1
            snapshot()
            return i + 1

        def quick(lo, hi):
            if lo < hi:
                p = partition(lo, hi)
                quick(lo, p - 1)
                quick(p + 1, hi)
            elif lo == hi:
                colors[lo] = "sorted"

        quick(0, n - 1)
        snapshot()

    elif algo == "merge":
        def merge(lo, mid, hi):
            left = arr[lo:mid + 1]
            right = arr[mid + 1:hi + 1]
            i = j = 0
            k = lo

            while i < len(left) and j < len(right):
                cmp[0] += 1
                colors[k] = "compare"
                snapshot()

                if left[i] <= right[j]:
                    arr[k] = left[i]
                    i += 1
                else:
                    arr[k] = right[j]
                    j += 1

                colors[k] = "sorted"
                k += 1

            while i < len(left):
                arr[k] = left[i]
                colors[k] = "sorted"
                i += 1
                k += 1

            while j < len(right):
                arr[k] = right[j]
                colors[k] = "sorted"
                j += 1
                k += 1

            snapshot()

        def msort(lo, hi):
            if lo < hi:
                mid = (lo + hi) // 2
                msort(lo, mid)
                msort(mid + 1, hi)
                merge(lo, mid, hi)
            else:
                colors[lo] = "sorted"

        msort(0, n - 1)
        snapshot()

    return steps

# ── Chart Creator ────────────────────────────────────────────────────────────
def make_figure(arr, colors, show_labels=True):
    bar_colors = [COL.get(c, COL["default"]) for c in colors]

    bar_kwargs = dict(
        x=list(range(len(arr))),
        y=arr,
        marker=dict(
            color=bar_colors,
            line=dict(width=0),
            cornerradius="30%"
        )
    )

    if show_labels:
        bar_kwargs["text"] = arr
        bar_kwargs["textposition"] = "outside"
        bar_kwargs["textfont"] = dict(color="#CBD5E1", size=10, family="Inter, sans-serif")

    fig = go.Figure(go.Bar(**bar_kwargs))

    fig.update_layout(
        margin=dict(l=10, r=10, t=25, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        uirevision="constant",
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            zeroline=False,
            range=[0, max(arr) + 15]
        ),
        bargap=0.18,
        height=360,
    )
    return fig

# ── Styling Shortcuts ─────────────────────────────────────────────────────────
CARD_STYLE = {
    "backgroundColor": "rgba(30, 41, 59, 0.7)",
    "backdropFilter": "blur(12px)",
    "border": "1px solid rgba(255, 255, 255, 0.1)",
    "borderRadius": "16px",
    "boxShadow": "0 20px 25px -5px rgba(0, 0, 0, 0.5)",
}

CONTROLS_CARD_STYLE = {
    **CARD_STYLE,
    "position": "relative",
    "zIndex": 1050,
    "overflow": "visible"
}

# ── App Layout ───────────────────────────────────────────────────────────────
app.layout = html.Div(
    style={
        "backgroundColor": "#090D16",
        "backgroundImage": "radial-gradient(circle at 50% 0%, #1E1B4B 0%, #090D16 70%)",
        "minHeight": "100vh",
        "color": "#F8FAFC",
        "padding": "40px 16px",
        "fontFamily": "Inter, system-ui, sans-serif",
    },
    children=[
        dbc.Container(
            [
                dcc.Store(id="store-steps"),
                dcc.Store(id="store-frame", data=0),
                dcc.Store(id="store-orig"),
                dcc.Interval(id="interval", interval=100, n_intervals=0, disabled=True),

                # App Header
                html.Div(
                    className="text-center mb-5",
                    children=[
                        html.H1(
                            "SORTING VISUALIZER",
                            style={
                                "fontSize": "38px",
                                "fontWeight": "900",
                                "letterSpacing": "2px",
                                "background": "linear-gradient(90deg, #818CF8, #C084FC, #F43F5E)",
                                "WebkitBackgroundClip": "text",
                                "WebkitTextFillColor": "transparent",
                                "margin": "0 0 8px 0",
                            },
                        ),
                        html.P("Real-time algorithmic execution & complexity profiler", style={"color": "#94A3B8", "fontSize": "15px"}),
                    ],
                ),

                # Control Panel Card
                dbc.Card(
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Label("ALGORITHM", style={"fontSize": "11px", "letterSpacing": "1px", "fontWeight": "700", "color": "#818CF8"}),
                                            dcc.Dropdown(
                                                id="dd-algo",
                                                options=[
                                                    {"label": "Bubble Sort", "value": "bubble"},
                                                    {"label": "Selection Sort", "value": "selection"},
                                                    {"label": "Insertion Sort", "value": "insertion"},
                                                    {"label": "Quick Sort", "value": "quick"},
                                                    {"label": "Merge Sort", "value": "merge"},
                                                ],
                                                value="quick",
                                                clearable=False,
                                                style={"backgroundColor": "#0F172A", "color": "#000", "border": "none", "borderRadius": "8px"},
                                            ),
                                        ],
                                        md=4, className="mb-3"
                                    ),
                                    dbc.Col(
                                        [
                                            html.Label("ARRAY SIZE", style={"fontSize": "11px", "letterSpacing": "1px", "fontWeight": "700", "color": "#818CF8"}),
                                            dcc.Slider(id="sl-size", min=10, max=60, step=5, value=30, marks={10: "10", 30: "30", 60: "60"}),
                                        ],
                                        md=4, className="mb-3"
                                    ),
                                    dbc.Col(
                                        [
                                            html.Label("ANIMATION SPEED", style={"fontSize": "11px", "letterSpacing": "1px", "fontWeight": "700", "color": "#818CF8"}),
                                            dcc.Slider(id="sl-speed", min=1, max=10, step=1, value=6, marks={1: "Slow", 10: "Ultra"}),
                                        ],
                                        md=4, className="mb-3"
                                    ),
                                ]
                            ),
                            html.Hr(style={"borderColor": "rgba(255,255,255,0.1)", "margin": "16px 0"}),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Checklist(
                                            options=[{"label": " Show Bar Values", "value": True}],
                                            value=[True],
                                            id="sw-values",
                                            switch=True,
                                            style={"color": "#94A3B8", "fontSize": "13px", "fontWeight": "600"}
                                        ),
                                        width=6,
                                        className="d-flex align-items-center"
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Button("New Array", id="btn-gen", color="secondary", outline=True, className="me-2 px-4 fw-bold", style={"borderRadius": "8px"}),
                                            dbc.Button("▶ Run Algorithm", id="btn-start", color="primary", className="me-2 px-4 fw-bold", style={"borderRadius": "8px", "background": "linear-gradient(90deg, #6366F1, #8B5CF6)", "border": "none"}),
                                            dbc.Button("↺ Reset", id="btn-reset", color="dark", className="px-3", style={"borderRadius": "8px"}),
                                        ],
                                        width=6,
                                        className="d-flex justify-content-end",
                                    ),
                                ],
                                className="align-items-center"
                            ),
                        ]
                    ),
                    style=CONTROLS_CARD_STYLE,
                    className="mb-4",
                ),

                # Metrics Dashboard
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.Div("COMPARISONS", style={"fontSize": "11px", "color": "#94A3B8", "fontWeight": "700", "letterSpacing": "1px"}),
                                    html.H2(id="stat-cmp", children="0", style={"fontSize": "32px", "fontWeight": "800", "color": "#F43F5E", "margin": "4px 0 0"}),
                                ]), style=CARD_STYLE, className="text-center mb-3"
                            ), width=3
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.Div("SWAPS / WRITES", style={"fontSize": "11px", "color": "#94A3B8", "fontWeight": "700", "letterSpacing": "1px"}),
                                    html.H2(id="stat-swp", children="0", style={"fontSize": "32px", "fontWeight": "800", "color": "#F59E0B", "margin": "4px 0 0"}),
                                ]), style=CARD_STYLE, className="text-center mb-3"
                            ), width=3
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.Div("TIME COMPLEXITY", style={"fontSize": "11px", "color": "#94A3B8", "fontWeight": "700", "letterSpacing": "1px"}),
                                    html.H2(id="stat-tc", children="O(n log n)", style={"fontSize": "26px", "fontWeight": "800", "color": "#818CF8", "margin": "8px 0 0"}),
                                ]), style=CARD_STYLE, className="text-center mb-3"
                            ), width=3
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.Div("SPACE COMPLEXITY", style={"fontSize": "11px", "color": "#94A3B8", "fontWeight": "700", "letterSpacing": "1px"}),
                                    html.H2(id="stat-sc", children="O(log n)", style={"fontSize": "26px", "fontWeight": "800", "color": "#10B981", "margin": "8px 0 0"}),
                                ]), style=CARD_STYLE, className="text-center mb-3"
                            ), width=3
                        ),
                    ]
                ),

                # Main Visualization Display
                dbc.Card(
                    dbc.CardBody(
                        [
                            dcc.Graph(id="graph", config={"displayModeBar": False}),
                            html.Div(
                                [
                                    html.Span(
                                        [
                                            html.Span(style={"width": "10px", "height": "10px", "borderRadius": "50%", "backgroundColor": v, "display": "inline-block", "marginRight": "6px", "boxShadow": f"0 0 10px {v}"}),
                                            k.capitalize(),
                                        ],
                                        style={"marginRight": "24px", "fontSize": "12px", "color": "#CBD5E1", "display": "inline-flex", "alignItems": "center"}
                                    )
                                    for k, v in COL.items()
                                ],
                                className="d-flex justify-content-center mt-3 pt-3",
                                style={"borderTop": "1px solid rgba(255, 255, 255, 0.08)"}
                            ),
                        ]
                    ),
                    style=CARD_STYLE,
                    className="mb-3",
                ),

                # Status Indicator
                html.Div(
                    id="status-msg",
                    children="Select settings and click ▶ Run Algorithm",
                    style={"textAlign": "center", "color": "#64748B", "fontSize": "13px", "fontWeight": "600", "letterSpacing": "0.5px"},
                ),
            ],
            style={"maxWidth": "1000px"}
        )
    ]
)

# ── Callbacks ─────────────────────────────────────────────────────────────────

@app.callback(
    Output("store-orig", "data"),
    Output("store-steps", "data"),
    Output("store-frame", "data"),
    Output("graph", "figure"),
    Output("stat-cmp", "children"),
    Output("stat-swp", "children"),
    Output("stat-tc", "children"),
    Output("stat-sc", "children"),
    Output("status-msg", "children"),
    Input("btn-gen", "n_clicks"),
    Input("sl-size", "value"),
    Input("dd-algo", "value"),
    State("sw-values", "value"),
)
def new_array(n_clicks, size, algo, show_val):
    arr = [random.randint(10, 99) for _ in range(size)]
    colors = ["default"] * size
    show_labels = True if show_val and len(show_val) > 0 else False
    fig = make_figure(arr, colors, show_labels=show_labels)
    tc = COMPLEXITY[algo]["time"]
    sc = COMPLEXITY[algo]["space"]
    return json.dumps(arr), None, 0, fig, "0", "0", tc, sc, "Array initialized. Click ▶ Run Algorithm to start."

@app.callback(
    Output("graph", "figure", allow_duplicate=True),
    Input("sw-values", "value"),
    State("store-steps", "data"),
    State("store-frame", "data"),
    State("store-orig", "data"),
    prevent_initial_call=True,
)
def toggle_values(show_val, steps_json, frame, orig_json):
    show_labels = True if show_val and len(show_val) > 0 else False
    
    if steps_json and frame is not None:
        steps = json.loads(steps_json)
        idx = min(frame, len(steps) - 1)
        arr, colors, _, _ = steps[idx]
        return make_figure(arr, colors, show_labels=show_labels)
    
    if orig_json:
        arr = json.loads(orig_json)
        colors = ["default"] * len(arr)
        return make_figure(arr, colors, show_labels=show_labels)
        
    return dash.no_update

@app.callback(
    Output("store-steps", "data", allow_duplicate=True),
    Output("store-frame", "data", allow_duplicate=True),
    Output("interval", "disabled"),
    Output("interval", "interval"),
    Input("btn-start", "n_clicks"),
    State("store-orig", "data"),
    State("dd-algo", "value"),
    State("sl-speed", "value"),
    prevent_initial_call=True,
)
def start_sort(n_clicks, orig_json, algo, speed):
    if not orig_json:
        return dash.no_update, dash.no_update, True, 100

    arr = json.loads(orig_json)
    steps = generate_steps(arr, algo)
    interval_ms = max(5, int(200 / (1.5 ** (speed - 1))))
    return json.dumps(steps), 0, False, interval_ms

@app.callback(
    Output("store-steps", "data", allow_duplicate=True),
    Output("store-frame", "data", allow_duplicate=True),
    Output("graph", "figure", allow_duplicate=True),
    Output("interval", "disabled", allow_duplicate=True),
    Output("stat-cmp", "children", allow_duplicate=True),
    Output("stat-swp", "children", allow_duplicate=True),
    Output("status-msg", "children", allow_duplicate=True),
    Input("btn-reset", "n_clicks"),
    State("store-orig", "data"),
    State("sw-values", "value"),
    prevent_initial_call=True,
)
def reset(n_clicks, orig_json, show_val):
    if not orig_json:
        return None, 0, dash.no_update, True, "0", "0", "Array reset."

    arr = json.loads(orig_json)
    colors = ["default"] * len(arr)
    show_labels = True if show_val and len(show_val) > 0 else False
    fig = make_figure(arr, colors, show_labels=show_labels)
    return None, 0, fig, True, "0", "0", "Array reset."

@app.callback(
    Output("graph", "figure", allow_duplicate=True),
    Output("store-frame", "data", allow_duplicate=True),
    Output("interval", "disabled", allow_duplicate=True),
    Output("stat-cmp", "children", allow_duplicate=True),
    Output("stat-swp", "children", allow_duplicate=True),
    Output("status-msg", "children", allow_duplicate=True),
    Input("interval", "n_intervals"),
    State("store-steps", "data"),
    State("store-frame", "data"),
    State("sw-values", "value"),
    prevent_initial_call=True,
)
def tick(n_intervals, steps_json, frame, show_val):
    if not steps_json:
        return dash.no_update, dash.no_update, True, dash.no_update, dash.no_update, dash.no_update

    steps = json.loads(steps_json)
    frame = frame or 0

    if frame >= len(steps):
        return dash.no_update, frame, True, dash.no_update, dash.no_update, "EXECUTION COMPLETE"

    arr, colors, cmp, swp = steps[frame]
    show_labels = True if show_val and len(show_val) > 0 else False
    fig = make_figure(arr, colors, show_labels=show_labels)
    next_frame = frame + 1
    done = next_frame >= len(steps)
    msg = f"COMPLETE: {cmp} COMPARISONS, {swp} SWAPS" if done else f"STEP {next_frame} / {len(steps)}"

    return fig, next_frame, done, str(cmp), str(swp), msg

if __name__ == "__main__":
    app.run(debug=True)