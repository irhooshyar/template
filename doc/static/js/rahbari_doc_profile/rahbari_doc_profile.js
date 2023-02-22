let startTime, endTime;

let first_loading = true;
let loaded_doc = 0
let counter = 0
const load_size = 200;
const notyf = new Notyf({position: {x: 'left', y: 'bottom'}});
const ft = FooTable.init('#PopUpTable', {
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
        "enabled": false
    },
    "sorting": {
        "enabled": true
    },
    "empty": "در حال بازیابی اسناد (لطفا صبر نمایید)",
    "columns": [{
        "name": "id",
        "title": "ردیف",
        "breakpoints": "xs sm",
        "type": "number",
        "style": {
            "width": 80,
            "maxWidth": 80
        }
    }, {
        "name": "document_name",
        "title": "نام سند"
    }, {
        "name": "subject",
        "title": "موضوع سند"
    }, {
        "name": "category",
        "title": "دسته سند"
    }, {
        "name": "date",
        "title": "تاریخ"
    }, {
        "name": "tag",
        "title": "انتخاب"
    }],
});

// const notyf = new Notyf({
//     duration: 5000,
//     position: {
//         x: "left",
//         y: "bottom",
//     },
//     dismissible: true,
// });

/* Search after press Enter */
$("#SearchBox").keyup(function (event) {
    if (event.keyCode === 13) {
        Search_Document_ByName();
    }
});

$(document).ready(function () {
    // $('#ApprovalsDropdown').addClass('active');
    $('#Rahbari_profile_link').addClass('active');
    $('select#language').on('change', function (e) {
            let selected_language = this.value;
            let current_url = window.location.href;
            if (selected_language === 'England') {
                if (selected_language === 'England') {
                    let page_name = current_url.split('/')[3]
                    let requested_url = current_url.replace(page_name, 'en')
                    window.location = requested_url;
                } else if (selected_language === 'Russia') {
                    let page_name = current_url.split('/')[3]
                    let requested_url = current_url.replace(page_name, 'ru')
                    window.location = requested_url;
                }
            }
        }
    )
    ;
});

init();

async function init() {
    await initSearchableSelects();

    document.getElementById("comment_form").addEventListener('submit', SubmitDocumentComment)
    document.getElementById("note_form").addEventListener('submit', SubmitDocumentNote)

    const url = new URL(window.location.href);
    var document_id = url.searchParams.get("id");

    if (document_id) {
        await SelectDocumentFunction(document_id)

    } else {
        const text = "انتخاب نمایید"
        document.getElementById("document").innerHTML = "<option value=" + 0 + " disabled>" + text + "</option>";
        document.getElementById("document_download").disabled = true;
        document.getElementById("pdf_download").disabled = true;
        document.getElementById("document_search").disabled = true;

        document.getElementById("document_select").disabled = true;
        const country_name = $("#country option:selected").text();
        document.getElementById('ModalHeader').innerText = 'مجموعه سند: ' + country_name;
        document.getElementById("document_select").disabled = false;

        if ($('.add-row-1').length === 0) {
            window.setTimeout(function () {
                $(".pagination").append("<li class='footable-page visible'><a class='add-row-1' href='#' onclick='loadMoreDoc()'>+</a></li>");
            }, 1000);
        }
    }
    loadMoreDoc()

    // user log
    let form_data = new FormData()
    let detail_type = "نمایش پنل"
    form_data.append('detail_type', detail_type);
    UserLog(form_data)
}


async function CountryChanged() {

    startBlockUI();
    document.getElementById("document_select").disabled = true;

    const country_name = $("#country option:selected").text();

    document.getElementById('ModalHeader').innerText = 'مجموعه سند: ' + country_name;

    document.getElementById("document_select").disabled = false;

    counter = 0;
    loaded_doc = 0
    first_loading = true

    $(".add-row-1").css('visibility', 'visible');

    document.getElementById("document_select").disabled = true;
    await setTimeout(loadMoreDoc(), 1000)
    document.getElementById("document_select").disabled = false;

    stopBlockUI()
}

async function ShowResult() {
    await DownloadLinkSet();
    await ShowDocumentComment()
    await ShowDocumentNote()

    const document_id = document.getElementById("document").value
    const country_id = document.getElementById('country').value

    document.getElementById("document_download").disabled = false;
    document.getElementById("pdf_download").disabled = false;
    document.getElementById("document_search").disabled = false;

    getDocumentFullProfileInfo(country_id, document_id)

    let form_data = new FormData()
    let detail_type = "نتایج جست و جو"
    let country_name = $("#country option:selected").text();
    let document_select_name = document.getElementById("document_select").title
    form_data.append('detail_type', detail_type);
    form_data.append('country_name', country_name);
    form_data.append('document_select_name', document_select_name);
    UserLog(form_data)
}

