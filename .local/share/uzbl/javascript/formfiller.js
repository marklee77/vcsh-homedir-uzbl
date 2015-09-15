uzbl.formfiller = {

    dump: function() {
        var data = [];
        var allFrames = new Array(window);

        for (var i = 0; i < window.frames.length; i++) {
            allFrames.push(window.frames[i]);
        }

        for (var i = 0; i < allFrames.length; i++) {
            try {
                var forms = allFrames[i].document.getElementsByTagName('form');
                for(var j = 0; j < forms.length; j++) {
                    var form = forms[j];
                    forminfo = {'name': form.name, 'fields': []}
                    for(var k = 0; k < form.elements.length; k++) {
                        var element = form.elements[k];
                        if (element.name == '') continue;
                            elementinfo = { 'name': element.name, 
                                            'type': element.type, 
                                            'value': element.value};
                        if (['checkbox', 'radio'].indexOf(element.type) > -1) {
                            elementinfo['checked'] = element.checked;
                        }
                        forminfo['fields'].push(elementinfo)
                    }
                    data.push(forminfo)
                }

            }
            catch (err) { }
        }
        return JSON.stringify(data);
    },
    
    load: function(data) {
        var allFrames = new Array(window);

        for (var i = 0; i < window.frames.length; i++) {
            allFrames.push(window.frames[i]);
        }

        for (var i = 0; i < allFrames.length; i++) {
            try {
                var forms = allFrames[i].document.getElementsByTagName('form');
            }
            catch (err) { }
        }
    },

    insert: function(fname, ftype, fvalue, fchecked) {
        fname = unescape(fname);
        var allFrames = new Array(window);
        for ( var f = 0; f < window.frames.length; ++f ) {
            allFrames.push(window.frames[f]);
        }
        for ( var j = 0; j < allFrames.length; ++j ) {
            try {
                if ( uzbl.formfiller.inputTypeIsText(ftype) || ftype == 'textarea' ) {
                    allFrames[j].document.getElementsByName(fname)[0].value = fvalue;
                }
                else if ( ftype == 'checkbox' ) {
                    allFrames[j].document.getElementsByName(fname)[0].checked = fchecked;
                }
                else if ( ftype == 'radio' ) {
                    fvalue = unescape(fvalue);
                    var radios = allFrames[j].document.getElementsByName(fname);
                    for ( r=0; r<radios.length; ++r ) {
                        if ( radios[r].value == fvalue ) {
                            radios[r].checked = fchecked;
                        }
                    }
                }
            }
            catch (err) { }
        }
    }
}
