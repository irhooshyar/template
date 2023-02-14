let person_rows = []
init()

function init() {
    const menu_columns = {
        "all_repetition": 'تعداد احکام حاوی نام',
        "person_name": 'نام فرد',
    }
    append_column(menu_columns, "PersonColumnSelect")
}

async function get_document_profile_real_persons(generated_persons) {
    person_rows = generateRows(generated_persons)

    // const paragraph_table_tab = document.getElementById("paragraph_person_info_tab")
    // if (paragraph_table_tab.classList.contains("active")) {
    //     document.getElementById("SearchResultLable").innerText = "تعداد کل نتایج: " + generated_persons.length + " فرد"
    // }
    // paragraph_table_tab.addEventListener("click", () => {
    //     document.getElementById("SearchResultLable").innerText = "تعداد کل نتایج: " + generated_persons.length + " فرد"
    // })

    startBlockUI('paragraph_info_pane');
    table_show_result();
    stopBlockUI()

}

function generateRows(persons) {
    const rows = []

    let counter = 1
    for (const person of persons) {
        if(person['key'] === "بدون شخص حقیقی") continue
        const modal_function = `show_detail_modal('${person['key']}', 'احکام دارای شخص حقیقی')`
        const detail = '<button type="button" class="btn modal_btn" data-bs-toggle="modal" onclick="' + modal_function + '" data-bs-target="#ChartModal_2">جزئیات</button>'


        const row = {}
        row['id'] = counter
        row['person_name'] = person['key']
        row['all_repetition'] = person['doc_count'];
        row['detail'] = detail

        rows.push(row)
        counter++;
    }

    return rows
}

async function tableExportExcel() {
    let csv = FooTable.get('#DocProfilePersonsTable').toCSV();
    const btn_regex = new RegExp('<button.*</button>', 'g')
    csv = csv.replaceAll("#", "")
    csv = csv.replaceAll(btn_regex, "")
    const document_name = document.getElementById('document_select').title
    let save_file_name = "افراد حقیقی {" + document_name + "}"

    let csvContent = "data:text/csv;charset=utf-8,%EF%BB%BF" + encodeURI(csv);
    const link = document.createElement("a");
    link.setAttribute("href", csvContent);
    link.setAttribute("download", save_file_name + ".csv");
    document.body.appendChild(link);
    link.click()
}

function table_show_result() {


    let selected_columns = ["id", "detail"]
    selected_columns = find_selected_column(selected_columns, "PersonColumnSelect")

    const PersonTableColumns = [
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
            "name": "person_name",
            "title": "نام فرد",
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
        for (let column of PersonTableColumns) {
            if (selected_columns.includes(column["name"])) {
                column["visible"] = true
            } else {
                column["visible"] = false
            }
        }
    }


    $('#DocProfilePersonsTable').empty();
    $('#DocProfilePersonsTable').footable({
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
            "placeholder": "نام فرد...."
        },
        "sorting": {
            "enabled": true
        },
        "empty": "فردی یافت نشد.",

        "columns": PersonTableColumns,
        "rows": person_rows
    })
}