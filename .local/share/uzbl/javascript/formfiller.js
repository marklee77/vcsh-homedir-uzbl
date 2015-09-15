uzbl.formfiller = {

    getForms: function() {
        var forms = new Array();

        var frames = new Array(window);
        for (var i = 0; i < window.frames.length; i++) {
            frames.push(window.frames[i]);
        }

        for (var i = 0; i < frames.length; i++) {
            try {
                frameForms = frames[i].document.getElementsByTagName('form');
                for (var j = 0; j < frameForms.length; j++) {
                    forms.push(frameForms[j]);
                }
            }
            catch (err) { }
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
        return JSON.stringify(allFormsData);
    },
    
    load: function(allFormsData) {
        var forms = this.getForms();

        for (var i = 0; i < forms.length && i < allFormsData.length; i++) {
            for (var j = 0; j < allFormsData[i].elements.length; j++) {
                var elementData = allFormsData[i].elements[j];
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
                    // this bit of ugliness is because elements[name] might be a
                    // collection if more than one element has the same name. In 
                    // this case we just set the value of the first.
                    var element = forms[i].elements[elementData.name];
                    if (element.length) {
                        element = element[0];
                    } 
                    element.value = elementData.value;
                }
            }
        }
    },
}
