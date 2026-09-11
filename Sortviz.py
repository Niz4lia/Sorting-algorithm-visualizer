import random
import dash
from dash import dcc, html, Input, Output, State, clientside_callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

app = dash.Dash(
    __name__,
    title="Sortviz by Nizalia",
    external_stylesheets=[
        dbc.themes.DARKLY,
        dbc.icons.FONT_AWESOME
    ]
)
server = app.server

# ── Color Palette Definitions ───────────────────────────────────────────────
THEMES = {
    "dark": {
        "bg": "#090D16",
        "bg_gradient": "radial-gradient(circle at 50% 0%, #1E1B4B 0%, #090D16 70%)",
        "card_bg": "rgba(30, 41, 59, 0.7)",
        "text": "#F8FAFC",
        "text_muted": "#94A3B8",
        "border": "rgba(255, 255, 255, 0.1)",
        "grid": "rgba(255, 255, 255, 0.05)",
        "colors": {
            "default": "#6366F1",
            "compare": "#F43F5E",
            "swap": "#F59E0B",
            "sorted": "#10B981",
            "pivot": "#A855F7",
        }
    },
    "light": {
        "bg": "#F8FAFC",
        "bg_gradient": "radial-gradient(circle at 50% 0%, #E0E7FF 0%, #F8FAFC 70%)",
        "card_bg": "rgba(255, 255, 255, 0.85)",
        "text": "#0F172A",
        "text_muted": "#64748B",
        "border": "rgba(0, 0, 0, 0.08)",
        "grid": "rgba(0, 0, 0, 0.05)",
        "colors": {
            "default": "#4F46E5",
            "compare": "#E11D48",
            "swap": "#D97706",
            "sorted": "#059669",
            "pivot": "#7C3AED",
        }
    }
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
        steps.append({"arr": arr[:], "colors": colors[:], "cmp": cmp[0], "swp": swp[0]})

    snapshot()

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

# ── Figure Builder ────────────────────────────────────────────────────────────
def make_figure(arr, colors, theme_key="dark", show_labels=True):
    t = THEMES[theme_key]
    col_map = t["colors"]
    bar_colors = [col_map.get(c, col_map["default"]) for c in colors]

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
        bar_kwargs["textfont"] = dict(color=t["text_muted"], size=10, family="Inter, sans-serif")

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
            gridcolor=t["grid"],
            zeroline=False,
            range=[0, max(arr) + 15] if arr else [0, 100]
        ),
        bargap=0.18,
        height=360,
    )
    return fig

