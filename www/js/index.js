currentFile={
    name : null,
    dir : null,
    path : null,
    isdir : null
}

function setCurrentFile(dir, name, isdir) {
    currentFile={
        name : name,
        dir : dir,
        path : dir+"/"+name,
        isdir : isdir
    }
}

_sort_field=null
_sort_order=null
function _cmp(a,b)
{
    a=a.attributes["data-"+_sort_field].value
    b=b.attributes["data-"+_sort_field].value
    if(_sort_field!="name"){
        a=parseFloat(a)
        b=parseFloat(b)
        console.log(a+" "+b)
        return (_sort_order=="dec")?(a<b):(a>b)
    }
    return (_sort_order=="dec")?(a.toLowerCase()<b.toLowerCase()):(a.toLowerCase()>b.toLowerCase())
}

function sort(field, order) {
    data.user.sort=_sort_field=field
    data.user.order=_sort_order=order
    list=[]
    llist=$(".sortable").each(function(a,b){list.push(b)})
    root=llist.parent()
    llist.remove()
    list.sort(_cmp)
    for(var i in list){
        root.append($(list[i]))
    }

}

function main(){
    autoreplaceall()
    $("#clicktrigger").on("click", function() {
        $("#file").trigger("click");
    });

    $("#file").change(function (){
        modal("loading")
        sendfile()
     });
}

function confirm_modify(){
    x=$("#s_perm").val().join("")+($("#edit_is_hidden").is(":checked")?"h":"")
    data={
        "attrs" : x
    }
    modal("loading")
    console.log(data)
    $.ajax({
            type: 'POST',
            processData: false, // important
            contentType: false, // important
            url: "/file/"+currentFile.path,
            data: JSON.stringify(data),
            headers : {
                "Content-Type": "application/json"
            },
            success: function(jsonData){
                modalClose("loading")
                modalClose("edit_file")
                window.location.reload()
            },
            error : function(_a, _b, _c)
            {
                modalClose("loading")
                error("Impossible de modifier '"+currentFile.name+"'", _a.responseText)
            }
     });


}

function confirm_delete()
{
    confirm("Êtes-vous sûr ?", "Voulez vous vraiment supprimer '"+currentFile.name+"'", function(){
            modal("loading")
            $.ajax({
                type: 'GET',
                processData: false, // important
                contentType: false, // important
                url: "/delete/"+currentFile.path,

                success: function(jsonData){
                    modalClose("loading")
                    modalClose("edit_file")
                    window.location.reload()
                },
                error : function(_a, _b, _c)
                {
                    modalClose("loading")
                    error("Impossible de supprimer '"+currentFile.name+"'", _a.responseText)
                }
            });
        })
}

function _edit_file(data)
{
    modalClose("loading")
    modal("edit_file")
    $("#edit_name").val(data["name"])
    $("#s_perm").val(data.attrs.split(""))
    $('select').formSelect();
    $("#edit_is_hidden").prop('checked', data["attrs"].search("h")>=0);
    M.updateTextFields();
}

function edit_file()
{
    loading("Chargement")
    $.ajax({
        type: 'GET',
        processData: false, // important
        contentType: false, // important
        dataType: 'json',
        url: "/file/"+currentFile.path,

        success: function(jsonData){
            modalClose("loading")
            _edit_file(jsonData)
        },
        error : function(_a, _b, _c)
        {
            modalClose("loading")
            error("Impossible de récupérer les données", _a.responseText)
        }
    });
}


function sendfile()
{
    var data = new FormData();
    data.append("file", $("#file").prop("files")[0])
    loading("Transfert du fichier, merci de patienter")
    $.ajax({
        type: 'POST',
        processData: false, // important
        contentType: false, // important
        data: data,
        dataType: 'text',
        url: "/upload/"+$("#CONST_PATH").html(),
        // in PHP you can call and process file in the same way as if it was submitted from a form:
        // $_FILES['input_file_name']
        success: function(jsonData){
            modalClose("loading")
            window.location.reload()
        },
        error : function(_a, _b, _c)
        {
            modalClose("loading")
            error("Impossible d'envoyer le fichier", _a.responseText)
        }
    });
}

GB=1024*1024*1024
MB=1024*1024
KB=1024

MIME={

}


function min(x,y){ return x>y?x:y }
function padd(x, n=2) {
    x=""+x
    while(x.length<n) x="0"+x
    return x
}

function autoreplace_date(text){
    timestamp=parseFloat(text)
    date = new Date(timestamp * 1000)
    if(data.user.mobile) return padd(date.getDate())+"/"+padd(date.getMonth()+1)+"/"+date.getFullYear()
    else return padd(date.getDate())+"/"+padd(date.getMonth()+1)+"/"+date.getFullYear()+" "+padd(date.getHours())+":"+padd(date.getMinutes())
}


function autoreplace_boundtext(text){
    max_size=MAX_STR_LENGTH
    nline=MAX_STR_LINE
    text = text.length>nline*max_size ? text.substr(0,max_size*nline-3)+"...": text
    out=""
    for(var i=0; i<nline; i++)
    {
        line=min(text.length, text.substr(0, max_size))
        text=text.substr(max_size)
        out+=line+((i<nline)?"<br>":"")
    }
    return out
}

function _append_table(el, key, value){
    el.append($("<tr><td>"+key+"</td><td>"+value+"</td></tr>"))
}

DIR_INFO={
}


