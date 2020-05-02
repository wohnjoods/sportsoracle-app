import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

def Header():
    search_bar = dbc.Row(
        [
            dbc.Col(dbc.Input(type="search", placeholder="Search")),
            dbc.Col(
                dbc.Button("Search", color="primary", className="ml-2"),
                width="auto",
            ),
        ],
        no_gutters=True,
        className="ml-auto flex-nowrap mt-3 mt-md-0",
        align="center",
    )


    navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                        html.A([
                            html.Img(src='/assets/logo1-crop-rect.png', height="78px")
                        #dbc.Col(dbc.NavbarBrand("Navbar", className="ml-2")),
                        #dbc.Col(dbc.NavItem(dbc.NavLink(
                        #    "Page 1", href="#"), className="btn-primary")),
                        ],href='/'),
                        dbc.Nav(
                            [
                                dbc.NavItem(dbc.NavLink(
                                    "Boxscores", href="/ncaab/boxscore/")),
                                dbc.NavItem(dbc.NavLink(
                                    "Average Stats", href="/ncaab/average-stats/")),
                                dbc.DropdownMenu(
                                    [dbc.DropdownMenuItem(
                                        "Rankings", href="/ncaab/rank/"), dbc.DropdownMenuItem("Rank Accuracy", href= "/ncaab/rank/accuracy/")],
                                    label="Rankings",
                                    nav=True,
                                ),
                                dbc.DropdownMenu(
                                    [dbc.DropdownMenuItem(
                                        "Spread Projections", href="/ncaab/betting/spread/predictions/"), dbc.DropdownMenuItem("Spread Accuracy", href="/ncaab/betting/spread/accuracy/")],
                                    label="Spread",
                                    nav=True,
                                ),
                                dbc.DropdownMenu(
                                    [dbc.DropdownMenuItem(
                                        "Total Projections", href="/ncaab/betting/total/predictions/"), dbc.DropdownMenuItem("Total Accuracy", href="/ncaab/betting/total/accuracy/")],
                                    label="Total",
                                    nav=True,
                                ),
                                dbc.DropdownMenu(
                                    [dbc.DropdownMenuItem(
                                        "Moneyline Projections", href="/ncaab/betting/moneyline/predictions/"), dbc.DropdownMenuItem("Moneyline Accuracy", href="/ncaab/betting/moneyline/accuracy/")],
                                    label="Moneyline",
                                    nav=True,
                                ),
                            ],
                            justified=True,
                            pills=True,
                        ),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/ncaab/index",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
    ],
    color="dark",
    dark=True,
    sticky = 'top',
    )
    return navbar
    #return get_logo(), html.Br([]), get_menu()
        #get_header(),
        


#def get_logo():
#    logo = html.Div([
#
#        html.Div([
#            html.Img(src='assets/logo1-crop-rect.png',
#                     height='78', width='120')
#        ], className="ten columns padded"),

#    ], className="row gs-header")
#    return logo
def get_logo():
    logo = html.Img(src='assets/logo1-crop-rect.png',
                   height='78', width='120')
    return logo


def get_header():
    header = html.Div([

        html.Div([
            html.H5(
                'Sports Oracle')
        ], className="twelve columns padded")

    ], className="row gs-header gs-text-header")
    return header


def get_menu():
    menu = html.Div([

        dcc.Link('Boxscores   ',
                 href='/ncaab/boxscore/', className="tab first"),

        dcc.Link('Average Stats   ',
                 href='/ncaab/average-stats/', className="tab"),

        dcc.Link('Rankings  ',
                 href='/ncaab/rank/', className="tab"),

        dcc.Link('Ranking Accuracy   ', href='/ncaab/rank/accuracy/',
                 className="tab"),

        dcc.Link('Spread Projections  ',
                 href='/ncaab/betting/spread/predictions/', className="tab"),

        dcc.Link('Total Projections   ',
                 href='/ncaab/betting/total/predictions/', className="tab"),

        dcc.Link('Moneyline Projections   ',
                 href='/ncaab/betting/moneyline/predictions/', className="tab"),
        dcc.Link('Spread Accuracy   ',
                 href='/ncaab/betting/spread/accuracy/', className="tab"),

        dcc.Link('Total Accuracy   ',
                 href='/ncaab/betting/total/accuracy/', className="tab"),

        dcc.Link('Moneyline Accuracy   ',
                 href='/ncaab/betting/moneyline/accuracy/', className="tab")


    ], className="row ")
    return menu
