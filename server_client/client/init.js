///<reference path="https://code.jquery.com/jquery-2.2.4.js"/>
///<reference path="../lib/md5.js"/>


class System {
    constructor() {
        this.ws = new WebSocket("ws://" + location.host + "/websocket");
    }

    init(){
        window.addEventListener("hashchange", function () { scrollBy(0, -60) });
        $("input").on('change', $.proxy(this.send_value, this))
        $(".btn").on('click', $.proxy(this.send_value, this))

        this.ws.onmessage = this.get_data
    }

    get_data(evt){
        log(evt.data, 'success');
        var data = evt.data.split(',');
        var id = data[0];
        
        if (id[0] == 'r') {
            id = 'input' + id;
        }

        var value = data[1];
        var element = document.getElementById(id);
        var action = data[2];

        if (id.startsWith('input')) {
            element.value = value;
        }

        else if (action == undefined) {
            element.innerText = value;
        }
        else if (action == 's') {
            if (value == 1){
                $(element).addClass("on");
                $(element).removeClass("off");
                log('class on');
            }
            else if (value == 0) {
                $(element).removeClass("on");
                $(element).addClass("off");
                log('class off');
            }
        }
    }

    send_value(event) {
        var id = event.currentTarget.id;
        var val = document.getElementById(id).value;
        if (val == 'click') {
            val = 1
        }
        console.log(id, val);
        id = id.slice('input'.length);
        this.ws.send(id + ',' + val);
    }

}

class Auth {
    constructor() {
        this.user_name = getCookie('name');
        self = this;
    }

    is_logged_in() {
        console.log(this);
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

auth = new Auth();
system = new System();

$(document).ready(function () {
    $(document).on('system_redirect', $.proxy(system.init, system))
    if (auth.is_logged_in()) {
        auth.redirect_to_system();
    }
    else {
        
        auth.redirect_to_login();
    }
});