function copyDocumentName() {
    const copyText = document.getElementById("document_select");
    navigator.clipboard.writeText(copyText.innerText);
    $('.tooltip-inner').html('کپی شد!');
}

async function ShowDocumentContent() {
    document.getElementById('DocumentContentBody').innerHTML = ""
    const document_id = document.getElementById("document").value
    // disable show button before choosing a document
    if (!document_id || document_id == '0') {
        alert('لطفا یک سند را انتخاب نمایید.')
        return
    }
    $('#documentContent').modal('show');

    const request_link = 'http://' + location.host + "/GetDocumentContent/" + document_id + "/";
    let response = await fetch(request_link).then(response => response.json());
    response = response["document_paragraphs"]

    for (var i = 0; i < response.length; i++) {
        const document_name = response[i]["document_name"]
        const paragraph_text = response[i]["paragraph_text"]
        const paragraph_id = response[i]["paragraph_id"]


        paragraph_link = 'http://' + location.host + "/sentiment_analysis/?id=" + paragraph_id;

        const paragraph_tag = '<p>' + paragraph_text + '</p>'

        document.getElementById('documentContentHeader').innerText = document_name
        document.getElementById('DocumentContentBody').innerHTML += paragraph_tag

    }

    //user log
    let form_data = new FormData()
    let detail_type = "نمایش سند"
    let country_name = $("#country option:selected").text();
    let document_select_name = document.getElementById("document_select").title
    form_data.append('detail_type', detail_type);
    form_data.append('country_name', country_name);
    form_data.append('document_select_name', document_select_name);
    UserLog(form_data)
}

async function ShowDocumentSubject() {

    document.getElementById('subjectContentBody').innerHTML = ""
    const document_id = document.getElementById("document").value
    // disable show button before choosing a document
    if (!document_id || document_id == '0') {
        alert('لطفا یک سند را انتخاب نمایید.')
        return
    }
    $('#subjectContent').modal('show');

    const request_link = 'http://' + location.host + "/GetDocumentSubjectContent/" + document_id + "/" + 12 + "/";
    let response = await fetch(request_link).then(response => response.json());
    response = response["document_paragraphs"]

    for (var i = 0; i < response.length; i++) {
        const document_name = response[i]["document_name"]
        const paragraph_text = response[i]["paragraph_text"]
        let subject_tag = ""
        if (response[i]["subject_name"] !== "")
            subject_tag = response[i]["subject_name"]

        const paragraph_tag = '<div class="subject-content-container"><p>' + paragraph_text + '</p>' + subject_tag + "</div>"
        document.getElementById('subjectContentHeader').innerText = document_name
        document.getElementById('subjectContentBody').innerHTML += paragraph_tag
    }

    //user log
    let form_data = new FormData()
    let detail_type = "نمایش موضوع"
    let country_name = $("#country option:selected").text();
    let document_select_name = document.getElementById("document_select").title
    form_data.append('detail_type', detail_type);
    form_data.append('country_name', country_name);
    form_data.append('document_select_name', document_select_name);
    UserLog(form_data)
}

