///<reference path="https://code.jquery.com/jquery-2.2.4.js"/>
///<reference path="../lib/md5.js"/>


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
        $(".side-menu").load('ui/left_panel.html').show();
        $(".side-body").load('ui/system', function (resp, status, xhr) {
            if (status == "success") {
                $(document).trigger('system_redirect');
            }
        });
    }

    redirect_to_login() {
        var self = this;
        $(".side-menu").empty().hide();
        $(".side-body").empty();
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
        console.log("submit");

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
    console.log(document.getElementById(id).value);
    val = document.getElementById(id).value;
    id = id.slice(5);
    console.log(id);
    ws.send(id + ',' + val);
}

function system_init() {
    $('.navbar-toggle').click(function () {
        $('.navbar-nav').toggleClass('slide-in');
        $('.side-body').toggleClass('body-slide-in');
    });
    $(".room-anchor").click(function () {
        $('.navbar-nav').toggleClass('slide-in');
        $('.side-body').toggleClass('body-slide-in');
    });
    $("input").on('change', send_value)
    ws = new WebSocket("ws://" + location.host + "/websocket");

    ws.onmessage = function (evt) {
        console.log(evt.data);
        var data = evt.data.split(',');
        var id = data[0];
        var value = data[1];
        var element = document.getElementById(id);
        element.innerText = value;
    }


}

$(document).ready(function () {
    $(document).on('system_redirect', system_init)
    var auth = new Auth();
    if (auth.is_logged_in()) {
        auth.redirect_to_system();
    }
    else {
        auth.redirect_to_login();
    }
});