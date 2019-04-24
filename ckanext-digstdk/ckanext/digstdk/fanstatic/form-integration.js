function buildQueryStr(list, element){
    var subjects = {};

    if (list && list.trim() !== "" && list.trim().length > 1) {
        list = list.slice(1, -1);
        if (element)
            element.val(list);
        $(list.split(",")).each(function () {
            subjects[this] = this;
        });
    }

    var queryStr = "/forms-search/solr/mycore/select?q=exactID_s:(";
    $.each(subjects, function(id, text) {
        queryStr += id+"%20";
    });
    queryStr += ")"

    return { queryStr: queryStr, subjects: subjects };
}

$(document).ready(function() {
    $('.js-example-basic-multiple').select2({
        placeholder: "Search for a FORM code",
        minimumInputLength: 1,
        multiple: true,
        ajax: {
            url: '/forms-search/solr/mycore/select',
            data: function (term, page) {
                var normalizedTerm=term.replace(/ /g,"\\ ");
                var queryStr="text_s:*"+normalizedTerm+"*"+" OR id:"+normalizedTerm+"*"+" OR exactID_s:"+normalizedTerm;
                var query = {
                    q: queryStr,
                }

                return query;
            },
            results: function (data, page) {
                var items = data.response.docs;
                var results = [];
                for (let i=0; i<items.length; i++) {
                    results.push({id: "\""+items[i].id+"\"", text: items[i].id+" - "+items[i].text_s});
                }
                return { results: results}
            },
            cache: true
        },
        initSelection : function (element, callback) {
            var list = element.val();

            var res = buildQueryStr(list, element);
            var queryStr = res.queryStr;
            var subjects = res.subjects;

            $.ajax(queryStr, { dataType: "json" }).done(function(searchResult) {
                var items = searchResult.response.docs;
                for (let i=0; i<items.length; i++) {
                    subjects["\""+items[i].id+"\""] = items[i].text_s;
                }
                var data = [];
                $.each(subjects, function(id, text) {
                    data.push({id: id, text: id.slice(1,-1)+" - "+text});
                });
                callback(data);
            });
        }
    });



    var tagWithFormCodes=$("th:contains('Opgave')").next();
    if (tagWithFormCodes) {
        var queryStr = buildQueryStr(tagWithFormCodes.text()).queryStr;

        enhancedText = "";
        $.ajax(queryStr, { dataType: "json" }).done(function(searchResult) {
            items = searchResult.response.docs;

            for (let i=0; i<items.length; i++) {
                enhancedText += items[i].id + " - " + items[i].text_s + "<br>"
            }

            tagWithFormCodes.text("");
            tagWithFormCodes.append(enhancedText);
        });
    }
});

