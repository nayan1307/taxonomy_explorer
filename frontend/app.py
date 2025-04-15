import dash
from dash import dcc, html, Input, Output, State, ctx
import requests
from urllib.parse import urlencode, parse_qs

API_URL = "http://127.0.0.1:8000"

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Taxonomy Explorer"

# Overall layout for single-page routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
], style={"backgroundColor": "#f9f9f9", "color": "#000", "minHeight": "100vh", "padding": "20px"})


# Routing to either search or taxon detail page
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    State("url", "search")
)
def render_page(pathname, search):
    if pathname in ["/", "/search"]:
        query = parse_qs(search[1:]) if search else {}
        return build_search_ui(query)
    elif pathname.startswith("/taxon/"):
        tax_id = pathname.split("/")[-1]
        return build_taxon_page(tax_id, search)
    return html.Div("404 - Page not found", style={"textAlign": "center", "padding": "50px"})


# Build search page with keyword input, dropdown filter, and search results
def build_search_ui(query):
    keyword = query.get("keyword", [""])[0]
    mode = query.get("mode", ["contains"])[0]
    page = int(query.get("page", [1])[0])

    return html.Div([
        dcc.Store(id="search-state", data={"keyword": keyword, "mode": mode, "page": page}),
        html.H2("NCBI Taxonomy Search", style={"textAlign": "center", "marginBottom": "30px"}),

        # Input + Dropdown + Button
        html.Div([
            dcc.Input(
                id="search-input",
                type="text",
                placeholder="Enter keyword",
                value=keyword,
                style={"width": "400px", "padding": "10px", "fontSize": "16px"}
            ),
            dcc.Dropdown(
                id="search-mode",
                options=[
                    {"label": "Contains", "value": "contains"},
                    {"label": "Starts With", "value": "starts with"},
                    {"label": "Ends With", "value": "ends with"},
                ],
                value=mode,
                clearable=False,
                style={"width": "180px", "fontSize": "16px"}
            ),
            html.Button("Search", id="search-button", n_clicks=0,
                        style={"padding": "10px 30px", "fontSize": "16px",
                               "backgroundColor": "#007bff", "color": "white", "border": "none",
                               "borderRadius": "8px", "cursor": "pointer"})
        ], style={"display": "flex", "justifyContent": "center", "gap": "20px", "marginBottom": "30px"}),

        html.Div(id="search-results"),
        html.Div(id="pagination-controls", style={"textAlign": "center", "margin": "20px"}),
        html.Div(id="search-feedback", style={"textAlign": "center", "color": "#555"})
    ])


# Search trigger: Update URL
@app.callback(
    Output("url", "search"),
    Input("search-button", "n_clicks"),
    State("search-input", "value"),
    State("search-mode", "value"),
    prevent_initial_call=True
)
def trigger_search(n_clicks, keyword, mode):
    return f"?{urlencode({'keyword': keyword, 'mode': mode, 'page': 1})}"


# Pagination logic
@app.callback(
    Output("url", "search", allow_duplicate=True),
    Input("next-page-btn", "n_clicks"),
    Input("prev-page-btn", "n_clicks"),
    State("search-state", "data"),
    prevent_initial_call=True
)
def paginate(next_click, prev_click, state):
    page = state.get("page", 1)
    keyword = state.get("keyword", "")
    mode = state.get("mode", "contains")

    if ctx.triggered_id == "next-page-btn":
        page += 1
    elif ctx.triggered_id == "prev-page-btn" and page > 1:
        page -= 1

    return f"?{urlencode({'keyword': keyword, 'mode': mode, 'page': page})}"


