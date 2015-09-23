uzbl.formfiller = {

    getFrameList: function() {
        var frame = window;
        if (arguments.length > 0) {
            frame = arguments[0];
        }
        var frameList = [frame];

        for (var i = 0; i < frame.frames.length; i++) {
            frameList = frameList.concat(this.getFrameList(frame.frames[i]))
        }

        return frameList;
    },

    getHrefList: function() {
        var frameList = this.getFrameList();
        var hrefList = [];
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
            var formList = frame.document.getElementsByTagName('form');
            if (!formList.length) continue;
            var formDataList = [];
            for (var j = 0; j < formList.length; j++) {
                var form = formList[j];
                var formData = {'elements': []}
                try {
                    formData.name = form.name;
                } catch (e) { /* unnamed form not an error */ }
                for(var k = 0; k < form.elements.length; k++) {
                    var element = form.elements[k];
                    try {
                        elementData = {name: element.name, type: element.type, 
                                       value: element.value};
                        if (['checkbox', 'radio'].indexOf(element.type) > -1) {
                            elementData.checked = element.checked;
                        }
                        formData.elements.push(elementData)
                    } catch (e) { /* cannot capture unnamed elements */ }
                }
                formDataList.push(formData)
            }
            formDataListPageDict[frame.location.href] = formDataList;
        }
        return formDataListPageDict;
    },

    updateForms: function(formDataListPageDict) {
        var frameList = this.getFrameList();

        for (var i = 0; i < frameList.length; i++) {
            var frame = frameList[i];
            var formDataList = 
                formDataListPageDict[frame.location.href];
            try {
                formList = frame.document.getElementsByTagName('form');
                for (var j = 0; 
                     j < formList.length && j < formDataList.length; 
                     j++) 
                {
                    var form = formList[j];
                    var formData = formDataList[j];
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
