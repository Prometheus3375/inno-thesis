import plotly.graph_objects as go

from geometry.figures import Sector


# TODO: add slots to classes


def draw_sector(sector: Sector):
    center = sector.center
    view_size = sector.r * 1.5

    fig = go.Figure()
    fig.add_shape(
        **sector.circle.as_plotly_shape(),
        line_color='Green',
    )
    fig.add_shape(
        **sector.as_plotly_shape(),
        line_color='RoyalBlue',
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        range=[center.x - view_size, center.x + view_size]
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        scaleanchor='x',
        scaleratio=1,
        range=[center.y - view_size, center.y + view_size]
    )
    # fig.update_layout(width=900, height=900, )
    fig.show()
