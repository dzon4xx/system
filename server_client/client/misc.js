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
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}