# ── App Layout ───────────────────────────────────────────────────────────────
app.layout = html.Div(
    id="main-container",
    style={
        "backgroundColor": THEMES["dark"]["bg"],
        "backgroundImage": THEMES["dark"]["bg_gradient"],
        "minHeight": "100vh",
        "color": THEMES["dark"]["text"],
        "padding": "40px 16px",
        "fontFamily": "Inter, system-ui, sans-serif",
        "transition": "all 0.3s ease"
    },
    children=[
        dbc.Container(
            [
                dcc.Store(id="store-steps"),
                dcc.Store(id="store-orig"),
                dcc.Store(id="store-theme", data="dark"),
                dcc.Store(id="store-trigger", data=0),

                # App Header
                html.Div(
                    className="d-flex justify-content-between align-items-center mb-4",
                    children=[
                        html.Div(
                            children=[
                                html.H1(
                                    "SORTVIZ",
                                    style={
                                        "fontSize": "38px",
                                        "fontWeight": "900",
                                        "letterSpacing": "2px",
                                        "background": "linear-gradient(90deg, #818CF8, #C084FC, #F43F5E)",
                                        "WebkitBackgroundClip": "text",
                                        "WebkitTextFillColor": "transparent",
                                        "margin": "0 0 4px 0",
                                    },
                                ),
                                html.P("Sorting Visualizer and Real-time algorithmic execution & complexity profiler", id="sub-title", style={"color": THEMES["dark"]["text_muted"], "fontSize": "15px", "margin": "0"}),
                            ]
                        ),
                        dbc.Button(
                            html.I(className="fas fa-sun", id="theme-icon"),
                            id="btn-theme",
                            color="dark",
                            outline=True,
                            className="p-3 rounded-circle",
                            style={"width": "48px", "height": "48px", "display": "flex", "alignItems": "center", "justifyContent": "center"}
                        )
                    ]
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
                                                style={"backgroundColor": "rgba(15, 23, 42, 0.5)", "color": "#000", "border": "none", "borderRadius": "8px"},
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
                            html.Hr(id="hr-line", style={"borderColor": THEMES["dark"]["border"], "margin": "16px 0"}),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Checklist(
                                            options=[{"label": " Show Bar Values", "value": True}],
                                            value=[True],
                                            id="sw-values",
                                            switch=True,
                                            style={"color": THEMES["dark"]["text_muted"], "fontSize": "13px", "fontWeight": "600"}
                                        ),
                                        width=6,
                                        className="d-flex align-items-center"
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Button("New Array", id="btn-gen", color="secondary", outline=True, className="me-2 px-4 fw-bold", style={"borderRadius": "8px"}),
                                            dbc.Button("▶ Run Algorithm", id="btn-start", color="primary", className="me-2 px-4 fw-bold", style={"borderRadius": "8px", "background": "linear-gradient(90deg, #6366F1, #8B5CF6)", "border": "none"}),
                                            dbc.Button("↺ Refresh", id="btn-refresh", color="dark", className="px-3 fw-bold", style={"borderRadius": "8px"}),
                                        ],
                                        width=6,
                                        className="d-flex justify-content-end",
                                    ),
                                ],
                                className="align-items-center"
                            ),
                        ]
                    ),
                    id="card-controls",
                    style={
                        "backgroundColor": THEMES["dark"]["card_bg"],
                        "backdropFilter": "blur(12px)",
                        "border": f"1px solid {THEMES['dark']['border']}",
                        "borderRadius": "16px",
                        "boxShadow": "0 20px 25px -5px rgba(0, 0, 0, 0.3)",
                        "position": "relative",
                        "zIndex": 1050,
                        "overflow": "visible"
                    },
                    className="mb-4",
                ),

                # Metrics Dashboard
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.Div("COMPARISONS", style={"fontSize": "11px", "color": THEMES["dark"]["text_muted"], "fontWeight": "700", "letterSpacing": "1px"}),
                                    html.H2(id="stat-cmp", children="0", style={"fontSize": "32px", "fontWeight": "800", "color": "#F43F5E", "margin": "4px 0 0"}),
                                ]), id="card-stat-1", style={"backgroundColor": THEMES["dark"]["card_bg"], "border": f"1px solid {THEMES['dark']['border']}", "borderRadius": "16px"}, className="text-center mb-3"
                            ), width=3
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.Div("SWAPS / WRITES", style={"fontSize": "11px", "color": THEMES["dark"]["text_muted"], "fontWeight": "700", "letterSpacing": "1px"}),
                                    html.H2(id="stat-swp", children="0", style={"fontSize": "32px", "fontWeight": "800", "color": "#F59E0B", "margin": "4px 0 0"}),
                                ]), id="card-stat-2", style={"backgroundColor": THEMES["dark"]["card_bg"], "border": f"1px solid {THEMES['dark']['border']}", "borderRadius": "16px"}, className="text-center mb-3"
                            ), width=3
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.Div("TIME COMPLEXITY", style={"fontSize": "11px", "color": THEMES["dark"]["text_muted"], "fontWeight": "700", "letterSpacing": "1px"}),
                                    html.H2(id="stat-tc", children="O(n log n)", style={"fontSize": "26px", "fontWeight": "800", "color": "#818CF8", "margin": "8px 0 0"}),
                                ]), id="card-stat-3", style={"backgroundColor": THEMES["dark"]["card_bg"], "border": f"1px solid {THEMES['dark']['border']}", "borderRadius": "16px"}, className="text-center mb-3"
                            ), width=3
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.Div("SPACE COMPLEXITY", style={"fontSize": "11px", "color": THEMES["dark"]["text_muted"], "fontWeight": "700", "letterSpacing": "1px"}),
                                    html.H2(id="stat-sc", children="O(log n)", style={"fontSize": "26px", "fontWeight": "800", "color": "#10B981", "margin": "8px 0 0"}),
                                ]), id="card-stat-4", style={"backgroundColor": THEMES["dark"]["card_bg"], "border": f"1px solid {THEMES['dark']['border']}", "borderRadius": "16px"}, className="text-center mb-3"
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
                                id="legend-container",
                                className="d-flex justify-content-center mt-3 pt-3",
                                style={"borderTop": f"1px solid {THEMES['dark']['border']}"}
                            ),
                        ]
                    ),
                    id="card-graph",
                    style={"backgroundColor": THEMES["dark"]["card_bg"], "border": f"1px solid {THEMES['dark']['border']}", "borderRadius": "16px"},
                    className="mb-3",
                ),

                # Status Indicator
                html.Div(
                    id="status-msg",
                    children="Select settings and click ▶ Run Algorithm",
                    style={"textAlign": "center", "color": THEMES["dark"]["text_muted"], "fontSize": "13px", "fontWeight": "600", "letterSpacing": "0.5px"},
                ),
            ],
            style={"maxWidth": "1000px"}
        )
    ]
)

