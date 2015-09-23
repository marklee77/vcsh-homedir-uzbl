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
                if (form.name) formData.name = form.name;
                for(var k = 0; k < form.elements.length; k++) {
                    var element = form.elements[k];
                    if (!element.name) continue; // do not capture unnamed
                    elementData = {name: element.name, type: element.type, 
                                   value: element.value};
                    if (['checkbox', 'radio'].indexOf(element.type) > -1) {
                        elementData.checked = element.checked;
                    }
                    formData.elements.push(elementData)
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
            var formList = frame.document.getElementsByTagName('form');
            try {
                var formDataList = formDataListPageDict[frame.location.href];
                for (var j = 0; 
                     j < formList.length && j < formDataList.length; 
                     j++)
                {
                    var form = formList[j];
                    var formData = formDataList[j];
                    try {
                        for (var k = 0; j < formData.elements.length; k++) {
                            var elData = formData.elements[k];
                            var el = form.elements[elData.name];
                            if (['checkbox', 'radio'].indexOf(elData.type) > -1) 
                            {
                                // if element is a singleton rather than a 
                                // collection, then wrap it in an array.
                                if (!el.length) el = [el];
                                for (l = 0; l < el.length; l++) {
                                    if (el[l].value == elData.value) {
                                        el[l].checked = elData.checked;
                                    }
                                }
                            } else {
                                // if element is collection, get first
                                if (el.length) el = el[0];
                                el.value = elData.value;
                            }
                        }
                    } catch (e) { /* problem with formData.elements */ }
                }
            } catch (e) { /* did not get proper formDataList */ }
        }
    },
}
