
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
    setInterval(reloadQueue, 5000);
}

var stInterval = null;
var curSong = null;

function updateTime()
{
    var seconds = Number(curSong.duration) - Math.round((curSong.finish - new Date()) / 1000);
    if (seconds >= curSong.duration) {
        clearInterval(stInterval);
        $("#playing").html("");
        return;
    }
    var minutes = Math.floor(seconds / 60);
    seconds = seconds % 60;
    if (seconds < 10)
        seconds = "0" + seconds;
    $("#song-minutes").text(minutes);
    $("#song-seconds").text(seconds);
}


var oldQueue = "";
function reloadQueue() {
    $.post("/ajax/queue", {}, function(response) {
        var str = JSON.stringify(response);
        if (str == oldQueue)
            return;

        oldQueue = str;
        putTpl("tpl-queue", "#queue", response);

        if (response.playing) {
            var song = response.playing;
            song.added = new Date(song.added);
            song.finish = new Date(song.finish);
            var mins = Math.floor(Number(song.duration) / 60);
            var secs = mins % 60;
            if (secs < 10)
                secs = "0" + secs;
            song.durationStr = mins + ":" + secs;
            curSong = song;
            stInterval = setInterval(updateTime, 100);


            putTpl("tpl-playing", "#playing", song);
        }

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
