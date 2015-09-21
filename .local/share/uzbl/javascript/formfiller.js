uzbl.formfiller = {

    getFrameList: function() {
        var frame = window;
        if (arguments.length > 0) {
            frame = arguments[0];
        }
        var frameList = new Array(frame);

        for (var i = 0; i < frame.frames.length; i++) {
            frameList = frameList.concat(this.getFrameList(frame.frames[i]))
        }

        return frameList;
    },

    getHrefList: function() {
        var frameList = this.getFrameList(window);
        var hrefList = new Array();
        for (var i = 0; i < frameList.length; i++) {
            hrefList.push(frameList[i].location.href);
        }
        return hrefList;
    },

    dump: function() {
        var frameList = this.getFrameList(window);
        var formDataList = [];

        for (var i = 0; i < frameList.length; i++) {
            var frame = frameList[i];
            try {
                var frameFormList = frame.document.getElementsByTagName('form');
                for (var j = 0; j < frameFormList.length; j++) {
                    var form = frameFormList[j];
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

    load: function(formDataDict) {
        var frameList = this.getFrameList(window);

        for (var i = 0; i < frameList.length; i++) {
            var frame = frameList[i];
            var frameFormDataDict = formDataDict[frame.location.href];
            try {
                frameFormList = frame.document.getElementsByTagName('form');
                for (var j = 0; 
                     j < frameFormList.length && j < frameFormDataList.length; 
                     j++) 
                {
                    var form = frameFormList[j];
                    var formData = frameFormDataDict[form.name];
                    for (var k = 0; j < formData.elements.length; k++) {
                        var element = form.elements[elementData.name];
                        var elementData = formData.elements[k];
                        try {
                            if (['checkbox', 'radio'].indexOf(elementData.type) 
                                > -1) 
                            {
                                // if element is a singleton rather than a 
                                // collection, then wrap it in an array.
                                if (!element.length) element = [element];
                                
                                for (l = 0; l < element.length; l++) {
                                    if (element[l].value == elementData.value) {
                                        element[l].checked = 
                                            elementData.checked;
                                    }
                                }
                            } else {
                                // this bit of ugliness is because 
                                // element[name] might be a collection if more 
                                // than one element has the same name. In this 
                                // case we just set the value of the first.
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
