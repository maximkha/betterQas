function QueryForAnswer(question, callB)
{
    var request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) {
                callB(JSON.parse(request.responseText));
                // console.log("get!")
            } else if (this.response == null && this.status === 0) {
                console.log("The computer appears to be offline.");
            } else {
                console.log("???")
            }
        }
    };
    request.open("GET", "http://127.0.0.1:5000/?question=" + encodeURIComponent(question) + "&qtype=" + encodeURIComponent(type), true);
    request.send(null);
}

function runquery()
{
    QueryForAnswer(document.getElementById("question").value, disp)
}

function disp(resp)
{
    if (!resp["error"])
    {
        document.getElementById("outp").innerHTML = resp["results"].join("<br>");
    }
}