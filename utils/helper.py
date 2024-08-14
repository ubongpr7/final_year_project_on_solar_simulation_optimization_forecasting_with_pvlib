import plotly.express as px
import plotly.graph_objects as go

def generate_plot(y,df, plot_type='line', title='Plot', labels=None, color='#1f77b4'):
    """
    Generate a Plotly graph based on the provided parameters.

    Parameters:
    - x: Data for the x-axis
    - y: Data for the y-axis (or values for pie chart)
    - plot_type: Type of plot ('line', 'scatter', 'bar', 'area', 'histogram', 'box', 'violin', 'pie', 'density_contour', 'funnel')
    - title: Title of the plot
    - labels: Dictionary with 'x' and 'y' keys for axis labels
    - color: Color of the plot elements

    Returns:
    - fig: Plotly figure object
    """
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    df['month'] = df.index.month_name()
    monthly_avg = df.groupby('month')[y].mean().reindex(month_order)
    print('monthly_avg: ',monthly_avg.head())
    if labels is None:
        labels = {'x': 'X-Axis', 'y': 'Y-Axis'}

    if plot_type == 'line':
        fig = px.line(df,x=df.index, y=df[y],color='month',color_discrete_sequence=[color], title=title, labels=labels)
        fig.update_traces(line=dict(colors=color))

    elif plot_type == 'scatter':
        fig = px.scatter(df,x=df.index,color_discrete_sequence=[color],color='month', y=df[y], title=title, labels=labels)
        fig.update_traces(marker=dict(colors=color))
        

    elif plot_type == 'area':
        fig = px.area(df, x=df.index,color='month',color_discrete_sequence=[color], y=df[y], title=title, labels=labels)
        fig.update_traces(line=dict(colors=color))

    # elif plot_type == 'bar':
    #     fig = px.bar(df, x=df.index,color_discrete_sequence=[color],color='month', y=y,title=title, labels=labels,barmode='group')
    #     fig.update_traces(marker=dict(color=color))
        

    elif plot_type == 'bar':
        fig = px.bar(monthly_avg, x='month',color_discrete_sequence=[color],color='month', y=y,title=title, labels=labels,barmode='group')
        fig.update_traces(marker=dict(color=color))
        

    elif plot_type == 'histogram':
        fig = px.histogram(df, x=y,nbins=20, title=title, labels={labels.get('x', 'X-Axis')})
        fig.update_traces(marker=dict(color=color))
        

    elif plot_type == 'box':
        fig = px.box(df,x='month',y=y,title=title,color='month',color_discrete_sequence=[color] labels=labels)
        fig.update_traces(marker=dict(colors=color))
        

    elif plot_type == 'violin':
        fig = px.violin(df,x='month', y=y,color='month',color_discrete_sequence=[color], title=title, labels=labels)
        fig.update_traces(marker=dict(colors=color))
        
    elif plot_type == 'pie':
        fig = px.pie(monthly_avg,values=y, names='month', title=title)
        fig.update_traces(marker=dict(colors=[color]))

    elif plot_type == 'heatmap':
        z = df.pivot(index='month', columns='month', values=y)
        fig = px.imshow(z, color_continuous_scale='Viridis', title='Heatmap')

    elif plot_type == 'density_contour':
        fig = px.density_contour(df, title=title, labels=labels)
        fig.update_traces(contours_coloring="fill", colorscale=[[0, color], [1, color]])

    elif plot_type == 'funnel':
        fig = px.funnel(df, title=title, labels=labels)
        fig.update_traces(marker=dict(color=color))
        

    else:
        raise ValueError(f"Unknown plot_type: {plot_type}")
    
    fig.update_layout(
        title=title,
        xaxis_title=labels.get('x', 'X-Axis'),
        yaxis_title=labels.get('y', 'Y-Axis'),
        height=600,
    )

    return fig
import pandas as pd
import plotly.express as px

def df_sample_to_bootstrap_cards(df, x_col, y_col, title='Sample Data'):
    # Take 10 random samples
    sample_df = df[[x_col, y_col]].sample(10)

    # Initialize HTML for Bootstrap cards
    html_output = '<div class="row">'

    # Loop through the sample and create cards
    for _, row in sample_df.iterrows():
        x_val = row[x_col]
        y_val = row[y_col]
        
        # Create the plot using Plotly
        fig = px.scatter(x=[x_val], y=[y_val], title=f'{x_col}: {x_val}, {y_col}: {y_val}')
        fig.update_traces(marker=dict(size=12))
        
        # Convert Plotly figure to HTML
        plot_html = fig.to_html(full_html=False)
        
        # Create Bootstrap card
        card_html = f'''
        <div class="col-md-4">
            <div class="card mb-4 shadow-sm">
                <div class="card-body">
                    <h5 class="card-title">{x_col}: {x_val}, {y_col}: {y_val}</h5>
                    <div>{plot_html}</div>
                </div>
            </div>
        </div>
        '''
        html_output += card_html

    html_output += '</div>'
    
    return html_output

