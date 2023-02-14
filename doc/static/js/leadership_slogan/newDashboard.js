MAX_RESULT_WINDOW = 5000
SEARCH_RESULT_SIZE = 100


function startBlockUI() {
    $.blockUI({
        // BlockUI code for element blocking
        message: ("<div class='lds-ellipsis'><div></div><div></div><div></div><div></div></div><h6 style = 'font-family:vazir;'>...در حال دریافت اطلاعات<h6>"),
        css: {
            color: 'var(--menu_color)',
            border: 'none',
            borderRadius: '5px',
            borderColor: 'var(--menu_color)',
            paddingTop: '5px'
        }
    });
    startTime = new Date();
}

function stopBlockUI() {
    $.unblockUI();
    elapsed_time = endTimer();
    toast_message = '<span class="text-secondary"> ' + 'زمان سپری شده: ' + '</span>' + '<span class="bold" style="color:var(--menu_color)">' + elapsed_time + ' ثانیه' + '</span>'
}

async function new_prof_slogan_year_changed(year) {
    const request_link = 'http://' + location.host + "/slogan_get_chart/" + year + "/"

    let response = await fetch(request_link).then(response => response.json());

    console.log(response)
    const data = []
    let all_data = 0
    for (let buc of response['with_word_year_agg']['approval-year-content-agg']['buckets']) {
        all_data += buc['doc_count']
    }
    for (let item of Object.keys(response.keyword_repeat)) {
        data.push([item, response.keyword_repeat[item]])
    }
    guage_chart("word_count_container", {
        data: data,
        all_data: all_data,
        title: 'توزیع کلیدواژه ها در اسناد حاوی واژه',
        size: "full",
        onClick: (e, data, index) => {
            console.log(data)
            console.log(index)
        }
    })
    create_bars_chart_data(response['year_agg']['approval-year-agg']['buckets'],
        response['with_word_year_agg']['approval-year-content-agg']['buckets'])
}

function create_bars_chart_data(all_year, keyword_all_year) {
    all_year = all_year.sort((a, b) => a['key'] - b['key'])

    let data = {}
    data["اسناد بدون واژه"] = []
    data["اسناد حاوی حداقل واژه"] = []
    for (let year_bucket of all_year) {
        let is_have_keyword = false;
        for (let keyword_bucket of keyword_all_year) {
            if (year_bucket['key'] === keyword_bucket['key']) {
                data["اسناد بدون واژه"].push({
                    x: year_bucket["key"],
                    value: year_bucket["doc_count"] - keyword_bucket["doc_count"]
                })
                data["اسناد حاوی حداقل واژه"].push({x: year_bucket["key"], value: keyword_bucket["doc_count"]})
                is_have_keyword = true
                break
            }
        }
        if (!is_have_keyword) {
            data["اسناد بدون واژه"].push({
                x: year_bucket["key"],
                value: year_bucket["doc_count"]
            })
            data["اسناد حاوی حداقل واژه"].push({x: year_bucket["key"], value: 0})
        }
        // if (row.length === 2) row[2] = 0
    }

    console.log(data)

    const options = {
        data: data,
        xAxisTitle: 'سال',
        title: 'توزیع اسناد حاوی حداقل یک واژه به تفکیک سال',
        size: "full",
        yAxisTitle: "تعداد کل اسناد",
        onClick: (e, junk_data, data) => {
            const key = data[0] === "اسناد حاوی حداقل واژه" ? 1 : 0;
            const year = data[1]
            const slogan_year = document.getElementById("slogan").value;

            click_stack_based_column(key, slogan_year, year, data[0])
        }
    };


    newStackedColumnChart("doc_count_container", options)
}

