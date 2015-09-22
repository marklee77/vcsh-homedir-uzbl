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
        var frameList = this.getFrameList();
        var hrefList = new Array();
        for (var i = 0; i < frameList.length; i++) {
            hrefList.push(frameList[i].location.href);
        }
        return hrefList;
    },

    getFormDataListPageDict: function() {
        var frameList = this.getFrameList();
        var formDataListPageDict = {};

        for (var i = 0; i < frameList.length; i++) {
            var frame = frameList[i];
            try {
                var frameFormList = frame.document.getElementsByTagName('form');
                var formDataList = [];
                for (var j = 0; j < frameFormList.length; j++) {
                    var form = frameFormList[j];
                    var formData = {'name': form.name,
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
                formDataListPageDict[frame.location.href] = formDataList;
            }
            catch (err) { }
        }
        return formDataListPageDict;
    },

    updateForms: function(formDataDict) {
        var frameList = this.getFrameList();

        for (var i = 0; i < frameList.length; i++) {
            var frame = frameList[i];
            var frameFormDataList = formDataDict[frame.location.href];
            try {
                frameFormList = frame.document.getElementsByTagName('form');
                for (var j = 0; 
                    j < frameFormList.length && j < frameFormDataList.length; 
                    j++) 
                {
                    var form = frameFormList[j];
                    var formData = frameFormDataList[j];
                    for (var k = 0; j < formData.elements.length; k++) {
                        var elementData = formData.elements[k];
                        var element = form.elements[elementData.name];
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
