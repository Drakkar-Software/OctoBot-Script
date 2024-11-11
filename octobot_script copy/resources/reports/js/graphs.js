$(document).ready(function() {

const CANDLES_PLOT_SOURCES = ["open", "high", "low", "close"];
const ALL_PLOT_SOURCES = ["y", "z", "volume"].concat(CANDLES_PLOT_SOURCES);

const getPlotlyConfig = () => {
    return {
        scrollZoom: true,
        modeBarButtonsToRemove: ["select2d", "lasso2d", "toggleSpikelines"],
        responsive: true,
        showEditInChartStudio: false,
        displaylogo: false // no logo to avoid 'rel="noopener noreferrer"' security issue (see https://webhint.io/docs/user-guide/hints/hint-disown-opener/)
    };
}

const _getChartedElements = (chartDetails, yAxis, xAxis, chartIdentifier, plotOnlyY) => {
    const chartedElements = {
        x: chartDetails.x,
        mode: chartDetails.mode,
        type: chartDetails.kind,
        text: chartDetails.text,
        name: `${chartDetails.title}${chartIdentifier}`,
        user_title: chartDetails.title,
    }
    chartedElements.line = {
        shape: chartDetails.line_shape
    }
    const markerAttributes = ["color", "size", "opacity", "line", "symbol"];
    chartedElements.marker = {};
    markerAttributes.forEach(function (attribute) {
        if (chartDetails[attribute] !== null) {
            chartedElements.marker[attribute] = chartDetails[attribute];
        }
    });
    if (plotOnlyY) {
        chartedElements.y = chartDetails.y;
    } else {
        ALL_PLOT_SOURCES.forEach(function (element) {
            if (chartDetails[element] !== null) {
                chartedElements[element] = chartDetails[element]
            }
        })
    }
    if (xAxis > 1) {
        chartedElements.xaxis = `x${xAxis}`
    }
    chartedElements.yaxis = `y${yAxis}`
    return chartedElements;
}

const _createOrAdaptChartedElements = (chartDetails, yAxis, xAxis, chartIdentifier) => {
    const createdChartedElements = [];
    if(chartDetails.x === null){
        return createdChartedElements;
    }
    createdChartedElements.push(
        _getChartedElements(chartDetails, yAxis, xAxis, chartIdentifier, false)
    );
    return createdChartedElements;
}

const createChartLayout = (chartDetails, chartData, yAxis, xAxis, xaxis_list, yaxis_list, chartIdentifier) => {
    const xaxis = {
        gridcolor: borderColor,
        color: textColor,
        autorange: true,
        rangeslider: {
            visible: false,
        },
        domain: [0.02, 0.98]
    };
    const yaxis = {
    };
    if(chartDetails.x_type !== null){
        xaxis.type = chartDetails.x_type;
    }
    if(xAxis > 1){
        xaxis.overlaying = "x"
    }
    _createOrAdaptChartedElements(chartDetails, yAxis, xAxis, chartIdentifier).forEach(element => {
        chartData.push(element);
    })
    const layout = {
        autosize: true,
        margin: {l: 50, r: 50, b: 30, t: 0, pad: 0},
        showlegend: true,
        legend: {x: 0.01, xanchor: 'left', y: 0.99, yanchor:"top"},
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        dragmode: "pan",
        font: {
            color: textColor
        },
        yaxis: {
            gridcolor: borderColor,
            color: textColor,
            fixedrange: false,
            anchor: "free",
            overlaying: "y",
            side: 'left',
            position: 0
        },
        yaxis2: {
            gridcolor: borderColor,
            color: textColor,
            fixedrange: false,
            anchor: "free",
            overlaying: "y",
            side: 'right',
            position: 1
        },
        yaxis3: {
            gridcolor: borderColor,
            color: textColor,
            fixedrange: false,
            anchor: "free",
            overlaying: "y",
            side: 'right',
            position: 0.985
        },
        yaxis4: {
            gridcolor: borderColor,
            color: textColor,
            fixedrange: false,
            anchor: "free",
            overlaying: "y",
            side: 'left',
            position: 0.015
        }
    };
    if(true){
        // unified tooltip
        layout.hovermode = "x unified";
        layout.hoverlabel = {
            bgcolor: "#131722",
            bordercolor: borderColor
        };
    } else {
        layout.hovermode = false;
    }

    const MAX_AXIS_INDEX = 4;
    yaxis_list.push(yaxis)
    yaxis_list.forEach(function (axis, i){
        if(i > 0 && i < MAX_AXIS_INDEX){
            layout[`yaxis${i + 1}`].type = axis.type;
        } else{
            layout["yaxis"].type = axis.type
        }
    });
    xaxis_list.push(xaxis)
    xaxis_list.forEach(function (axis, i){
        if(i > 0){
            layout[`xaxis${i + 1}`] = axis;
        }else{
            layout.xaxis = axis
        }
    });
    return layout
}

const createCharts = () => {
    FULL_DATA.forEach((maybeChart, index) => {
        if (maybeChart.type !== "chart") {
            return;
        }
        const chartData = [];
        const xaxis_list = [];
        const yaxis_list = [];
        let yAxis = 0;
        const chartDivID = `${maybeChart.name}-${index}`;
        const parentDiv = $(document.getElementById(maybeChart.name));
        parentDiv.append(`<div id="${chartDivID}" class="${maybeChart.name}"></div>`);
        let layout = undefined;
        maybeChart.data.elements.forEach((chartDetails) => {
            if (chartDetails.own_yaxis && yAxis < 4) {
                yAxis += 1;
            } else if (yAxis === 0) {
                yAxis = 1;
            }
            let xAxis = 1;
            if (chartDetails.own_xaxis) {
                xAxis += 1;
            }
            const chartIdentifier = "";
            layout = createChartLayout(chartDetails, chartData, yAxis, xAxis, xaxis_list, yaxis_list, chartIdentifier);
        })
        Plotly.newPlot(chartDivID, chartData, layout, getPlotlyConfig());
    })
}

const init = () => {
    createCharts();
}

init();
});
