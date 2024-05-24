var kbcddpweb = { 
    var: {
        cddpqueue_list:"/api/publish/cddp-contents/"
    },
    init_dashboard: function() { 
        $( "#cddp-queue-limit" ).change(function() {
            common_pagination.var.current_page=0;
            kbcddpweb.get_cddpqueue();
        });

        kbcddpweb.get_cddpqueue();
    },
    get_cddpqueue: function(params_str){
        if (!params_str){
            params = {
                limit: $('#cddp-queue-limit').val(),
            }

            params_str = utils.make_query_params(params);
        }

        const tbody = $('#cddp-queue-tbody');
        let url = kbcddpweb.var.cddpqueue_list;
        url += "?limit="+$('#cddp-queue-limit').val();
        url += "&offset="+0; 
        
        $.ajax({
            url: kbcddpweb.var.cddpqueue_list+"?"+params_str,
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            success: (response) => {
                console.log({response})
                for(let i in response.results){
                    if(response.results[i].status == 'FAILED') response.results[i].success = false;
                    else if(response.results[i].status == 'PUBLISHED') response.results[i].success = true;
                    else response.results[i].success = null;
                }

                // table.set_tbody(tbody, response.results, [
                table.set_tbody(tbody, response, [
                    {filepath:"text"}, 
                    {created_at:'text'},
                    {size_kb:'text'}
                ]);
                if(response.results == 0){
                    table.message_tbody(tbody, "No results found");
                }
                common_pagination.init(response.count, params, kbcddpweb.get_cddpqueue, $('#paging_navi'));
            },
            error: (error)=> {
                table.message_tbody(tbody, "No results found");
                common_entity_modal.show_alert("An error occured while getting cddp queue.");
            },
        });
    },
}
