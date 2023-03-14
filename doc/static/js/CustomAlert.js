

function HooshyarAlertShow(alert_header_text, alert_body_text, icon_type) {
  let icon_parent_color = "#FDCECE"
  let icon_color = "#F30C0C"
  if (icon_type === 2)
  {
      icon_parent_color = "#FEEED7"
      icon_color = "#C27605"
  }

  alert_body_text = alert_body_text || '';
  const html_value = `<div class="alert" tabindex="-1" role="dialog" aria-labelledby="HooshyaralertHeader" aria-hidden="true">
    <div class="alert-header">
      
      <button type="button" class="closeset" aria-label="Close" style="color: #4F4F4F;" onClick=HooshyarAlertClose()>
        <i class="fa fa-remove" ></i>
      </button>
  
      <h5 class="alert-title"  style="text-align: center; justify-content: center" >
        ${alert_header_text}
      </h5>

      <div class="icon-parent" style="background: ${icon_parent_color}">
        <i class="icon-child fa fa-exclamation" style="background: ${icon_color}"></i>
      </div>
      

    </div>
    <div class="alert-body" id="alertBody" style="text-align: center; justify-content: center">
      ${alert_body_text}
    </div>
    <div class="alert-footer" id="alertFooter" style="text-align: center; justify-content: center">
      <button type="button" id="alertBtn" class="btn btn-secondary btn-understand" onClick=HooshyarAlertClose()>متوجه شدم</button>
    </div>
  </div>`

  

  document.getElementById("HooshyarAlert").innerHTML = html_value
  if (alert_body_text == "ثبت‌نام شما توسط ادمین تایید شده است. از طریق دکمه‌ی زیر، وارد سامانه شوید."){
    let tag = '<a href="http://virtualjuristic.datakaveh.com:7090/login/"><button type="button" id="login-btn" class="btn btn-secondary btn-understand closeModal" data-dismiss="modal">ورود</button></a>';
    document.getElementById("alertFooter").innerHTML += tag;
    document.getElementById("alertBtn").style.display = "none";
  }
  if (alert_body_text == "متاسفانه تایید شما توسط ادمین رد شده است. با پشتیبانی از طریق ایمیل زیر، در تماس باشید."){
    let tag = '<div class="alert-body" style="text-align: center; justify-content: center">support@irhooshyar.com</div>';
    document.getElementById("alertBody").innerHTML += tag;
  }
  if (alert_body_text == "اگر ثبت‌نام را انجام نداده‌اید، بر روی دکمه‌ی زیر کلیک فرمایید."){
    let tag = '<a href="http://virtualjuristic.datakaveh.com:7090/signup/"><button type="button" id="login-btn" class="btn btn-secondary btn-understand closeModal" data-dismiss="modal">ثبت‌نام</button></a>';
    document.getElementById("alertFooter").innerHTML += tag;
    document.getElementById("alertBtn").style.display = "none";
  }
  document.getElementById("HooshyarAlert").style.display = 'flex';

}

function HooshyarAlertClose() {
document.getElementById("HooshyarAlert").innerHTML = ""
document.getElementById("HooshyarAlert").style.display = 'none';
}