# ── Callbacks ─────────────────────────────────────────────────────────────────

# Theme Switching
@app.callback(
    Output("main-container", "style"),
    Output("sub-title", "style"),
    Output("card-controls", "style"),
    Output("card-stat-1", "style"),
    Output("card-stat-2", "style"),
    Output("card-stat-3", "style"),
    Output("card-stat-4", "style"),
    Output("card-graph", "style"),
    Output("legend-container", "children"),
    Output("legend-container", "style"),
    Output("hr-line", "style"),
    Output("status-msg", "style"),
    Output("theme-icon", "className"),
    Output("store-theme", "data"),
    Input("btn-theme", "n_clicks"),
    State("store-theme", "data")
)
def toggle_theme(n_clicks, current_theme):
    theme_key = "light" if (n_clicks and current_theme == "dark") else "dark"
    t = THEMES[theme_key]

    main_style = {
        "backgroundColor": t["bg"],
        "backgroundImage": t["bg_gradient"],
        "minHeight": "100vh",
        "color": t["text"],
        "padding": "40px 16px",
        "fontFamily": "Inter, system-ui, sans-serif",
        "transition": "all 0.3s ease"
    }

    sub_title_style = {"color": t["text_muted"], "fontSize": "15px", "margin": "0"}

    card_style = {
        "backgroundColor": t["card_bg"],
        "backdropFilter": "blur(12px)",
        "border": f"1px solid {t['border']}",
        "borderRadius": "16px",
        "boxShadow": "0 20px 25px -5px rgba(0, 0, 0, 0.15)",
        "transition": "all 0.3s ease"
    }

    controls_style = {
        **card_style,
        "position": "relative",
        "zIndex": 1050,
        "overflow": "visible"
    }

    legend_items = [
        html.Span(
            [
                html.Span(style={
                    "width": "10px", "height": "10px", "borderRadius": "50%",
                    "backgroundColor": v, "display": "inline-block", "marginRight": "6px",
                    "boxShadow": f"0 0 10px {v}"
                }),
                k.capitalize(),
            ],
            style={"marginRight": "24px", "fontSize": "12px", "color": t["text_muted"], "display": "inline-flex", "alignItems": "center"}
        )
        for k, v in t["colors"].items()
    ]

    legend_style = {"borderTop": f"1px solid {t['border']}"}
    hr_style = {"borderColor": t["border"], "margin": "16px 0"}
    status_style = {"textAlign": "center", "color": t["text_muted"], "fontSize": "13px", "fontWeight": "600", "letterSpacing": "0.5px"}
    icon_class = "fas fa-moon" if theme_key == "light" else "fas fa-sun"

    return (
        main_style, sub_title_style, controls_style, card_style, card_style,
        card_style, card_style, card_style, legend_items, legend_style,
        hr_style, status_style, icon_class, theme_key
    )


# Generate New Array
@app.callback(
    Output("store-orig", "data"),
    Output("store-steps", "data"),
    Output("graph", "figure"),
    Output("stat-cmp", "children"),
    Output("stat-swp", "children"),
    Output("stat-tc", "children"),
    Output("stat-sc", "children"),
    Output("status-msg", "children"),
    Input("btn-gen", "n_clicks"),
    Input("sl-size", "value"),
    Input("dd-algo", "value"),
    Input("store-theme", "data"),
    State("sw-values", "value"),
)
def new_array(n_clicks, size, algo, theme_key, show_val):
    arr = [random.randint(10, 99) for _ in range(size)]
    colors = ["default"] * size
    show_labels = True if show_val and len(show_val) > 0 else False
    fig = make_figure(arr, colors, theme_key=theme_key, show_labels=show_labels)
    tc = COMPLEXITY[algo]["time"]
    sc = COMPLEXITY[algo]["space"]
    return arr, None, fig, "0", "0", tc, sc, "Array initialized. Click ▶ Run Algorithm to start."


