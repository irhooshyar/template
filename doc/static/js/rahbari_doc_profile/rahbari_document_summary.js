async function GetTextSummary() {
    document.getElementById("summary_text").innerHTML = "";

    let document_text = ""
    const document_id = document.getElementById("document").value
    const request_link = 'http://' + location.host + "/GetDocumentContent/" + document_id + "/";
    let response = await fetch(request_link).then(response => response.json());
    response = response["document_paragraphs"]

    for (let i = 0; i < response.length; i++) {
        const paragraph_text = response[i]["paragraph_text"]
        if (paragraph_text.length < 100) continue

        document_text += paragraph_text + "\n\r"
    }

    summery(document_text)
}

function summery(text) {
    const link_request = "http://" + location.host + "/GetTextSummary/";
    let form_data = new FormData();
    form_data.append("text", text);

    $.ajax({
        url: link_request,
        data: form_data,
        type: "POST",
        contentType: false,
        processData: false,
        async: true,
    })
        .done(
            function (res) {
                document.getElementById("summary_text").innerHTML = res["text_summary"].replaceAll(" ّ ", "");
            }
        )
        .fail(
            function (res) {
                console.log("fail");
            }
        );
}