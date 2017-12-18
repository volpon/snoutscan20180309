$.fn.serializeObject = function () {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function () {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

function getCookie(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) {
                c_end = document.cookie.length;
            }
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}

function set_access_token(token, profile) {

    window.sessionStorage.accessToken = token;

    document.cookie = "access_token=" + token;
    document.cookie = "access_profile=" + profile;
}

function set_jwt_auth_header(xhr) {
    xhr.setRequestHeader("Authorization", "JWT " + window.sessionStorage.accessToken)
}

function clear_access_token() {

    window.sessionStorage.accessToken = null;

    document.cookie = "access_token=";
    document.cookie = "access_profile=";
}
