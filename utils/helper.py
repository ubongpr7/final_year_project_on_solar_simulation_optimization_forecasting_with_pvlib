import plotly.express as px
import plotly.colors as colors
import pandas as pd


def df_sample_to_bootstrap_cards(df):
    html_table = df.to_html(classes='table table-striped')

    # Wrap the table in a div with overflow styling
    html = f'''
    <div style="overflow-x: auto;">
        {html_table}
        {df.shape}
    </div>
    '''
    return html

def generate_plot(y, df, plot_type='line',location=None, labels=None, color='#1f77b4'):
    """
    Generate a Plotly graph based on the provided parameters.

    Parameters:
    - y: Data for the y-axis (or values for pie chart)
    - df: DataFrame containing the data
    - plot_type: Type of plot ('line', 'scatter', 'bar', 'area', 'histogram', 'box', 'violin', 'pie', 'density_contour', 'funnel')
    - color: Color of the plot elements

    Returns:
    - fig: Plotly figure object
    """
    # Assigning month names based on the index
    df['month'] = df.index.month_name()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)

    # Create a dictionary mapping month names to colors
    color_scale = colors.qualitative.Set1
    month_colors = dict(zip(df['month'].unique(), color_scale))

    # Calculate monthly average once
    # monthly_avg = df.groupby('month')[y].mean().reset_index()
    monthly_avg = df.groupby('month', observed=False)[y].mean().reset_index()

    # Titles and labels based on the plot type and y variable
    title_dict = {
        'line': f"Trend of {y.capitalize()} Over Time ",
        'scatter': f"Scatter Plot of {y.capitalize()} Over Time",
        'area': f"Cumulative {y.capitalize()} Over Time",
        'bar': f"Monthly Average {y.capitalize()}",
        'histogram': f"Distribution of {y.capitalize()}",
        'box': f"Monthly Distribution of {y.capitalize()}",
        'violin': f"Monthly Distribution of {y.capitalize()}",
        'pie': f"Proportion of Monthly Average {y.capitalize()}",
        'heatmap': f"Heatmap of {y.capitalize()} by Month",
        'density_contour': f"Density Contour of {y.capitalize()} Over Time",
        'funnel': f"Funnel Plot of {y.capitalize()} Over Time"
    }

    label_dict = {
        'line': {'x': 'Date', 'y': f'{y.capitalize()}'},
        'scatter': {'x': 'Date', 'y': f'{y.capitalize()}'},
        'area': {'x': 'Date', 'y': f'Cumulative {y.capitalize()}'},
        'bar': {'x': 'Month', 'y': f'Average {y.capitalize()}'},
        'histogram': {'x': f'{y.capitalize()}', 'y': 'Frequency of Occurence  of {y.capitalize()}'},
        'box': {'x': 'Month', 'y': f'{y.capitalize()}'},
        'violin': {'x': 'Month', 'y': f'{y.capitalize()}'},
        'pie': {'x': 'Month', 'y': f'Proportion of {y.capitalize()}'},
        'heatmap': {'x': 'Month', 'y': 'Month'},
        'density_contour': {'x': 'Date', 'y': f'{y.capitalize()}'},
        'funnel': {'x': 'Date', 'y': f'{y.capitalize()}'}
    }

    title = title_dict.get(plot_type, f"{y.capitalize()} vs Time for {location}")
    labels = label_dict.get(plot_type, {'x': 'Date', 'y': y.capitalize()})

    # Create plots
    if plot_type == 'line':
        fig = px.line(df, x=df.index, y=df[y], title=title, labels=labels)
        fig.update_traces(line=dict(color=color))
    elif plot_type == 'scatter':
        fig = px.scatter(df, x=df.index, y=df[y], color='month', color_discrete_map=month_colors, title=title, labels=labels)
    elif plot_type == 'area':
        fig = px.area(df, x=df.index, y=df[y], title=title, labels=labels)
        fig.update_traces(line=dict(color=color))
    elif plot_type == 'bar':
        fig = px.bar(monthly_avg, x='month',color='month', color_discrete_map=month_colors, y=y, title=title, labels=labels)
        # fig.update_traces(line=dict(color=color))

    elif plot_type == 'histogram':
        fig = px.histogram(df, x=y, nbins=20, title=title, labels=labels)
    elif plot_type == 'box':
        fig = px.box(df, x='month', y=y, color='month', color_discrete_map=month_colors, title=title, labels=labels)
    elif plot_type == 'violin':
        fig = px.violin(df, x='month', y=y, color='month', color_discrete_map=month_colors, title=title, labels=labels)
    elif plot_type == 'pie':
        fig = px.pie(monthly_avg, values=y, names='month', title=title)
    elif plot_type == 'heatmap':
        z = df.pivot_table(index='month', columns='month', values=y)
        fig = px.imshow(z, color_continuous_scale='Viridis', title=title)
    elif plot_type == 'density_contour':
        fig = px.density_contour(df, x=df.index, y=df[y], title=title, labels=labels)
        fig.update_traces(contours_coloring="fill", colorscale=[[0, color], [1, color]])
    elif plot_type == 'funnel':
        fig = px.funnel(df, x=df.index, y=df[y], title=title, labels=labels)
        fig.update_traces(marker=dict(color=color))
    else:
        raise ValueError(f"Unknown plot_type: {plot_type}")

    # Update layout
    fig.update_layout(
        title=f"{title} for {location} \n Source: PVGIS",
        xaxis_title=labels.get('x', 'X-Axis'),
        yaxis_title=labels.get('y', 'Y-Axis'),
        height=600,
    )

    return fig
