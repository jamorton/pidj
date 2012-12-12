
var userID;
var token;
var compiledTemplates = {};
var songData;

function getTemplate(tid) {
    if (compiledTemplates[tid])
        return compiledTemplates[tid];
    var source = $("#" + tid).html();
    var template = Handlebars.compile(source);
    compiledTemplates[tid] = template;
    return template;
}

function putTpl(tid, targ, params)
{
    $(targ).html(getTemplate(tid)(params));
}

function loggedIn(auth) {
    userID = auth.userID;
    token = auth.accessToken;
    putTpl("tpl-main", "#content");
    reloadQueue();
}

function reloadQueue() {
    $.post("/ajax/queue", {}, function(response) {
        putTpl("tpl-queue", "#queue", response);
    });
}

$(function() {

    FB.init({
        appId: FB_APP_ID,
        status: true,
        cookie: true,
        xfbml: true
    });

    FB.getLoginStatus(function(response) {
        if (response.authResponse)
            loggedIn(response.authResponse);
        else
            putTpl("tpl-login", "#content");
    });

    $(document).on("click", "#login-btn", function() {
        FB.login(function (response) {
            if (response.authResponse)
                loggedIn(response.authResponse);
        });
        return false;
    });

    $(document).on("submit", "#search-form", function() {
        var inpDiv = $("#search-form .search-input");
        var val = inpDiv.val();
        inpDiv.val("");

        putTpl("tpl-modal", "#search-modal", {query: val});
        $("#search-modal").modal("show");

        $.post("/ajax/search", {query: val}, function(response) {
            songData = response.songs;
            for (var i = 0; i < songData.length; i++)
                songData[i]["id"] = i;
            putTpl("tpl-searchlist", "#search-modal .search-list", {songs: songData});
        });

        return false;
    });

    $(document).on("click", ".song-add-button", function() {
        var idx = $(this).attr("data-id");
        var sid = songData[idx].SongID;
        $("#search-modal").modal("hide");
        $.post("/ajax/add", {songid: sid}, function(response) {
            reloadQueue();
        });
        return false;
    });

    $(document).on("click", "a[rel=external]", function() {
        window.open(this.href, "pidjGsWindow", "width=800, height=600");
        return false;
    });
});
