var kblayersubscription = { 
    var: {
        layersubscription_data_url: '/api/catalogue/layers/subscriptions/',
        layersubscription_date_format: "dd/mm/yyyy",
    },
    init_dashboard: function() { 

        $('#subscription-subscribed-from').datepicker({ 
            dateFormat: kblayersubscription.var.layersubscription_date_format, 
            format: kblayersubscription.var.layersubscription_date_format,
        });
        $('#subscription-subscribed-to').datepicker({  
            dateFormat: kblayersubscription.var.layersubscription_date_format, 
            format: kblayersubscription.var.layersubscription_date_format,
        });

        $( "#subscription-filter-btn" ).click(function() {
            kblayersubscription.get_layer_subscription();
        });
        $( "#subscription-limit" ).change(function() {
            common_pagination.var.current_page=0;
            kblayersubscription.get_layer_subscription();
        });
        $( "#subscription-order-by" ).change(function() {
            common_pagination.var.current_page=0;
            kblayersubscription.get_layer_subscription();
        });
        $( "#subscription-new-btn" ).click(function() {
            kblayersubscription.show_new_subsctiption_modal();
        });

        kblayersubscription.get_layer_subscription();
    },
    get_layer_subscription: function(param_str){
        if(!param_str){
            params = {
                status:                 $('#layer-submission-status').val(),
                limit:                  $('#layer-submission-limit').val(),
                order_by:               $('#layer-submission-order-by').val(),
                catalogue_entry__name__icontains:  $('#layer-submission-name').val(),
                //custodian
                //status
                subscribed_after:        utils.convert_date_format($('#subscription-subscribed-from').val(), kblayersubscription.var.layersubscription_date_format, hh="00", mm="00", ss="00"),
                subscribed_before:       utils.convert_date_format($('#subscription-subscribed-to').val(), kblayersubscription.var.layersubscription_date_format,hh="23", mm="59", ss="59"),
                //assigned_to
                //description
                //number(id)
            }
            
            params_str = utils.make_query_params(params);
        }

        $.ajax({
            url: kblayersubscription.var.layersubscription_data_url+params_str,
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                if(!response || !response.results){
                    table.message_tbody("No results found");
                    return;
                }
                // for(let i in response.results){
                //     response.results[i]['when'] = utils.convert_datetime_format(response.results[i].when, kbcatalogue_detail.var.catalogue_table_date_format); 
                // }
                // table.set_tbody($('#subscription-tbody'), response.results, [{id:"text"}, {name:'text'}, {url:'text'}]);
                common_pagination.init(response.count, params, kblayersubscription.get_layer_subscription, $('#subscription-navi'));
            },
            error: function (error){
                common_entity_modal.show_error_modal(error);
            }
        });
    },
    show_new_subsctiption_modal: function(){
        common_entity_modal.init("New Layer Subscription", "submit");

        let workspace_id = common_entity_modal.add_field(label="Workspace", type="text");    //??
        let source_name_id = common_entity_modal.add_field(label="Source Name", type="text", value="catalogue.name", option_map=null, disabled=true);    //catalogue.name
        let enabled_id = common_entity_modal.add_field(label="Enabled", type="switch");
        let auto_disable_id = common_entity_modal.add_field(label="Auto disable on connection failure", type="switch");
        let capabilities_url_id = common_entity_modal.add_field(label="capabilities URL", type="text");
        let user_name_id = common_entity_modal.add_field(label="User Name", type="text");
        let user_password_id = common_entity_modal.add_field(label="User Password", type="password");

        // common_entity_modal.add_callbacks(submit_callback=(success_callback, error_callback)=> 
        //                     kbcatalogue_detail.create_communication_log(success_callback, error_callback, type_id, to_id, cc_id, from_id, subject_id, text_id));
        common_entity_modal.show();

    }
}
