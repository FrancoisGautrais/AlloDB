function api(s){
    if(s[0]=="/") return "/api"+s
    else return "/api/"+s
}


var MODALS={}

function modal(s, fct=null, args=null)
{
    obj = MODALS[s]
    obj.open()
    if(fct!=null) {
        fct(args)
    }
}



function modalClose(s, fct=null, args=null)
{
    obj = MODALS[s]
    obj.close()
    if(fct!=null) {
        fct(args)
    }
}

function _confirmClose(after)
{
    modalClose("confirm")

}

function confirm(title, text, onYes, onNo=null)
{
    $("#confirm-title").html(title)
    $("#confirm-text").html(text)
    $("#confirm-no").off("click")
    $("#confirm-no").on("click", function(){
        modalClose("confirm")
        if(onNo) onNo()
     })

    $("#confirm-yes").off("click")
    $("#confirm-yes").on("click", function(){
        modalClose("confirm")
        if(onYes) onYes()
     })
     modal("confirm")
}

function loading(text)
{
    $("#loading-text").html(text)
    modal("loading")
}

function error(title, text)
{
    $("#error-title").html(title)
    $("#error-text").html(text)
    modal("error")
}


document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.sidenav');
    var instances = M.Sidenav.init(elems, {});
    M.updateTextFields();
    $(function() {
            M.updateTextFields();
    });
});

function url(_url){ window.location.href=_url}
function ajaxget(_url, success=null, error=null){
    $.ajax({
        type: "get",
        url: _url,
        success: success,
        error: error
    })
}

$(document).ready(function(){

    $('.modal').modal();
    $('.modal').each(function(i, obj){
        MODALS[obj.attributes["id"].value]=M.Modal.getInstance(obj)
    })
    $('.dropdown-trigger').dropdown();

    if (typeof main === "function") {
        main();
    }
    $('select').formSelect();
    $("select").each(function(x,y){
        x=$(y)
        attr=x.attr("name")
        if(attr){
            x.parent().find("input").attr("name", attr)
        }
    })
    $('.tooltipped').tooltip();
})

function clearTextSelection()
{
    var sel = window.getSelection ? window.getSelection() : document.selection;
    if (sel) {
        if (sel.removeAllRanges) {
            sel.removeAllRanges();
        } else if (sel.empty) {
            sel.empty();
        }
    }
}