function _file_info(el, data, dossier)
{
    attr=""
    cache=data.attrs.toLowerCase().search("h")>0?"Oui":"Non"
    if(data.attrs.toLowerCase().search("r")>=0) attr+="Lecture "
    if(data.attrs.toLowerCase().search("w")>=0) attr+="Écriture "
    if(data.attrs.toLowerCase().search("x")>=0) attr+="Exécution "
    _append_table(el, "Nom", data.name)
    _append_table(el, "Parent", "/"+data.dir)
    _append_table(el, "Création", autoreplace_date(data.creation))
    if(dossier){
        _append_table(el, "Éléments", data.length)
    }else {
        _append_table(el, "Taille", autoreplace_size(data.size))
        _append_table(el, "Type", data.mime)
        _append_table(el, "Téléchargements", data.download)
    }
    _append_table(el, "Permissions", attr)
    _append_table(el, "Caché", cache)
}

function file_info()
{
    name=currentFile.name
    dir=currentFile.dir
    isdir=currentFile.isdir
    modal("loading")
    $("#fi_name").val(currentFile.name)
    tbody=$("#fi_tbody")
    tbody.empty()
    $.ajax({type: 'GET', dataType:"json",
                url: "/file/"+currentFile.path,

                success: function(jsonData){
                    console.log(tbody, jsonData)
                    modalClose("loading")
                    _file_info(tbody,jsonData,isdir)
                    modal("file_info")
                },
                error : function(_a, _b, _c)
                {
                    modalClose("loading")
                    error("Ereur", _a.responseText)
                }
            });
}

function click_open(dir, name, isdir)
{
    clearTextSelection();
    setCurrentFile(dir, name, isdir)
    $("#fc_name").html(name)
    $("#fc_download").html(isdir?"Ouvrir":"Télécharger")
    $("#fc_download_icon").html(isdir?"folder_open":"file_download")

    $("#fc_info_a").on("click", function(){modalClose("file_click"); file_info()})
    $("#fc_download_a").on("click", function(){
        modalClose("file_click");
        window.location.href=(isdir?"/browse/":"/share/")+dir+"/"+name
    })
    $("#fc_modify_a").on("click", function(){modalClose("file_click"); edit_file(dir, name)})
    $("#fc_remove_a").on("click", function(){ modalClose("file_click");confirm_delete()})
    modal("file_click")
    return false;
}

function autoreplace_size(value){
    var m=!data.user.mobile
    if(value>=GB) return (value/GB).toFixed(m?1:0)+(m?" Gio":"G")
    if(value>=MB) return (value/MB).toFixed(m?1:0)+(m?" Mio":"M")
    if(value>=KB) return (value/KB).toFixed(m?1:0)+(m?" Kio":"K")
    return value+" o"
}


MIME_TO_ICON={
    "audio" : { "*": "audiotrack"},
    "video" : { "*": "movie"},
    "image" : { "*": "photo"},
    "text" : { "*": "insert_drive_file" },
    "application" :  {
		//Archives
		"zip,x-bzip,x-tar,x-rar-compressed,bzip2,x-tar+gzip,gzip" : "archive",

		//defaut
		"*" 				: "insert_drive_file"
	},
    "*" : "insert_drive_file"
}

MIME_TO_TYPES={
    "audio" : { "*": "audio"},
    "video" : { "*": "video"},
    "image" : { "*": "image"},
    "text" : { "*": "text" },
    "application" :  {
		//Archives
		"zip,x-bzip,x-tar,x-rar-compressed,bzip2,x-tar+gzip,gzip" : "archive",

		//defaut
		"*" 				: "text"
	},
    "*" : "text"
}


function initMimeTypes(input)
{
	out={ "*" : input["*"]}
	for(var k in input) {
		if(k!="*") {
			for(var s in input[k])
			{
				val=input[k][s]
				list=s.split(",")
				for(var l in list)
					out[k+"/"+list[l]] = val
			}
		}
	}
	return out
}

MIME_TO_ICON=initMimeTypes(MIME_TO_ICON)
MIME_TO_TYPES=initMimeTypes(MIME_TO_TYPES)

function mimeTo(input, mime){
	mime=mime.split("/")
	first=mime[0]
	second=mime[1]
	if( !(first in input) )  return input["*"]
	if( !(second in input[first])) return input[first]["*"]
	return input[first][second]
}

function autoreplace_mime(mime) {  return mimeTo(MIME_TO_ICON, mime) }

function autoreplace_menupath(path)
{
    path=path.split('/')
    acc="/browse/"
    out=[]
    for(p in path){
        if(path[p]!="")
        {
            acc+=path[p]
            out.push($('<li><a href="'+acc+'" class="menu">'+path[p]+'</a></li>'))
            out.push($('<li><i class="material-icons prefix small color-4">chevron_right</i></li>'))
        }
    }
    return out
}

function confrmNewDir(){
    name=$("#new_dir").val()
    modal("loading")
    $.ajax({type: 'GET',
        url: "/createdir/"+data.path+"/"+name,
        success: function(jsonData){
            modalClose("loading")
            window.location.reload()
        },
        error : function(_a, _b, _c)
        {
            modalClose("loading")
            error("Impossible de créer le dossier", _a.responseText)
        }
    });
}

function new_file()
{
    modalClose("add_file_dir")
    $("#file").click()

}

function new_dir()
{
   modalClose("add_file_dir")
   modal("add_dir")
}



function on_new()
{
   modal("add_file_dir")
}