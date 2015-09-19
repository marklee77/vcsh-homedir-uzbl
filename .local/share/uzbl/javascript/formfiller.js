uzbl.formfiller = {

    getFrames: function(frame) {
        var frames = new Array(frame);

        for (var i = 0; i < frame.frames.length; i++) {
            frames = frames.concat(this.getFrames(frame.frames[i]))
        }

        return frames;
    },

    dump: function() {
        var allFormsData = [];
        var frames = this.getFrames(window);

        for (var i = 0; i < frames.length; i++) {
            try {
                forms = frames[i].document.getElementsByTagName('form');
                for (var j = 0; j < forms.length; j++) {
                    var formData = {'href': frames[i].location.href,
                                    'hostname': frames[i].location.hostname,
                                    'pathname': frames[i].location.pathname,
                                    'name': forms[j].name, 
                                    'elements': []}
                    for(var k = 0; k < forms[j].elements.length; k++) {
                        var element = forms[j].elements[k];
                        if (element.name == '') continue;
                        elementData = {'name': element.name, 
                                       'type': element.type, 
                                       'value': element.value};
                        if (['checkbox', 'radio'].indexOf(element.type) > -1) {
                            elementData['checked'] = element.checked;
                        }
                        formData['elements'].push(elementData)
                    }
                    allFormsData.push(formData)
                }
            }
            catch (err) { }
        }
        return allFormsData;
    },

    // load matches forms by array index and doesn't currently use the form name
    // for matching. Revisit if it turns out to be an issue.
    load: function(allFormsData) {
        var frames = this.getFrames(window);

        for (var i = 0; i < frames.length; i++) {
            var hostname = frames[i].location.hostname;
            var pathname = frames[i].location.pathname;
            var frameFormsData = allFormsData[hostname][pathname]
            try {
                forms = frames[i].document.getElementsByTagName('form');
                for (var j = 0; j < forms.length && j < frameFormsData.length ; j++) {
                    var form = forms[j];
                    var formData = frameFormsData[j];
                    for (var k = 0; j < formData.elements.length; k++) {
                        var elementData = formData.elements[k];
                        try {
                            if (['checkbox', 'radio'].indexOf(elementData.type) > -1) {
                                var elements = form.elements[elementData.name];
                                // if elements is a singleton rather than a collection,
                                // then wrap it in an array.
                                if (!elements.length) {
                                    elements = [elements];
                                }
                                for (l = 0; l < elements.length; l++) {
                                    if (elements[l].value == elementData.value) {
                                        elements[l].checked = elementData.checked;
                                    }
                                }
                            } else {
                                // this bit of ugliness is because elements[name] might 
                                // be a collection if more than one element has the same 
                                // name. In this case we just set the value of the 
                                // first.
                                var element = form.elements[elementData.name];
                                if (element.length) {
                                    element = element[0];
                                }
                                element.value = elementData.value;
                            }
                        }
                        catch (err) { }
                    }
                }
            }
            catch (err) { }
        }
 
    },
}