async function generatePDF() {
    startBlockUI();

    const approval_reference = "مقام معظم رهبری"
    const approval_date = document.getElementById("document_date").innerText

    const document_id = document.getElementById("document").value
    // disable show button before choosing a document
    if (!document_id || document_id == '0') {
        alert('لطفا یک سند را انتخاب نمایید.');
        return;
    }
    const request_link = 'http://' + location.host + "/GetDocumentContent/" + document_id + "/";
    let response = await fetch(request_link).then(response => response.json());
    response = response["document_paragraphs"];
    const document_name = response[0]["document_name"];
    let element = "<div8 class='d-flex'> <span>&nbsp;</span>  </div8>" +
        "<div1 class='container-fluid' style='direction: rtl'> " +
        "<div2 class='row p-4 mx-auto' style='border: 4px solid #ccc; border-radius: 20px;'> " +
        "<div6 style='margin: auto;text-align: center'> " +
        "<h5 style='padding-bottom: 10px'>" + document_name + "</h5> </div6> " +
        "<div7 class='d-flex' style='justify-content: space-between;width: 100%'> " +
        "<div8 class='d-flex'> <span> تاریخ تصویب  </span> <span>&nbsp;</span> <span> : </span> <span> " + approval_date + " </span> </div8> " +
        "<div9 class='d-flex'> <span> مرجع تصویب </span> <span>&nbsp;</span> <span> : </span> <span> " + approval_reference + " </span> </div9> </div7>" +

        "<div7 class='d-flex' style='justify-content: space-between;width: 100%'> " +
        "<div8 class='d-flex'> <span>&nbsp;</span>  </div8> " +
        "<div9 class='d-flex'>  <span>&nbsp;</span>  </div9> </div7> " +

        "<div3 class='d-flex' style='justify-content: space-between;width: 100%'>" + "<div4 > <p>سامانه ستار</p> </div4> " +
        "<div5> <span>rahnamud.ir:7074</span> </div5> </div3> </div2> </div1>"

    for (let i = 0; i < response.length; i++) {
        const paragraph_text = response[i]["paragraph_text"]
        const paragraph_tag = '<p dir="rtl">' + paragraph_text + '</p>';
        element += paragraph_tag;
    }
    //element += '</div>';
    console.log(element);

    let opt = {
        margin: 1,
        filename: document_name + '.pdf',
        image: {type: 'jpeg', quality: 0.98},
        html2canvas: {scale: 2},
        jsPDF: {unit: 'in', format: 'letter', orientation: 'portrait'},
        pagebreak: {mode: ['avoid-all', 'css', 'legacy'], after: 'firstPage'}
    };
    html2pdf().set(opt).from(element).save();

    stopBlockUI();

    //user log
    let form_data = new FormData()
    let detail_type = "دانلود سند"
    let country_name = $("#country option:selected").text();
    let document_select_name = document.getElementById("document_select").title
    form_data.append('detail_type', detail_type);
    form_data.append('country_name', country_name);
    form_data.append('document_select_name', document_select_name);
    UserLog(form_data)
}

// async function DownloadLinkSet() {
//     const country_id = document.getElementById("country").value;
//     let request_link = 'http://' + location.host + "/GetCountryById/" + country_id + "/";
//     let response = await fetch(request_link).then(response => response.json());
//     response = response["country_information"][0]
//
//     const country_folder = response["folder"];
//     const country_name = response["name"];
//     const document_id = document.getElementById("document").value;
//
//     request_link = 'http://' + location.host + "/GetDocumentById/" + document_id + "/";
//     response = await fetch(request_link).then(response => response.json());
//     const document_file_name = response["document_information"][0]["file_name"]
//
//     if (document_file_name !== "انتخاب نمایید ...") {
//         let file_path = "";
//
//         if (country_name.includes("فاوا")) {
//             file_path = 'http://' + location.host + '/media/data/' + country_folder + '\\' + document_file_name + '.docx';
//         } else {
//             file_path = 'http://' + location.host + '/media/data/' + country_folder + '\\' + document_file_name + '.txt';
//         }
//         document.getElementById("txt_download").href = file_path;
//
//         const document_id = document.getElementById("document").value;
//
//     } else {
//         document.getElementById("txt_download").href = "#";
//         return false;
//     }
// }

async function DownloadLinkSet() {
    var country_id = document.getElementById("country").value;
    var request_link = 'http://' + location.host + "/GetCountryById/" + country_id + "/";
    let response = await fetch(request_link).then(response => response.json());
    response = response["country_information"][0]

    const country_folder = response["folder"];
    const country_name = response["name"];
    const document_id = document.getElementById("document").value;

    request_link = 'http://' + location.host + "/GetDocumentById/" + document_id + "/";
    response = await fetch(request_link).then(response => response.json());
    var document_file_name = response["document_information"][0]["file_name"]

    if (document_file_name !== "انتخاب نمایید ...") {
        var file_path = "";

        if (country_name.includes("فاوا")) {
            file_path = 'http://' + location.host + '/media/data/' + country_folder + '\\' + document_file_name + '.docx';
        } else {
            file_path = 'http://' + location.host + '/media/data/' + country_folder + '\\' + document_file_name + '.txt';
        }
        document.getElementById("txt_download").href = file_path;

        const document_id = document.getElementById("document").value;

    } else {
        document.getElementById("txt_download").href = "#";
        return false;
    }
}

