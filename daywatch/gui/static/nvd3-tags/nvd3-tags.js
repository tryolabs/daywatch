/* Constants */

const NVD3_ID_ATTR_NAME = 'nvd3_id';

/** Map of option names to their attribute names.
 */
const option_attributes = {
    type: 'type',
    width: 'width',
    height: 'height',

    x_start: 'x-start',
    x_end: 'x-end',
    x_format: 'x-format',
    x_date_format: 'x-date-format',

    y_start: 'y-start',
    y_end: 'y-end',
    y_format: 'y-format',
    y_date_format: 'y-date-format',

    tooltips: 'tooltips',
    legend: 'legend',
    clip: 'clip'
};

/* Utilities */

/** Test whether an object is not undefined.
 */
function isDefined(obj) {
    return obj != undefined;
}

/** Convert 'true' to true and everything else to false.
 */
function strToBool(str) {
    return str === 'true' ? true : false
}

/* Data processing */

/** Extract data from CSV.
 */
function extractData(nodes) {
    const separated = nodes.text().split('\n');
    const cleaned = $.map(
        $.grep(separated, function(str) {
            return str.trim() != "";
        }),
        function(str) {
            return str.trim();
        }
    );
    const pairs = $.map(cleaned, function(str) {
        return [str.split(',')];
    });
    return $.grep(pairs, function(pair) {
        return isDefined(pair);
    });
}

/** Process CSV data.
 */
function processData(data) {
    return $.map(data, function(row) {
        return [$.map(row, function(item) {
            return !isNaN(item) ? parseFloat(item) : item;
        })];
    });
}

/** Process multi-series data into something NVD3 likes.
 */
function multiSeriesData(data) {
    const labels = data[0].slice(1);
    const values = data.slice(1);
    const output = $.map(labels, function(label,index) {
        return {
            'key': label,
            'values': $.map(values, function(row, pos) {
                return [[row[0],row[index+1]]];
            })
        };
    });
    return output;
}

/* Chart rendering */

/** Apply options to a chart.
 */
function customizeChart(chart, options) {
    /* Set the dimensions of the chart */
    if(isDefined(options.width)) {
        chart = chart.width(parseInt(options.width));
    }
    if(isDefined(options.height)) {
        chart = chart.height(parseInt(options.height));
    }

    /* Apply other general chart options */
    chart = chart.tooltips(strToBool(options.tooltips));
    if(isDefined(options.legend) & options.type != 'bar') {
        chart = chart.showLegend(strToBool(options.legend));
    }
    if(isDefined(options.clip)) {
        chart = chart.clipEdge(strToBool(options.clip));
    }

    /* Customize the axes */
    if(options.x_format) {
        chart.xAxis.tickFormat(d3.format(options.x_format));
    } else if(options.x_date_format) {
        chart.xAxis.tickFormat(function(x) {
            return d3.time.format(options.x_date_format)(new Date(x));
        });
    }

    if(options.y_format) {
        chart.yAxis.tickFormat(d3.format(options.y_format));
    } else if(options.y_date_format) {
        chart.yAxis.tickFormat(function(y) {
            return d3.time.format(options.y_date_format)(new Date(y));
        });
    }

    /* Customize axis ranges */
    const x_start = options.x_start;
    const x_end = options.x_end;
    if(isDefined(x_start) & isDefined(x_end)) {
        chart = chart.forceX([parseFloat(x_start), parseFloat(x_end)]);
    }

    const y_start = options.y_start;
    const y_end = options.y_end;
    if(isDefined(y_start) & isDefined(y_end)) {
        chart = chart.forceY([parseFloat(y_start), parseFloat(y_end)]);
    }

    /* Add the functions that extract data into the axes */
    return chart
        .x(function(item) {
            if(options.x_date_format) {
                // If the values of the x axis are Unix timestamps, we have to
                // modify them slightly for them to work
                return parseInt(item[0].toString() + '000');
            } else {
                return item[0];
            }
        })
        .y(function(item) {
            return item[1];
        });
}

/** Render a chart.
 */
function renderChart(chart_node, id) {
    chart_node.attr(NVD3_ID_ATTR_NAME, id.toString());
    chart_node.append('<svg></svg>');

    /* Hide the data */
    $(chart_node).find('data').hide();

    /* Extract the data and the options */

    var data = processData(extractData(chart_node.children('data')));

    const options = {
        type: chart_node.attr(option_attributes['type']),
        width: chart_node.attr(option_attributes['width']),
        height: chart_node.attr(option_attributes['height']),
        x_start: chart_node.attr(option_attributes['x_start']),
        x_end: chart_node.attr(option_attributes['x_end']),
        x_format: chart_node.attr(option_attributes['x_format']),
        x_date_format: chart_node.attr(option_attributes['x_date_format']),
        y_start: chart_node.attr(option_attributes['y_start']),
        y_end: chart_node.attr(option_attributes['y_end']),
        y_format: chart_node.attr(option_attributes['y_format']),
        y_date_format: chart_node.attr(option_attributes['y_date_format']),
        tooltips: chart_node.attr(option_attributes['tooltips']) || "false",
        legend: chart_node.attr(option_attributes['legend']) || "false",
        clip: chart_node.attr(option_attributes['clip']),
    };

    /* Decide what kind of chart we want to render, and in some cases manipulate
     * data to fit better */

    var chart_model;

    const type = options.type;
    if(type == 'line') {
        chart_model = nv.models.lineChart();
        data = multiSeriesData(data);
    } else if(type == 'pie') {
        chart_model = nv.models.pieChart();
    } else if(type == 'stacked') {
        chart_model = nv.models.stackedAreaChart();
        data = multiSeriesData(data);
    } else if(type == 'bar') {
        chart_model = nv.models.discreteBarChart();
        data = [["Values", 0]].concat(data);
        data = multiSeriesData(data);
    } else {
        console.log("Unknown chart type.");
    }

    /* Render the chart */

    if(chart_model) {
        nv.addGraph(function() {
            var plot = customizeChart(chart_model, options);

            selector = d3.select('chart[' + NVD3_ID_ATTR_NAME + '="'+id+'"] svg')
                .datum(data).transition().duration(500);

            if(isDefined(options.width)) {
                selector = selector.attr('width', options.width);
            }
            if(isDefined(options.height)) {
                selector = selector.attr('height', options.height);
            }
            selector = selector.call(plot);

            nv.utils.windowResize(plot.update);

            return plot;
        });
    }
}

/** Render all charts on a page.
 */
function renderAll() {
    $("chart").each(function(index) {
        renderChart($(this), index);
    });
}
