let location_rows = []
location_init()

function location_init() {
    const menu_columns = {
        "all_repetition": 'تعداد احکام حاوی نام',
        "person_name": 'موقعیت مکانی',
    }
    append_column(menu_columns, "LocationColumnSelect")
}

async function get_document_profile_locations(generated_locations) {
    location_rows = location_generateRows(generated_locations)

    // const paragraph_table_tab = document.getElementById("paragraph_person_info_tab")
    // if (paragraph_table_tab.classList.contains("active")) {
    //     document.getElementById("SearchResultLable").innerText = "تعداد کل نتایج: " + generated_persons.length + " فرد"
    // }
    // paragraph_table_tab.addEventListener("click", () => {
    //     document.getElementById("SearchResultLable").innerText = "تعداد کل نتایج: " + generated_persons.length + " فرد"
    // })

    startBlockUI('paragraph_info_pane');
    location_table_show_result();
    stopBlockUI()

}

function location_generateRows(locations) {
    const rows = []

    let counter = 1
    for (const location of locations) {
        if(location['key'] === "بدون موقعیت مکانی") continue
        const modal_function = `show_detail_modal('${location['key']}', 'احکام دارای موقعیت مکانی')`
        const detail = '<button type="button" class="btn modal_btn" data-bs-toggle="modal" onclick="' + modal_function + '" data-bs-target="#ChartModal_2">جزئیات</button>'


        const row = {}
        row['id'] = counter
        row['location_name'] = location['key']
        row['all_repetition'] = location['doc_count'];
        row['detail'] = detail

        rows.push(row)
        counter++;
    }

    return rows
}

// async function show_person_modal(personKey) {
//     const field_name = CHART_FIELD_DICT['person_container'] + '.keyword'
//     const chart_name = CHART_NAME_DICT['person_container']
//
//     GetClickedColumnParagraphs(chart_name, field_name, personKey.replaceAll("#", "*"), false, true)
// }


async function location_tableExportExcel() {
    let csv = FooTable.get('#DocProfileLocationTable').toCSV();
    const btn_regex = new RegExp('<button.*</button>', 'g')
    csv = csv.replaceAll("#", "")
    csv = csv.replaceAll(btn_regex, "")
    const document_name = document.getElementById('document_select').title
    let save_file_name = "موقعیت های مکانی {" + document_name + "}"

    let csvContent = "data:text/csv;charset=utf-8,%EF%BB%BF" + encodeURI(csv);
    const link = document.createElement("a");
    link.setAttribute("href", csvContent);
    link.setAttribute("download", save_file_name + ".csv");
    document.body.appendChild(link);
    link.click()
}

function location_table_show_result() {


    let selected_columns = ["id", "detail"]
    selected_columns = find_selected_column(selected_columns, "LocationColumnSelect")

    const LocationTableColumns = [
        {
            "name": "id",
            "title": "ردیف",
            "breakpoints": "xs sm",
            "type": "number",
            "style": {
                "width": "5%"
            }
        },
        {
            "name": "location_name",
            "title": "موقعیت مکانی",
        },
        {
            "name": "all_repetition",
            "title": "تعداد احکام حاوی نام",
            "type": "number",
            "style": {
                "width": "30%"
            }
        },
        // {
        //     "name": "v_positive_sentiment",
        //     "title": "تعداد احساس بسیار مثبت",
        //     "type": "number",
        //     "style": {
        //         "width": "8%"
        //     }
        // },
        // {
        //     "name": "positive_sentiment",
        //     "title": "تعداد احساس مثبت",
        //     "type": "number",
        //     "style": {
        //         "width": "8%"
        //     }
        // },
        // {
        //     "name": "mixed_sentiment",
        //     "title": "تعداد احساس خنثی",
        //     "type": "number",
        //     "style": {
        //         "width": "8%"
        //     }
        // },
        // {
        //     "name": "v_negative_sentiment",
        //     "title": "تعداد احساس بسیار منفی",
        //     "type": "number",
        //     "style": {
        //         "width": "8%"
        //     }
        // },
        // {
        //     "name": "negative_sentiment",
        //     "title": "تعداد احساس منفی",
        //     "type": "number",
        //     "style": {
        //         "width": "8%"
        //     }
        // },
        // {
        //     "name": "no_sentiment",
        //     "title": "تعداد بدون ابراز احساسات",
        //     "type": "number",
        //     "style": {
        //         "width": "8%"
        //     }
        // },
        {
            "name": "detail",
            "title": "جزئیات",
            "style": {
                "width": "10%"
            }
        },
    ]

    if (!selected_columns.includes("all")) {
        for (let column of LocationTableColumns) {
            if (selected_columns.includes(column["name"])) {
                column["visible"] = true
            } else {
                column["visible"] = false
            }
        }
    }


    $('#DocProfileLocationTable').empty();
    $('#DocProfileLocationTable').footable({
        "paging": {
            "enabled": true,
            strings: {
                first: '«',
                prev: '‹',
                next: '›',
                last: '»'
            }
        },
        "filtering": {
            "enabled": true,
            "placeholder": "موقعیت مکانی...."
        },
        "sorting": {
            "enabled": true
        },
        "empty": "در این خبر هیچ موقعیت مکانی یافت نشد.",

        "columns": LocationTableColumns,
        "rows": location_rows
    })
}