async function Reload() {
    startBlockUI();
    counter = 0;
    loaded_doc = 0
    first_loading = true

    $(".add-row-1").css('visibility', 'visible');

    document.getElementById("SearchBox").value = ""

    document.getElementById("document_select").disabled = true;
    setTimeout(loadMoreDoc, 1000)
    document.getElementById("document_select").disabled = false;
    // new
    if ($('.add-row-1').length === 0) {
        window.setTimeout(function () {
            $(".pagination").append("<li class='footable-page visible'><a class='add-row-1' href='#' onclick='loadMoreDoc()'>+</a></li>");
        }, 1000);
    }
    stopBlockUI()
}

function endTimer() {
    endTime = new Date();
    var timeDiff = endTime - startTime; //in ms
    // strip the ms
    timeDiff /= 1000;

    // get seconds
    var seconds = Math.round(timeDiff);
    console.log(seconds + " seconds");
    return seconds;
}

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

async function UserLog(form_data) {
    if (getCookie("username") !== "") {
        const user_name = getCookie("username")
        let page_url = window.location.pathname
        const user_ip = "127.0.0.0"

        page_url = page_url.slice(0, -1);
        if (page_url === "") {
            page_url = "/0";
        }
        let link_request = 'http://' + location.host + "/UserLogSaved/" + user_name + page_url + "/" + user_ip + "/";

        $.ajax({
            url: link_request,
            data: form_data,
            type: 'POST',
            contentType: false,
            processData: false,
            async: true,


        }).done(function (res) {
            console.log("done")

        }).fail(function (res) {
            console.log("fail")
        });

    }
}

async function loadMoreDoc() {
    let start_index = load_size * counter
    let end_index = load_size * (counter + 1)

    const country_id = document.getElementById("country").value

    const request_link = 'http://' + location.host + "/GetDocumentsByCountryId_Modal/" + country_id + "/" + start_index + "/" + end_index + "/"
    let response = await fetch(request_link).then(response => response.json());
    let documentsList = response["documentsList"]
    let all_count = response["document_count"]

    if (first_loading === false)
        ft.rows.load(documentsList, true);
    else {
        ft.rows.load(documentsList);
        document.getElementById("all_doc_count").innerText = all_count.toString()
    }

    loaded_doc += documentsList.length;

    document.getElementById("load_doc_count").innerText = loaded_doc.toString()
    counter += 1
    first_loading = false

    if (loaded_doc === all_count) {
        $(".add-row-1").css('visibility', 'hidden');
    } else {
        window.setTimeout(function () {
            $(".pagination").append("<li class='footable-page visible'><a class='add-row-1' href='#' onclick='loadMoreDoc()'>+</a></li>");
        }, 1000);
    }

}

async function pagingchange() {
    paging_size = $('#LoadCount option:selected').val()
    FooTable.get('#PopUpTable').pageSize(paging_size);
    window.setTimeout(function () {
        $(".pagination").append("<li class='footable-page visible'><a href='#' class='add-row-1' onclick='loadMoreDoc()'>+</a></li>");
    }, 1000);
}

async function SelectDocumentFunction(document_id) {
    const country_id = document.getElementById('country').value
    const request_link = 'http://' + location.host + "/GetDetailDocumentById/" + country_id + "/" + document_id + "/";
    let response = await fetch(request_link).then(response => response.json());
    const result = response["result"][0]['_source']
    document.getElementById("document").innerHTML = "<option value=" + result["document_id"] + " >" + result["document_name"] + "</option>";

    document_select_tag = '<i class="dropdown_icon bi bi-chevron-down ml-2 bold text-black"></i>' + result['document_name']
    document.getElementById('document_select').innerHTML = document_select_tag;
    document.getElementById('document_select').title = result['document_name'];

    document.getElementById('document_date').innerHTML = response['date']
    document.getElementById('document_subject').innerHTML = response['subject']
    document.getElementById('document_category').innerHTML = response['category']
    // GetTextSummary()
    ShowResult();
    find_rahbari_document_actors(document_id)
}

function debounce(func, timeout = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => {
            func.apply(this, args);
        }, timeout);
    };
}

const processSearch = debounce(() => Search_Document_ByName(), 500);

