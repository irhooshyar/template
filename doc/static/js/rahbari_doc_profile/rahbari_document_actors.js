let actors_rows = []
actor_init()

async function find_rahbari_document_actors(document_id) {

    const request_link = 'http://' + location.host + "/get_rahbari_document_actor/" + document_id + "/";
    let response = await fetch(request_link).then(response => response.json());

    get_document_profile_actors(response['result']);
}

function actor_init() {
    const menu_columns = {
        "all_repetition": 'تعداد احکام حاوی نام',
        "actor_name": 'نام کنشگر',
    }
    append_column(menu_columns, "ActorColumnSelect")
}

async function get_document_profile_actors(generated_locations) {
    actors_rows = actor_generateRows(generated_locations)

    // const paragraph_table_tab = document.getElementById("paragraph_person_info_tab")
    // if (paragraph_table_tab.classList.contains("active")) {
    //     document.getElementById("SearchResultLable").innerText = "تعداد کل نتایج: " + generated_persons.length + " فرد"
    // }
    // paragraph_table_tab.addEventListener("click", () => {
    //     document.getElementById("SearchResultLable").innerText = "تعداد کل نتایج: " + generated_persons.length + " فرد"
    // })

    startBlockUI('paragraph_info_pane');
    actor_table_show_result();
    stopBlockUI()

}

function actor_generateRows(actors) {
    const rows = []

    let counter = 1
    for (const actor of actors) {
        const modal_function = `show_detail_modal('${actor[0]}','احکام دارای کنشگر','attachment.content')`
        const detail = '<button type="button" class="btn modal_btn" data-bs-toggle="modal" onclick="' + modal_function + '" data-bs-target="#ChartModal_2">جزئیات</button>'


        const row = {}
        row['id'] = counter
        row['actor_name'] = actor[0]
        row['all_repetition'] = actor[1];
        row['detail'] = detail

        rows.push(row)
        counter++;
    }

    return rows
}

async function actor_tableExportExcel() {
    let csv = FooTable.get('#DocProfileActorsTable').toCSV();
    const btn_regex = new RegExp('<button.*</button>', 'g')
    csv = csv.replaceAll("#", "")
    csv = csv.replaceAll(btn_regex, "")
    const document_name = document.getElementById('document_select').title
    let save_file_name = "کنشگران {" + document_name + "}"

    let csvContent = "data:text/csv;charset=utf-8,%EF%BB%BF" + encodeURI(csv);
    const link = document.createElement("a");
    link.setAttribute("href", csvContent);
    link.setAttribute("download", save_file_name + ".csv");
    document.body.appendChild(link);
    link.click()
}

function actor_table_show_result() {
    let selected_columns = ["id", "detail"]
    selected_columns = find_selected_column(selected_columns, "ActorColumnSelect")

    const ActorTableColumns = [
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
            "name": "actor_name",
            "title": "کنشگر",
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
        for (let column of ActorTableColumns) {
            if (selected_columns.includes(column["name"])) {
                column["visible"] = true
            } else {
                column["visible"] = false
            }
        }
    }


    $('#DocProfileActorsTable').empty();
    $('#DocProfileActorsTable').footable({
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
            "placeholder": "نام کنشگر...."
        },
        "sorting": {
            "enabled": true
        },
        "empty": "در این سند هیچ کنشگری یافت نشد.",

        "columns": ActorTableColumns,
        "rows": actors_rows
    })
}