# Render paginated search results
@app.callback(
    Output("search-results", "children"),
    Output("search-feedback", "children"),
    Output("pagination-controls", "children"),
    Output("search-state", "data"),
    Input("url", "search")
)
def display_results(search):
    if not search:
        return html.Div("Start typing a keyword to search the taxonomy database...",
                        style={"textAlign": "center", "padding": "20px", "fontSize": "18px", "color": "#777"}), "", "", {}

    query = parse_qs(search[1:])
    keyword = query.get("keyword", [""])[0]
    mode = query.get("mode", ["contains"])[0]
    page = int(query.get("page", [1])[0])

    if not keyword:
        return "", "", "", {}

    try:
        response = requests.get(f"{API_URL}/search", params={
            "keyword": keyword,
            "search_mode": mode,
            "page": page,
            "items_per_page": 10
        })

        if response.status_code != 200:
            return "", f"Error: {response.status_code}", "", {}

        data = response.json()
        if not data.get("results"):
            return "", "No matches found.", "", {}

        # Table of results
        table = html.Table([
            html.Thead(html.Tr([
                html.Th("Taxonomy ID", style={"width": "30%"}),
                html.Th("Name", style={"width": "35%"}),
                html.Th("Class", style={"width": "35%"})
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(dcc.Link(str(r["tax_id"]), href=f"/taxon/{r['tax_id']}{search}"), style={"textAlign": "center"}),
                    html.Td(r["name"], style={"textAlign": "center"}),
                    html.Td(r["class"], style={"textAlign": "center"})
                ]) for r in data["results"]
            ])
        ], style={"width": "80%", "margin": "auto", "border": "1px solid #ccc",
                  "borderCollapse": "collapse", "fontSize": "16px", "backgroundColor": "#fff"})

        # Pagination
        controls = html.Div([
            html.Button("Previous", id="prev-page-btn", n_clicks=0, disabled=(page == 1),
                        style={"marginRight": "15px", "padding": "6px 12px"}),
            html.Span(f"Page {page}", style={"fontWeight": "bold", "fontSize": "16px"}),
            html.Button("Next", id="next-page-btn", n_clicks=0,
                        style={"marginLeft": "15px", "padding": "6px 12px"})
        ])

        return table, f"Showing {len(data['results'])} of {data['total']} result(s).", controls, {
            "keyword": keyword, "mode": mode, "page": page
        }

    except Exception as e:
        return "", f"Error: {str(e)}", "", {}


# Taxon detail page showing children and name info
def build_taxon_page(tax_id, search=None):
    try:
        res = requests.get(f"{API_URL}/taxa", params={"tax_id": tax_id})
        if res.status_code != 200:
            return html.Div("Taxon not found.", style={"padding": "40px"})

        data = res.json()
        parent = data.get("parent")
        parent_link = (
            dcc.Link(f"{parent['scientific_name']} ({parent['tax_id']})", href=f"/taxon/{parent['tax_id']}{search or ''}",
                     style={"color": "#007bff"}) if parent else "None"
        )

        # Children table
        children = html.Div([
            html.H4("Children", style={"marginTop": "30px", "textAlign": "center"}),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Child Taxon", style={"width": "50%"}),
                    html.Th("Rank", style={"width": "50%"})
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(dcc.Link(child["scientific_name"], href=f"/taxon/{child['tax_id']}{search or ''}"), style={"textAlign": "center"}),
                        html.Td(child["rank"], style={"textAlign": "center"})
                    ]) for child in data["children"]
                ])
            ], style={"width": "80%", "margin": "auto", "border": "1px solid #ccc",
                      "borderCollapse": "collapse", "backgroundColor": "#ffffff", "color": "#000"})
        ]) if data["children"] else html.P("No children.", style={"textAlign": "center"})

        # Names table
        names = html.Div([
            html.H4("Names", style={"marginTop": "30px", "textAlign": "center"}),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Name", style={"width": "50%"}),
                    html.Th("Class", style={"width": "50%"})
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(n["name"], style={"textAlign": "center"}),
                        html.Td(n["class"], style={"textAlign": "center"})
                    ]) for n in data["names"]
                ])
            ], style={"width": "80%", "margin": "auto", "border": "1px solid #ccc",
                      "borderCollapse": "collapse", "backgroundColor": "#fff", "color": "#000"})
        ])

        # Final layout
        return html.Div([
            html.Div([
                html.A("Home", href="/", style={"fontSize": "16px", "fontWeight": "bold", "color": "#007bff"}),
                html.H2(f"Taxon Details: {data['tax_id']}", style={"marginTop": "20px", "textAlign": "center"}),
                html.P(f"Rank: {data['rank']}", style={"textAlign": "center"}),
                html.P(["Parent: ", parent_link], style={"textAlign": "center"}),
            ]),
            children,
            names,
            html.Br(),
            dcc.Link("Back to Search Results", href=f"/search{search or ''}",
                     style={"fontSize": "16px", "color": "#007bff", "fontWeight": "bold", "display": "block", "textAlign": "center", "marginTop": "20px"})
        ], style={"padding": "30px", "fontSize": "16px", "backgroundColor": "#f9f9f9",
                  "borderRadius": "10px", "boxShadow": "0 4px 8px rgba(0,0,0,0.05)", "maxWidth": "900px", "margin": "auto"})

    except Exception as e:
        return html.Div(f"Error: {str(e)}", style={"padding": "40px"})


# Launch Dash server
if __name__ == "__main__":
    app.run(debug=True)