async function Search_Document_ByName() {
    const country_id = document.getElementById("country").value
    let text = document.getElementById("SearchBox").value
    let level_id = 0
    let subject_id = 0
    let type_id = 0
    let approval_reference_id = 0
    let from_year = 0
    let to_year = 0
    let place = 'عنوان'
    let search_type = 'exact'

    if (!text) {
        Reload();
        return;
    }


    const from_advisory_opinion_count = 0
    const from_interpretation_rules_count = 0
    const curr_page = 1

    const request_link = 'http://' + location.host + "/SearchDocument_ES/" + country_id + "/" + level_id + "/" + subject_id + "/" + type_id + "/" +
        approval_reference_id + "/" + from_year + "/" + to_year + "/" + from_advisory_opinion_count + "/" + from_interpretation_rules_count + "/" + "0" + "/" + place + "/" + text + "/" + search_type + "/" + curr_page + "/"


    let response = await fetch(request_link).then(response => response.json());
    let documentsList = response["result"]
    let document_count = response["total_hits"]

    document.getElementById("all_doc_count").innerText = document_count.toString()

    const result_documentsList = []
    for (const doc of documentsList) {
        let id = doc['_id']
        let approval_reference = doc['_source']['approval_reference_name']
        let approval_date = doc['_source']['approval_date']
        let subject = doc['_source']['subject_name']
        let document_name = doc['_source']['name']
        let tag = '<button type="button" class="btn modal_btn" data-bs-toggle="modal" onclick="SelectDocumentFunction(' + id + ')">انتخاب</button>'
        const row = {
            "id": id,
            "document_name": document_name,
            "subject": subject,
            "approval_reference": approval_reference,
            "approval_date": approval_date,
            "tag": tag
        }
        result_documentsList.push(row)
    }


    ft.rows.load(result_documentsList);

    loaded_doc = document_count;

    document.getElementById("load_doc_count").innerText = loaded_doc.toString()

    if (loaded_doc === document_count)
        $(".add-row-1").css('visibility', 'hidden');
    else {
        window.setTimeout(function () {
            $(".pagination").append("<li class='footable-page visible'><a href='#' class='add-row-1' onclick='loadMoreDoc()'>+</a></li>");
        }, 1000);
    }

}

async function show_detail_modal(Key, chart_name, field_value) {
    const document_id = document.getElementById("document").value
    const text = " " + Key + " "
    click_name_chart(document_id, text, chart_name, field_value)
}

function custom_highlight_function(paragraph, highlight_parameters, items) {
    let selected_word = highlight_parameters["selected_word"]
    selected_word = selected_word.trim()
    if (!items) {
        let selected_word_tag = '<span class="text-primary fw-bold">' + selected_word + '</span>'
        paragraph = paragraph.replaceAll(selected_word, selected_word_tag)
    } else {
        let resultText = paragraph
        let difference = 0;

        for (let i = 0; i < items.length; i++) {
            const object = items[i];
            if (object['word'] !== selected_word) continue

            const searchText = resultText.substring(object["start"] + difference, object["end"] + difference);
            const replaceHtml = '<span class="text-primary fw-bold">' + searchText + '</span>';

            resultText =
                resultText.substring(0, object["start"] + difference) +
                replaceHtml +
                resultText.substring(object["end"] + difference, resultText.length);

            difference = resultText.length - paragraph.length;
        }

        paragraph = resultText
    }
    return paragraph;
}

async function click_name_chart(document_id, text, chart_name, field_value) {
    startBlockUI("کلیک روی نمودار")
    let request_link = 'http://' + location.host + "/rahbari_document_name_chart_column/" + document_id + "/" + text + "/" + field_value + "/";

    document.getElementById("ChartModalBodyText_2").innerHTML = ""
    document.getElementById("ChartModalHeader_2").innerHTML = ""

    // set modal header
    modal_header = chart_name + ": " + text
    document.getElementById("ChartModalHeader_2").innerHTML = modal_header
    // define request link without curr_page & search_result_size

    export_link = 'http://' + location.host + "/export_rahbari_document_chart_column/"
        + document_id + "/"
        + text + "/"
        + field_value + "/"

    export_configs = {
        "link": export_link,
        "btn_id": "ExportExcel_2"
    }

    let load_object = field_value.split(".")[0]
    load_object = load_object + "_object"

    if (field_value === "attachment.content") {
        load_object = null
        request_link = 'http://' + location.host + "/rahbari_document_actor_chart_column/" + document_id + "/" + text + "/";
    }


    highlight_parameters = {"selected_word": text, "selected_object": load_object}

    highlight_configs = {
        "parameters": highlight_parameters,
        "highlight_enabled": true,
        "custom_function": custom_highlight_function
    }

    request_configs = {
        "link": request_link,
        "search_result_size": SEARCH_RESULT_SIZE,
        "max_result_window": MAX_RESULT_WINDOW,
        "data_type": "url_parameters",
        "form_data": null
    }

    modal_configs = {
        "body_id": "ChartModalBodyText_2",
        "modal_load_more_btn_id": "LoadMoreDocuments_2",
        "result_size_container_id": "DocsCount_2",
        "result_size_message": "حکم",
        "list_type": "ordered",
        "custom_body_function": null,
        "body_parameters": null

    }

    segmentation_config = {
        "parameters": ["احساس بسیار منفی", "بدون ابراز احساسات", "احساس منفی", "احساس خنثی یا ترکیبی از مثبت و منفی", "احساس مثبت", "احساس بسیار مثبت"],
        "keyword": "sentiment",
        "enable": false,
        "aggregation_keyword": "rahbari-sentiment-agg"
    }


    column_interactivity_obj = new ColumnInteractivity("paragraphs",
        request_configs, export_configs, modal_configs, highlight_configs, segmentation_config)

    result = await column_interactivity_obj.load_content();
    console.log(result)

    $('#ChartModalBtn_2').click()
    stopBlockUI('کلیک روی نمودار');

    $('#ExportExcel_2').on('click', async function () {
        await column_interactivity_obj.download_content();
    })
}

