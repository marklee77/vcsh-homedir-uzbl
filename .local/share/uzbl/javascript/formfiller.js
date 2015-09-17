uzbl.formfiller = {

    getForms: function(frame) {
        var forms = new Array();

        try {
            frameForms = frame.document.getElementsByTagName('form');
            for (var j = 0; j < frameForms.length; j++) {
                forms.push(frameForms[j]);
            }
        }
        catch (err) { }

        for (var i = 0; i < frame.frames.length; i++) {
            forms.concat(getForms(frame.frames[i]);
        }

        return forms;
    },

    dump: function() {
        var allFormsData = [];
        var forms = this.getForms();

        for (var i = 0; i < forms.length; i++) {
            var formData = {'name': forms[i].name, 'elements': []}
            for(var j = 0; j < forms[i].elements.length; j++) {
                var element = forms[i].elements[j];
                if (element.name == '') continue;
                elementData = {'name': element.name, 'type': element.type, 
                               'value': element.value};
                if (['checkbox', 'radio'].indexOf(element.type) > -1) {
                    elementData['checked'] = element.checked;
                }
                formData['elements'].push(elementData)
            }
            allFormsData.push(formData)
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
