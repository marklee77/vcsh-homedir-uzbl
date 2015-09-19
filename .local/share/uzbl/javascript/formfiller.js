uzbl.formfiller = {

    getFrameList: function(frame) {
        var frameList = new Array(frame);

        for (var i = 0; i < frame.frames.length; i++) {
            frameList = frameList.concat(this.getFrames(frame.frames[i]))
        }

        return frameList;
    },

    dump: function() {
        var frameList = this.getFrames(window);
        var formDataList = [];

        for (var i = 0; i < frameList.length; i++) {
            var frame = frameList[i];
            try {
                var formList = frame.document.getElementsByTagName('form');
                for (var j = 0; j < formList.length; j++) {
                    var form = formList[j];
                    var formData = {'href': frame.location.href,
                                    'hostname': frame.location.hostname,
                                    'pathname': frame.location.pathname,
                                    'name': form.name,
                                    'elements': []}
                    for(var k = 0; k < form.elements.length; k++) {
                        var element = form.elements[k];
                        if (element.name == '') continue;
                        elementData = {'name': element.name,
                                       'type': element.type,
                                       'value': element.value};
                        if (['checkbox', 'radio'].indexOf(element.type) > -1) {
                            elementData['checked'] = element.checked;
                        }
                        formData['elements'].push(elementData)
                    }
                    formDataList.push(formData)
                }
            }
            catch (err) { }
        }
        return formDataList;
    },

    // load matches forms by array index and doesn't currently use the form name
    // for matching. Revisit if it turns out to be an issue.
    load: function(formDataDict) {
        var frameList = this.getFrames(window);

        for (var i = 0; i < frameList.length; i++) {
            var frame = frameList[i];
            var hostname = frame.location.hostname;
            var pathname = frame.location.pathname;
            var frameFormDataList = formDataDict[hostname + "/" + pathname]
            try {
                frameFormList = frame.document.getElementsByTagName('form');
                for (var j = 0; 
                     j < frameFormList.length && j < frameFormDataList.length; 
                     j++) 
                {
                    var form = frameFormList[j];
                    var formData = frameFormDataList[j];
                    for (var k = 0; j < formData.elements.length; k++) {
                        var element = form.elements[elementData.name];
                        var elementData = formData.elements[k];
                        try {
                            if (['checkbox', 'radio'].indexOf(elementData.type) 
                                > -1) 
                            {
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
