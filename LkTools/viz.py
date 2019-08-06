if 'pd' not in globals():
    import pandas as pd
if 'np' not in globals():
    import numpy as np
if 'iplot' not in globals():
    import plotly.figure_factory as ff
    import plotly.graph_objs as go


def pltcat(c, t, sub, fillna=None, min_diff=0.001, normalize=True):
    '''
        args: 
            c: string: the category to crosstab
            t: string: the target variable
            sub: DataFrame: the dataset
            fillna: obj: anything you want to fill nan values with
            min_diff: float: the minimum difference in between response rates to plot (good for a lot of categories)
            normalize: bool: plot normalized values or counts
    '''
    
    if fillna is not None:
        sub[c] = sub[c].fillna(fillna)
        
    x = pd.crosstab(sub[c], sub[t], normalize=normalize).rename(columns={0:'neg', 1:'pos'}).reset_index()
    x['diff'] = x.pos-x.neg
    x = x.sort_values(by='diff')        
    
    x = x.loc[np.abs(x['diff']) > min_diff]
        
    layout = go.Layout(
        title=c, 
        legend_orientation="h"
    )
    
    fig = go.Figure([
        go.Bar(name='negative', x=x[c], y=x.neg),
        go.Bar(name='positive', x=x[c], y=x.pos)
    ], layout)
    
    return x, fig