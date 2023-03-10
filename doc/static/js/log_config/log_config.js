async function insert_log(message, file_name, line, level){
    const request_link = 'http://' + location.host + "/save_log/"

    let form_data = new FormData();
    form_data.append("message", message);
    form_data.append("file_name", file_name);
    form_data.append("line", line);
    form_data.append("level", level);

    $.ajax({
        url: request_link,
        data: form_data,
        type: "POST",
        contentType: false,
        processData: false,
        async: true,
    })
}

window.onerror = async function(message, source, line, col, error) {
    await insert_log(message, source, line, error)
    return true;
};