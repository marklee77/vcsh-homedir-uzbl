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
                    var formData = {'name': forms[j].name, 
                                    'href': frames[i].location.href,
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
        var forms = this.getForms();

        for (var i = 0; i < forms.length && i < allFormsData.length; i++) {
            var formData = allFormsData[i];
            for (var j = 0; j < formData.elements.length; j++) {
                var elementData = formData.elements[j];
                try {
                    if (['checkbox', 'radio'].indexOf(elementData.type) > -1) {
                        var elements = forms[i].elements[elementData.name];
                        // if elements is a singleton rather than a collection,
                        // then wrap it in an array.
                        if (!elements.length) {
                            elements = [elements];
                        }
                        for (k = 0; k < elements.length; k++) {
                            if (elements[k].value == elementData.value) {
                                elements[k].checked = elementData.checked;
                            }
                        }
                    } else {
                        // this bit of ugliness is because elements[name] might 
                        // be a collection if more than one element has the same 
                        // name. In this case we just set the value of the 
                        // first.
                        var element = forms[i].elements[elementData.name];
                        if (element.length) {
                            element = element[0];
                        } 
                        element.value = elementData.value;
                    }
                }
                catch (err) { }
            }
        }
    },
}
