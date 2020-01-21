from .elem import *

def mat_select(id, label, options, name=None, multiple=False, mobile=False, classes=[], optionsClasses=[]):
    lbl=htmllabel(label)
    print(name)
    select=htmlselect(id=id)
    select.add_class(classes)
    if mobile: select.add_class("browser-default")
    if multiple: select.attrs["multiple"]=None
    if name: select.attrs["name"]=name
    for k in options:
        oa={"value" : k}
        select.append(htmloption(options[k], classes=optionsClasses, attrs=oa))
    return lbl.after(select)

def mat_input_text(id, label, type="text", value="", disable=False, name=""):
    lbl=htmllabel(value, attrs={"for" : id})
    input=html_input(id, type, ["validate"], attrs={
        "placehoder" : label,
        "disabled" if disable else "": None,
        "name": name
    })
    return  htmldiv([input, lbl], classes="input-field")

def mat_switch(id, labelOn, labelOff="", name=""):
    if name: input=html_input(id, "checkbox", attrs={ "name": name}).after(htmlspan(classes="lever"))
    else: input=html_input(id, "checkbox").after(htmlspan(classes="lever"))

    return  htmldiv(htmllabel([ labelOn, input, labelOff]), classes="switch")

def mat_row(content, classes="col s12"):
    if isinstance(content, (list, tuple)): content="\n".join(content)
    x=htmldiv(content, classes="row ")
    return  x.add_class(classes)

def mat_col(content, classes="s12"):
    if isinstance(content, (list, tuple)): content="\n".join(content)
    x=htmldiv(content, classes="col ")
    return  x.add_class(classes)