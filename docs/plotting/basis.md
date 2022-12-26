# Plotting

## Plotting indicators
Indicators and associated signals can be easily plotted using the 
`plot_indicator(ctx, name, x, y, signals)` keyword.

Where:
- `name`: name of the indicator on the chart 
- `x`: values to use for the x axis
- `y`: values to use for the y axis
- `signal`: (optional) x values for which a signal is fired

Example where the goal is to plot the value of the rsi indicator from 
the [example script](../../#script).
``` python
await op.plot_indicator(ctx, "RSI", time_values, indicator_values, signal_times)
```

## Plotting anything

Anything can be plotted using the `plot(ctx, name, ...)` keyword. 
The plot arguments are converted into [plotly](https://plotly.com/javascript/) charts parameters.

Where:
- `name`: name of the indicator on the chart 

Optional arguments:
- `x`: values to use for the x axis
- `y`: values to use for the y axis
- `z`: values to use for the z axis
- `text`: point labels
- `mode`: plotly mode ("lines", "markers", "lines+markers", "lines+markers+text", "none")
- `chart`: "main-chart" or "sub-chart" (default is "sub-chart")
- `own_yaxis`: when True, uses an independent y axis for this plot (default is False)
- `color`: color the of plot
- `open`: open values for a candlestick chart
- `high`: high values for a candlestick chart
- `low`: low values for a candlestick chart
- `close`: close values for a candlestick chart
- `volume`: volume values for a candlestick chart
- `low`: low values for a candlestick chart

Example:
``` python
await op.plot(ctx, "RSI", x=time_values, y=indicator_values, mode="markers")
```