function guage_chart(container_id, options) {
    const {chartContainerId, chartDownloadId} = newChartContainer(container_id, options);
    const palette = anychart.palettes.distinctColors();

    palette.items(['#488FB8', '#B8A948', '#8FB848', '#CDC37F', '#CD7F8A', '#B1CD7F', '#CD7FB1', '#7FB1CD', '#7F8ACD', '#CDC37F', '#B1CD7F']);

    let all_data = options.all_data
    let chart_data = options.data

    if (chart_data.length === 0) {
        document.getElementById(chartContainerId).innerText = "هیچ داده ای وجود ندارد"
        return;
    }

    let names = [];
    let data = [];
    for (let item of chart_data) {
        names.push(item[0])
        data.push(item[1])
    }
    for (let i = 0; i < names.length; i++) {
        data.push(all_data)
    }

    var dataSet = anychart.data.set(data);
    var makeBarWithBar = function (gauge, radius, i, width) {
        var stroke = null;
        gauge
            .label(i)
            .text(names[i] + ' ' + Math.ceil(((data[i] / all_data) * 100)) + '%') // color: #7c868e
            .textDirection("rtl")
            .fontFamily("vazir")
            .fontColor('#6C757D')

        gauge
            .label(i)
            .hAlign('center')
            .vAlign('middle')
            .anchor('right-center')
            .padding(0, 10)
            .height(width / 2 + '%')
            .offsetY(radius + '%')
            .offsetX(0)
            .fontFamily("vazir");

        gauge
            .bar(i)
            .dataIndex(i)
            .radius(radius)
            .width(width)
            .fill(palette.itemAt(i))
            .stroke(null)
            .zIndex(5);
        gauge
            .bar(i + 100)
            .dataIndex(i + (data.length / 2))
            .radius(radius)
            .width(width)
            .fill('#F5F4F4')
            .stroke(stroke)
            .zIndex(4);

        return gauge.bar(i);
    };


    anychart.onDocumentReady(function () {
        var gauge = anychart.gauges.circular();
        gauge.data(dataSet);
        gauge
            .fill('#fff')
            .stroke(null)
            .padding(0)
            .margin(100)
            .startAngle(0)
            .sweepAngle(270);

        let tooltip = gauge.tooltip();
        tooltip.fontFamily("vazir");
        tooltip.hAlign('center').format("تعداد: {%value}");

        var axis = gauge.axis().radius(100).width(1).fill(null);
        axis
            .scale()
            .minimum(0)
            .maximum(all_data)
            .ticks({interval: 1})
            .minorTicks({interval: 1});
        axis.labels().enabled(false);
        axis.ticks().enabled(false);
        axis.minorTicks().enabled(false);

        const itration = data.length / 2
        let radius = 100;
        let width = 75 / itration
        if (itration === 1) width = 55
        for (let i = 0; i < itration; i++) {
            makeBarWithBar(gauge, radius, i, width);
            radius = radius - (100 / itration)
        }
        gauge.margin(50);

        if (options.onClick) {
            gauge.listen("mouseOver", function () {
                document.body.style.cursor = "pointer";
            });
            gauge.listen("mouseOut", function () {
                document.body.style.cursor = "auto";
            });

            gauge.listen('Click', (e) => {
                const click_tag = e.domTarget.tag;
                let index = click_tag["index"]
                if (index >= options.data.length) {
                    index = index - options.data.length
                }
                options.onClick(e, options.data, index)
            })
        }

        // gauge
        //     .title()
        //     .text(
        //         options.title
        //     )
        //     .useHtml(true);
        // gauge
        //     .title()
        //     .enabled(true)
        //     .hAlign('center')
        //     .padding(0)
        //     .margin([0, 0, 20, 0]);

        gauge.container(chartContainerId);
        gauge.draw();
    });
}

async function click_stack_based_column(key, slogan_year, selected_year, chart_name) {
    startBlockUI("کلیک روی نمودار")
    const request_link = 'http://' + location.host + "/slogan_stackBased_get_information/" + key + "/" + slogan_year + "/" + selected_year + "/";

    document.getElementById("ChartModalBodyText_2").innerHTML = ""
    document.getElementById("ChartModalHeader_2").innerHTML = ""


    // set modal header
    modal_header = chart_name + " در سال " + selected_year
    document.getElementById("ChartModalHeader_2").innerHTML = modal_header
    // define request link without curr_page & search_result_size

    request_configs = {
        "link": request_link,
        "search_result_size": SEARCH_RESULT_SIZE,
        "max_result_window": MAX_RESULT_WINDOW,
        "data_type": "url_parameters",
        "form_data": null
    }

    export_link = 'http://' + location.host + "/slogan_stackBased_information_export/" + key + "/" + slogan_year + "/" + selected_year + "/";

    export_configs = {
        "link": export_link,
        "btn_id": "ExportExcel_2"
    }

    highlight_configs = {
        "parameters": null,
        "highlight_enabled": false,
        "custom_function": null
    }

    modal_configs = {
        "body_id": "ChartModalBodyText_2",
        "modal_load_more_btn_id": "LoadMoreDocuments_2",
        "result_size_container_id": "DocsCount_2",
        "result_size_message": "سند",
        "list_type": "ordered",
        "custom_body_function": null,
        "body_parameters": null,
        "link_page": "information",

    }

    segmentation_config = {
        "parameters": ["احساس بسیار منفی", "بدون ابراز احساسات", "احساس منفی", "احساس خنثی یا ترکیبی از مثبت و منفی", "احساس مثبت", "احساس بسیار مثبت"],
        "keyword": "sentiment",
        "enable": false,
        "aggregation_keyword": "rahbari-sentiment-agg"
    }


    column_interactivity_obj = new ColumnInteractivity("documents",
        request_configs, export_configs, modal_configs, highlight_configs, segmentation_config)

    result = await column_interactivity_obj.load_content();
    console.log(result)

    $('#ChartModalBtn_2').click()
    stopBlockUI('کلیک روی نمودار');

    $('#ExportExcel_2').on('click', async function () {
        await column_interactivity_obj.download_content();
    })
}