# Refresh Button Browser Page Reload Callback
clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            window.location.reload();
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("btn-refresh", "id"),
    Input("btn-refresh", "n_clicks"),
    prevent_initial_call=True
)


# Start Sorting Engine (Triggers JS Loop)
@app.callback(
    Output("store-steps", "data", allow_duplicate=True),
    Output("store-trigger", "data"),
    Input("btn-start", "n_clicks"),
    State("store-orig", "data"),
    State("dd-algo", "value"),
    State("store-trigger", "data"),
    prevent_initial_call=True,
)
def start_sort(n_clicks, orig_data, algo, trigger_val):
    if not orig_data:
        return dash.no_update, dash.no_update

    steps = generate_steps(orig_data, algo)
    return steps, (trigger_val or 0) + 1


# Pure JavaScript Animation Engine
clientside_callback(
    """
    function(trigger, steps, theme_key, show_val, speed) {
        if (!steps || steps.length === 0) {
            return;
        }

        // Cancel any previous running animation timer
        if (window.animTimer) {
            clearInterval(window.animTimer);
            window.animTimer = null;
        }

        var frameIdx = 0;
        var intervalMs = Math.max(10, Math.floor(200 / Math.pow(1.5, speed - 1)));

        window.animTimer = setInterval(function() {
            if (frameIdx >= steps.length) {
                // STOP IMMEDIATELY
                clearInterval(window.animTimer);
                window.animTimer = null;

                var lastStep = steps[steps.length - 1];
                document.getElementById("stat-cmp").innerText = String(lastStep.cmp);
                document.getElementById("stat-swp").innerText = String(lastStep.swp);
                document.getElementById("status-msg").innerText = "COMPLETE: " + lastStep.cmp + " COMPARISONS, " + lastStep.swp + " SWAPS";
                return;
            }

            var step = steps[frameIdx];
            var theme = (theme_key === 'light') ? {
                grid: 'rgba(0,0,0,0.05)',
                text_muted: '#64748B',
                colors: {
                    default: '#4F46E5',
                    compare: '#E11D48',
                    swap: '#D97706',
                    sorted: '#059669',
                    pivot: '#7C3AED'
                }
            } : {
                grid: 'rgba(255,255,255,0.05)',
                text_muted: '#CBD5E1',
                colors: {
                    default: '#6366F1',
                    compare: '#F43F5E',
                    swap: '#F59E0B',
                    sorted: '#10B981',
                    pivot: '#A855F7'
                }
            };

            var barColors = step.colors.map(function(c) {
                return theme.colors[c] || theme.colors.default;
            });

            var showLabels = show_val && show_val.length > 0;
            var barData = {
                x: Array.from(Array(step.arr.length).keys()),
                y: step.arr,
                type: 'bar',
                marker: { color: barColors, line: { width: 0 }, cornerradius: '30%' }
            };

            if (showLabels) {
                barData.text = step.arr;
                barData.textposition = 'outside';
                barData.textfont = { color: theme.text_muted, size: 10, family: 'Inter, sans-serif' };
            }

            var maxVal = Math.max.apply(null, step.arr) + 15;
            var layout = {
                margin: { l: 10, r: 10, t: 25, b: 10 },
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)',
                showlegend: false,
                uirevision: 'constant',
                xaxis: { showticklabels: false, showgrid: false, zeroline: false },
                yaxis: { showgrid: true, gridcolor: theme.grid, zeroline: false, range: [0, maxVal] },
                bargap: 0.18,
                height: 360
            };

            Plotly.react('graph', [barData], layout, {displayModeBar: false});

            document.getElementById("stat-cmp").innerText = String(step.cmp);
            document.getElementById("stat-swp").innerText = String(step.swp);
            document.getElementById("status-msg").innerText = "STEP " + (frameIdx + 1) + " / " + steps.length;

            frameIdx++;
        }, intervalMs);

        return window.dash_clientside.no_update;
    }
    """,
    Output("store-trigger", "id"),
    Input("store-trigger", "data"),
    State("store-steps", "data"),
    State("store-theme", "data"),
    State("sw-values", "value"),
    State("sl-speed", "value"),
    prevent_initial_call=True
)

if __name__ == "__main__":
    app.run(debug=True)
