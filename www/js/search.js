var selectAdd = null
var critereListDiv = null
var critereContentDiv = null

function option(label, value) {
    return $('<li> <a onclick="onSelectCritereChange(\''+value+'\')">'+label+'</a></li>')
}

function loadRequest(a)
{

    a=REQUEST_LIST[a]
    var fields = a.fields;
    var values =  a.values;
    clearCriteres();
    for( var key in fields){
        var field = fields[key]
        onSelectCritereChange(field)
    }

    for (var keys in values) {
        var elem = $("[id^=widget-][id$='"+keys+"']")
        var val = values[keys]
        var id = elem.attr("id")
        if (id && id.startsWith("widget-sb")) {
            if(val) val="true"
            else if(val==false) val="false"
        }
        elem.val(val)
    }
    $("select").formSelect()
    modalClose("load_requests")
}

function updateSelecteAdd()
{
    var list = []
    selectAdd.empty()
    $("#criteres-list > div[data-label]").each(function(i, elem){
        elem=$(elem)
        selectAdd.append(option(elem.attr("data-label"), elem.attr("data-field")))
    })
}

function onRemoveCritere(x)
{
    var input = x.parent().find("div[data-label]")
    critereListDiv.append(input)
    x.parent().remove()
    updateSelecteAdd()
}

function clearCriteres()
{
    $("#criteres-content").find(".a-critere").each(function(i, elem){
        onRemoveCritere($(elem))
    })
}

function getResults()
{
    var values = {}
    $("#criteres-content").find("[id^=widget-").each(function(i ,elem){
        elem = $(elem)
        var elemDict=get_widget_val(elem)
        values=Object.assign(values, elemDict)

    })
    var fields = []
    $("#criteres-content").find("div[data-field]").each(function(i ,elem){
        fields.push($(elem).data("field"))
    })

    var out = {
        values: values,
        fields : fields
    }
    return out
}

var onSelectCritereChangeChanging = false;

function onSelectCritereChange(val)
{
    if(onSelectCritereChangeChanging) return
    onSelectCritereChangeChanging=true
    var elem = $("#criteres-list > div[data-field='"+val+"']")
    var icon = $('<a class="btn row col fond-color-1 a-critere" onclick="onRemoveCritere($(this))"><i class="material-icons" >remove</i></a>')
    var bound = $('<div class="row col s12"></div>')
    var root = $('<div class="row col s12"></row>')
    bound.append(elem)
    root.append(icon)
    root.append(bound)
    critereContentDiv.append(root)
    updateSelecteAdd()
    onSelectCritereChangeChanging=false
}

$(document).ready(function(){
    selectAdd = $("#dropdown-criteres")
    critereListDiv = $("#criteres-list")
    critereContentDiv = $("#criteres-content")
    updateSelecteAdd();

    $("#widget-it-match").autocomplete()
    $("#widget-it-match").keypress(function(evt) { if(evt.which==13) send_request() })
    $("#widget-it-match").keyup(function() { on_autocomplete_up($("#widget-it-match"), "name") })

    $("#widget-it-actor").autocomplete()
    $("#widget-it-actor").keypress(function(evt) { if(evt.which==13) send_request() })
    $("#widget-it-actor").keyup(function() { on_autocomplete_up($("#widget-it-actor"), "actor") })


    $("#widget-it-director").autocomplete()
    $("#widget-it-director").keypress(function(evt) { if(evt.which==13) send_request() })
    $("#widget-it-director").keyup(function() { on_autocomplete_up($("#widget-it-director"), "director") })

    _run()
})

var postjson={}

function it_val(x){ return (x.length==0)?null:x  }
function itn_val(x){ return (x.length==0)?null:parseInt(x)  }
function itf_val(x){ return (x.length==0)?null:parseFloat(x)  }

function s_val(x){ return (x.length==0)?null:x  }
function sm_val(x){ return (x.length==0)?null:x  }
function sb_val(x){ return (x.length==0)?null:(x=="true")  }

function showSaveRequestDialog(){
    $("#it-request").val("")
    modal("save_request")
}

function confirmSaveRequest()
{
    var data = getResults()
    var name=$("#it-request").val()
    data["name"]=name
    loading()
    $.ajax({
        type: 'POST',
        url: api('/request/'+name),
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function (data) {
            M.toast({html: "Requete sauvée"})
            modalClose("loading")
            modalClose("save_request")
        },
        error: function () {
            error("Impossible de sauver la requete")
        }
    });
}

function removeRequest(val)
{
    confirm("Supprimer",
            "Supprimer la requete '"+val+"' ?",
        function () {
            $.ajax({
                type: 'DELETE',
                url: api('/request/'+val),
                success: function (data) {
                    M.toast({ html: "Élément supprimé"})
                },
                error: function () {
                    error("Impossible de supprimer la requete")
                }
            })
        },function(){
            modalClose("loading")
        }
    )
}

function get_widget_val(x){
    var id=x.attr("id").substring(7)
    var type=id.substr(0,id.search("-"))
    var name=id.substr(id.search("-")+1)
    var val=null
    var tmp=null
    switch(type){
        case "it": val=it_val(x.val()); break;
        case "itn": val=itn_val(x.val()); break;
        case "itf": val=itf_val(x.val()); break;
        case "s": val=s_val(x.val()); break;
        case "sm": val=sm_val(x.val()); break;
        case "sb": val=sb_val(x.val()); break;
        default: alert(type+" inconnu")
    }
    obj={}
    obj[name]=val
    return obj
}

function add_widget_val(x){
    postjson = Object.assign(postjson, get_widget_val(x))
}

function send_request(){
    $("#root-widget").find('[id^=widget-]').each(function(a,b){ add_widget_val($(b)) } )
    $('body').append($('<form/>')
      .attr({'action': "/results", 'method': 'post', 'id': 'replacer'})
      .append($('<input/>')
        .attr({'type': 'hidden', 'name': 'json', 'value': JSON.stringify(postjson)})
      )
    ).find('#replacer').submit();
}

