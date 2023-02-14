
const html_value = `<button type="button" id="HooshyarModalBtn" class="btn d-none modal_btn" data-bs-toggle="modal"
                    data-bs-target="#HooshyarModal"></button>
                    <div class="modal fade" id="HooshyarModal" tabindex="-1" role="dialog" aria-labelledby="HooshyarModalHeader" aria-hidden="true">
                        <div class="modal-dialog" role="document">
                          <div class="modal-content">
                            <div class="modal-header">
                                <div class="d-flex" style="flex-direction: row-reverse;">
                                    <div class="icon-parent" id="HooshyarModalIconParent">
                                        <i class="icon-child fa fa-exclamation" id="HooshyarModalIcon"></i>
                                    </div>
                                    <h5 class="modal-title" id="HooshyarModalHeader">
                                    </h5>
                                </div>
                              <button type="button" class="closeset closeModal" data-dismiss="modal" aria-label="Close" style="color: #4F4F4F;">
                              &times;
                              </button>
                            </div>
                            <div class="modal-body" id="HooshyarModalBody">
                            </div>
                            <div class="modal-footer" style="text-align: center; justify-content: center">
                              <button type="button" class="btn btn-secondary btn-understand closeModal" data-dismiss="modal">متوجه شدم</button>
                            </div>
                          </div>
                        </div>
                    </div>`

setTimeout(() => {
  document.getElementById("HooshyarAlert").innerHTML = html_value
}, "1000")


function HooshyarAlertShow(alert_header_text, alert_body_text, icon_type)
{

    let icon_parent_color = NaN
    let icon_color = NaN
    if (icon_type === 1)
    {
        icon_parent_color = "#FDCECE"
        icon_color = "#F30C0C"
    }
    else if (icon_type === 2)
    {
        icon_parent_color = "#FEEED7"
        icon_color = "#C27605"
    }

    document.getElementById("HooshyarModalIconParent").style.backgroundColor = icon_parent_color
    document.getElementById("HooshyarModalIcon").style.backgroundColor = icon_color
    document.getElementById("HooshyarModalHeader").innerText = alert_header_text
    document.getElementById("HooshyarModalBody").innerText = alert_body_text

    const closeModalBtns = document.getElementsByClassName("closeModal")
    for (row of closeModalBtns) {
        row.onclick = function () {
            $("#HooshyarModal").modal("hide")
        }
    }

    $("#HooshyarModalBtn").click()

}