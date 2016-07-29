///<reference path="https://code.jquery.com/jquery-2.2.4.js"/>
///<reference path="../lib/md5.js"/>


function log(msg, color) {
    color = color || "black";
    bgc = "White";
    switch (color) {
        case "success": color = "Green"; bgc = "LimeGreen"; break;
        case "info": color = "DodgerBlue"; bgc = "Turquoise"; break;
        case "error": color = "Red"; bgc = "Black"; break;
        case "start": color = "OliveDrab"; bgc = "PaleGreen"; break;
        case "warning": color = "Tomato"; bgc = "Black"; break;
        case "end": color = "Orchid"; bgc = "MediumVioletRed"; break;
        default: color = color;
    }

    if (typeof msg == "object") {
        console.log(msg);
    } else if (typeof color == "object") {
        console.log("%c" + msg, "color: PowderBlue;font-weight:bold; background-color: RoyalBlue;");
        console.log(color);
    } else {
        console.log("%c" + msg, "color:" + color + ";font-weight:bold; background-color: " + bgc + ";");
    }
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length,c.length);
        }
    }
    return "";
}

class Communication {
    constructor() {

    }

    post(path, data) {
        
    }

    load(place, path) {

    }
}

class Auth {
    constructor() {
        this.user_name = getCookie('name');
    }

    is_logged_in() {
        if (this.user_name != '') {
            return true;
        }
        else {
            return false;
        }
        return false
    
    }

    redirect_to_system() {
        $(".auth").empty();
        $(".navigation-bar").load('ui/navigation_bar').show();
        $(".system-content").load('ui/system', function (resp, status, xhr) {
            if (status == "success") {
                $(document).trigger('system_redirect');
            }
        });
    }

    redirect_to_login() {
        document.cookie = "name="; //clear name cookie 
        var self = this;
        $(".navigation-bar").empty();    //hide and empty navigation bar
        $(".system-content").empty();
        $(".auth").load('auth/login_page.html', $.proxy(function (resp, status, xhr) {
            if (status = "success") {
                $('#submit-button').on("click", $.proxy(self.submit_login, this));
            }
        },this));
    }

    submit_login() {
        var user_name = $("#name").val();
        var pwd = md5($("#pwd").val());

        var data = JSON.stringify({
            action: 'login',
            name: user_name,
            password: pwd
        });
        log("submit login", 'info');

        $.post("auth", data, $.proxy(function (resp, status) {
            if (status == "success") {
                if (resp == "ok") {
                    document.cookie = "name=" + user_name;
                    this.redirect_to_system();
                }
            }
        }, this))
    }

}

function send_value(event) {
    var id = event.currentTarget.id;
    val = document.getElementById(id).value;
    id = id.slice('input'.length);
    console.log(id, val);
    ws.send(id + ',' + val);
}

function system_init() {

    window.addEventListener("hashchange", function () { scrollBy(0, -60) });

    $("input").on('change', send_value)
    ws = new WebSocket("ws://" + location.host + "/websocket");

    ws.onmessage = function (evt) {
        log(evt.data, 'success');
        var data = evt.data.split(',');
        var id = data[0];
        var value = data[1];
        var element = document.getElementById(id);
        var action = data[2];
        if (action == undefined) {
            element.innerText = value;
        }
        else if (action == 's') {
            if (value == 2){
                $(element).addClass("on");
                $(element).removeClass("off");
                log('class on');
            }
            else if (value == 1) {
                $(element).removeClass("on");
                $(element).addClass("off");
                log('class off');
            }
        }
    }
}

$(document).ready(function () {
    $(document).on('system_redirect', system_init)
    auth = new Auth();
    if (auth.is_logged_in()) {
        auth.redirect_to_system();
    }
    else {
        
        auth.redirect_to_login();
    }
});