uzbl.formfiller = {

    // this is pointlessly duplicated in uzbl.follow
    textInputTypes: [
      'text', 'password', 'search', 'email', 'url', 'number', 'range', 'color',
      'date', 'month', 'week', 'time', 'datetime', 'datetime-local'
    ]

    ,

    // this is pointlessly duplicated in uzbl.follow
    inputTypeIsText: function(type) {
        return uzbl.formfiller.textInputTypes.indexOf(type) >= 0;
    }

    ,

    dump: function() {
        var retval = ['test'];
        var allFrames = new Array(window);

        for (var i = 0; i < window.frames.length; i++) {
            allFrames.push(window.frames[i]);
        }

        for (var i = 0; i < allFrames.length; i++) {
            try {
                var forms = allFrames[i].document.getElementsByTagName('form');
                for(var j = 0; j < forms.length; j++) {
                    var form = forms[j];
                    retval.push({'name': form.name, 'elements': []})
                    for(var k = 0; k < form.elements.length; k++) {
                        var element = form.elements[k];
                        /*
                        retval[j]['elements'].push({'name': element.name, 
                                                    'type': element.type, 
                                                    'value': element.value});
                        if (element.type == 'checkbox' || element.type == 'radio' ) {
                            retval[j]['elements'][k]['checked'] = input.checked?1:0];
                        }
                        */
                    }
                }

            }
            catch (err) { }
        }
        return JSON.stringify(retval);
    }

    ,

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