async function SubmitDocumentComment(e) {
    let date = {year: 'numeric', month: '2-digit', day: '2-digit'};
    let comment_time = new Date().toLocaleDateString('fa-IR-u-nu-latn', date);
    comment_time = comment_time.replace("/", "-")
    comment_time = comment_time.replace("/", "-")
    console.log(comment_time);

    e.preventDefault()
    try {
        const document_id = document.getElementById("document").value
        const comment_text = document.getElementById("form_comment_text").value
        const comment_show_info = document.getElementById("form_comment_show_info").checked
        const username = getCookie("username")

        if (comment_text == '' || document_id == '') {
            notyf.error('لطفا تمامی فیلد ها را پر نمایید.');
            return
        }

        /* Post Comment */
        const request_link = 'http://' + location.host + "/CreateDocumentComment/" + document_id + "/" + encodeURIComponent(comment_text) + "/" + username + "/" + comment_show_info + "/" + comment_time + "/";
        const response = await fetch(request_link).then(response => response.json());
        const comment_id = response["comment_id"]

        let hash_tags_in_document_comment_text = comment_text.match(/#(\S+)/g); // returns an array with the matches. returns null if no match is found.
        if (hash_tags_in_document_comment_text != null) {
            for (let i = 0; i < hash_tags_in_document_comment_text.length; i++) {
                let hash_tag = hash_tags_in_document_comment_text[i];
                let hash_tag_name = hash_tag.slice(1);
                let hash_tag_link = 'http://' + location.host + "/CreateHashTagForDocumentComment/" + comment_id + "/" + encodeURIComponent(hash_tag) + "/";
                const hash_tag_response = await fetch(hash_tag_link).then(response => response.json());
            }
        }


        notyf.success('نظر شما با موفقیت ثبت شد');
        document.getElementById("form_comment_text").value = "";
        await ShowDocumentComment();

    } catch (e) {
        notyf.error('لطفا دوباره تلاش کنید.');
    }

}

async function SubmitDocumentNote(e) {

    // var todayFa = new Date().toLocaleDateString('fa-IR');
    let options = {year: 'numeric', month: '2-digit', day: '2-digit'};
    let todayFa = new Date().toLocaleDateString('fa-IR-u-nu-latn', options);
    todayFa = todayFa.replace("/", "-")
    todayFa = todayFa.replace("/", "-")
    // console.log(todayFa);

    // var todayEn = new Date();
    // var dd = todayEn.getDate();
    // var mm = todayEn.getMonth()+1;
    // var yyyy = todayEn.getFullYear();
    // if(dd<10)
    // {
    //     dd='0'+dd;
    // }
    // if(mm<10)
    // {
    //     mm='0'+mm;
    // }
    // todayEn = dd+'-'+mm+'-'+yyyy;
    // console.log(todayEn);

    e.preventDefault()
    try {
        const document_id = document.getElementById("document").value
        const note_text = document.getElementById("form_note_text").value
        let note_label = document.getElementById("form_note_label").value
        const username = getCookie("username")

        if (note_label == '') {
            note_label = "بدون برچسب"
        }
        if (note_text == '' || document_id == '') {
            notyf.error('لطفا تمامی فیلد ها را پر نمایید');
            return
        }
        /* Post Note */
        let request_link = 'http://' + location.host + "/CreateDocumentNote/" + document_id + "/" + encodeURIComponent(note_text) + "/" + username + "/" + todayFa + "/" + encodeURIComponent(note_label) + "/";
        // request_link = encodeURIComponent(request_link)
        const response = await fetch(request_link).then(response => response.json());
        const n_id = response['note_id']
        // console.log(n_id);

        let hash_tags_in_text = note_text.match(/#(\S+)/g); // returns an array with the matches. returns null if no match is found.
        console.log(hash_tags_in_text);
        if (hash_tags_in_text != null) {
            for (let i = 0; i < hash_tags_in_text.length; i++) {
                let hash_tag = hash_tags_in_text[i];
                let hash_tag_name = hash_tag.slice(1);
                // let hash_tag_link = 'http://' + location.host + "/CreateHashTagForNote/" + n_id + "/" + hash_tag_name + "/";
                let hash_tag_link = 'http://' + location.host + "/CreateHashTagForNote/" + n_id + "/" + encodeURIComponent(hash_tag) + "/";
                console.log(hash_tag_link);
                const hash_tag_response = await fetch(hash_tag_link).then(response => response.json());
                console.log(hash_tag_response['hash_tags']);
            }
        }

        notyf.success('یادداشت شما با موفقیت ثبت شد.');
        document.getElementById("form_note_text").value = "";
        document.getElementById("form_note_label").value = "";
        await ShowDocumentNote();

    } catch (e) {
        notyf.error('لطفا دوباره تلاش کنید.');
    }

}

async function ShowDocumentComment() {
    const document_id = document.getElementById("document").value
    const username = getCookie("username")

    const request_link = 'http://' + location.host + "/GetDocumentComments/" + document_id + "/" + username + "/";
    const response = await fetch(request_link).then(response => response.json());
    const comments = response['comments']

    let table_data = ''
    for (let i = 0; i < comments.length; i++) {
        let color = 'text-success'
        let commentStatus = 'تایید شده'
        if (comments[i].accepted === 0) {
            color = 'text-warning'
            commentStatus = 'در انتظار تایید'
        }
        if (comments[i].accepted === -1) {
            color = 'text-danger'
            commentStatus = 'رد شده'
        }
        let link = "#"
        if (comments[i].user_id) {
            link = 'http://' + location.host + "/ShowUserProfile/?u=" + comments[i].user_id;
        }
        table_data += `<tr>
                                <td class="text-center">${i + 1}</td>
                                <td class="text-center">
                                    <a href="${link}">${comments[i].first_name} ${comments[i].last_name}</a></td>
                                <td class="text-center"><span class="${color}">${commentStatus}</span></td>

                                <td class="text-center">${comments[i].comment}</td>
                                <td class="text-center">
                                <div class="">
                                    <button type="button" onclick="OnVoteClick('agree', ${comments[i].id})"
                                            class="btn btn-success btn-agree-state">
                                            <i class="bi bi-hand-thumbs-up-fill" style="position:relative;top:-3px;"
                                                                         data-bs-toggle="tooltip"
                                                                         data-bs-placement="top"
                                                                         title="موافق"></i></button>
                                    <button type="button" onclick="OnVoteClick('disagree', ${comments[i].id})"
                                            class="btn btn-danger btn-agree-state">
                                           <i class="bi bi-hand-thumbs-down-fill" style="position:relative;top:-3px;"
                                                                         data-bs-toggle="tooltip"
                                                                         data-bs-placement="top"
                                                                         title="مخالف"></i></button>
                                </div>
                            </td>
                            <td class="text-center cursor-pointer" id="comment_agree" data-bs-target="#VoteDetailModal" data-bs-toggle="modal" onclick="VoteDetailFunction(${comments[i].id}, true)">${comments[i].agreed_count}</td>
                            <td class="text-center cursor-pointer" id="comment_disagree" data-bs-target="#VoteDetailModal" data-bs-toggle="modal" onclick="VoteDetailFunction(${comments[i].id}, false)">${comments[i].disagreed_count}</td>
                            <td class="text-center" id="comment_date" >${comments[i].time}</td>
                         </tr>`
    }
    if (comments.length == 0) {
        table_data = ` <tr>
                            <td class="text-center" id="comment_number">-</td>
                            <td class="text-center" id="comment_first_name">-</td>
                            <td class="text-center" id="follow">-</td>
                            <td class="text-center" id="comment_text">-</td>
                            <td class="text-center">-</td>
                            <td class="text-center" id="comment_agree">-</td>
                            <td class="text-center" id="comment_disagree">-</td>
                            <td class="text-center" id="comment_date">-</td>
                         </tr>`
    }
    document.getElementById('comments_table_body').innerHTML = table_data;
    $('.cm_table').footable({
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
            "enabled": false
        },
        "sorting": {
            "enabled": true
        }
    });
}

async function ShowDocumentNote() {
    const document_id = document.getElementById("document").value
    const username = getCookie("username")

    const request_link = 'http://' + location.host + "/GetDocumentNotes/" + document_id + "/" + username + "/";
    const response = await fetch(request_link).then(response => response.json());
    // const notes = response['notes']
    let notes = response['notes'].sort(function (a, b) {
        if (a.starred == b.starred) {
            return 0;
        } else if (a.starred == true) {
            return -1;
        } else {
            return 1;
        }
    })

    let table_data = ''
    for (let i = 0; i < notes.length; i++) {
        if (notes[i].label === null) {
            notes[i].label = "بدون برچسب"
        }
        if (notes[i].starred) {
            table_data += `<tr>
                                    <td class="text-center" id="note_number_${i + 1}">${i + 1}</td>
                                    <td class="text-center" id="note_text_${i + 1}">${notes[i].note}</td>
                                    <td class="text-center" id="note_time_${i + 1}">${notes[i].time}</td>
                                    <td class="text-center" id="note_label_${i + 1}">${notes[i].label}</td>
                                    <td class="text-center" >
                                        <button value="0" style="border: none;" onclick="ToggleStar('${notes[i].id}','note_starred_${i + 1}')" id="note_starred_${i + 1}">
                                            <span class="fa fa-star checked"></span>
                                        </button>
                                    </td>
                                    <td class="text-center " id="note_download_${i + 1}">
                                        <div class="text-center">
                                            <button type="button" id="document_download" onclick="generatePDFNote('${notes[i].document_name}','${notes[i].time}','${notes[i].note}')"
                                                class="btn d-flex float-center  mr-2 ">
                                                PDF
                                            </button>
                                        </div>
                                    </td>
                            </tr>`
        } else {
            table_data += `<tr>
                                    <td class="text-center" id="note_number_${i + 1}">${i + 1}</td>
                                    <td class="text-center" id="note_text_${i + 1}">${notes[i].note}</td>
                                    <td class="text-center" id="note_time_${i + 1}">${notes[i].time}</td>
                                    <td class="text-center" id="note_label_${i + 1}">${notes[i].label}</td>
                                    <td class="text-center" >
                                        <button value="1" style="border: none;" onclick="ToggleStar('${notes[i].id}','note_starred_${i + 1}')"  id="note_starred_${i + 1}">
                                            <span class="fa fa-star"></span>
                                        </button>
                                    </td>
                                    <td class="text-center " id="note_download_${i + 1}">
                                        <div class="text-center">
                                            <button type="button" id="document_download" onclick="generatePDFNote('${notes[i].document_name}','${notes[i].time}','${notes[i].note}')"
                                                class="btn d-flex float-center  mr-2 ">
                                                PDF
                                            </button>
                                        </div>
                                    </td>
                            </tr>`
        }
    }
    if (notes.length == 0) {
        table_data = `<tr>
                                <td class="text-center" id="note_number">-</td>
                                <td class="text-center" id="note_text">-</td>
                                <td class="text-center" id="note_time">-</td>
                                <td class="text-center" id="note_label">-</td>
                                <td class="text-center" id="note_starred">-</td>
                                <td class="text-center" id="note_download">-</td>
                        </tr>`
    }
    document.getElementById('notes_table_body').innerHTML = table_data;
    $('.note_table').footable({
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
            "enabled": false
        },
        "sorting": {
            "enabled": true
        }
    });
}

async function ToggleStar(note_id, star_id) {
    const request_link = 'http://' + location.host + "/ToggleNoteStar/" + note_id + "/";
    console.log(request_link)
    fetch(request_link).then(response => response.json()).then(response => {
        if (response['starred']) {
            document.getElementById(star_id).innerHTML = `<span class="fa fa-star checked"></span>`
        } else {
            document.getElementById(star_id).innerHTML = `<span class="fa fa-star"></span>`
        }
    }).catch(error => {
            console.log(error)
        }
        ,)
}

async function OnVoteClick(state, document_comment) {
    try {
        const username = getCookie("username")
        const request_link = 'http://' + location.host + "/changeVoteState/" + username + "/" + document_comment + "/" + state + "/";
        let response = await fetch(request_link);
        if (state == "agree") {
            notyf.success('شما با این نظر موافقت کردید');

        } else if (state == "disagree") {
            notyf.error('شما با این نظر مخالفت کردید');
        }
    } catch (err) {
        notyf.error('عملیات ناموفق بوده است');
    }
    ShowDocumentComment()
}