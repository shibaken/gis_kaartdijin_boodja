var kblayersubscription = { 
    var: {
        layersubscription_data_url: '/api/catalogue/layers/subscriptions/',
        layersubscription_date_format: "dd/mm/yyyy",
        publish_workspace_url: '/api/publish/workspaces/',
        subscription_table_date_format: "DD MMM YYYY HH:mm:ss",
        workspace_map: {}, // will be filled later
        subscription_type_map: {1:"WMS", 2:"WFS"},
    },
    init_dashboard: function() { 

        $('#subscription-updated-from').datepicker({ 
            dateFormat: kblayersubscription.var.layersubscription_date_format, 
            format: kblayersubscription.var.layersubscription_date_format,
        });
        $('#subscription-updated-to').datepicker({  
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

        kblayersubscription.get_workspace(kblayersubscription.get_layer_subscription);
    },
    get_layer_subscription: function(param_str){
        if(!param_str){
            params = {
                status:                 $('#layer-submission-status').val(),
                limit:                  $('#subscription-limit').val(),
                order_by:               $('#subscription-order-by').val(),
                catalogue_entry__name__icontains:  $('#subscription-name').val(),
                //custodian
                //status
                updated_after:        utils.convert_date_format($('#subscription-updated-from').val(), kblayersubscription.var.layersubscription_date_format, hh="00", mm="00", ss="00"),
                updated_before:       utils.convert_date_format($('#subscription-updated-to').val(), kblayersubscription.var.layersubscription_date_format,hh="23", mm="59", ss="59"),
                //assigned_to
                //description
                //number(id)
            }
            
            param_str = utils.make_query_params(params);
        }

        $.ajax({
            url: kblayersubscription.var.layersubscription_data_url+"?"+param_str,
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                if(!response || !response.results){
                    table.message_tbody("No results found");
                    return;
                }
                for(let i in response.results){
                    response.results[i]['created_at'] = utils.convert_datetime_format(response.results[i].created_at, kblayersubscription.var.subscription_table_date_format);
                    response.results[i]['type_str'] = kblayersubscription.var.subscription_type_map[+response.results[i].type];
                    response.results[i]['workspace_str'] = kblayersubscription.var.workspace_map[+response.results[i].type];
                }
                table.set_tbody($('#subscription-tbody'), response.results, 
                                [{id:"text"}, {name:'text'}, {description:'text'}, {workspace_str:'text'}, 
                                {type_str:'text'}, {enabled:'text'}, {created_at:'text'}],
                                buttons={View:(att)=>kblayersubscription.get_layer_subscription(),
                                         History:(att)=>kblayersubscription.get_layer_subscription()});
                common_pagination.init(response.count, params, kblayersubscription.get_layer_subscription, $('#subscription-navi'));
            },
            error: function (error){
                common_entity_modal.show_error_modal(error);
            }
        });
    },
    get_workspace: function(callback){
        $.ajax({
            url: kblayersubscription.var.publish_workspace_url,
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                if(!response || !response.results){
                    common_entity_modal.show_alert("Error occured while getting workspaces");
                    return;
                }
                for(let i in response.results){
                    kblayersubscription.var.workspace_map[response.results[i].id] = response.results[i].name; 
                    // response.results[i]['when'] = utils.convert_datetime_format(response.results[i].when, kbcatalogue_detail.var.catalogue_table_date_format); 
                }
                $('#layer-subscription-workspace').empty();
                $('#layer-subscription-workspace').append($('<option>', {
                    value: null,
                    text: "All"
                }));
                for(let key in kblayersubscription.var.workspace_map){
                    let option=$('<option>', {
                        value: key,
                        text: kblayersubscription.var.workspace_map[key]
                    });
                    $('#layer-subscription-workspace').append(option);
                }
                if(callback()){
                    callback();
                }
            },
            error: function (error){
                common_entity_modal.show_error_modal(error);
            }
        });
    },
    show_new_subsctiption_modal: function(){
        common_entity_modal.init("New Layer Subscription", "submit");

        let type_id = common_entity_modal.add_field(label="Type", type="select", value=1, option_map={1:'WMS', 2:'WFS'});    //publish workspace
        let workspace_id = common_entity_modal.add_field(label="Workspace", type="select", value=null, option_map=kblayersubscription.var.workspace_map);    //publish workspace
        let name_id = common_entity_modal.add_field(label="Name", type="text", );
        let description_id = common_entity_modal.add_field(label="Description", type="text_area", );
        let enabled_id = common_entity_modal.add_field(label="Enabled", type="switch");
        // let auto_disable_id = common_entity_modal.add_field(label="Auto disable on connection failure", type="switch");
        let capabilities_url_id = common_entity_modal.add_field(label="capabilities URL", type="text");
        let user_name_id = common_entity_modal.add_field(label="User Name", type="text");
        let user_password_id = common_entity_modal.add_field(label="User Password", type="password");
        let connection_timeout_id = common_entity_modal.add_field(label="Connection Timeout(ms)", type="number");
        let max_concurrent_connections_id = common_entity_modal.add_field(label="Max Concurrent Connections", type="number");
        let read_timeout_id = common_entity_modal.add_field(label="Read Timeout(ms)", type="number");

        $('#'+type_id).change(function(){
            common_entity_modal.hide_entity(max_concurrent_connections_id);
            common_entity_modal.hide_entity(read_timeout_id);
            if($('#'+type_id).val() == 1){  //WMS
                common_entity_modal.show_entity(max_concurrent_connections_id);
                common_entity_modal.show_entity(read_timeout_id);
            }
        })

        common_entity_modal.add_callbacks(submit_callback=(success_callback, error_callback)=> 
                kblayersubscription.create_subscription(success_callback, error_callback, 
                                                        type_id, workspace_id, name_id, description_id, enabled_id, 
                                                        capabilities_url_id, user_name_id, user_password_id,
                                                        connection_timeout_id, max_concurrent_connections_id, 
                                                        read_timeout_id),
                success_callback=()=>table.refresh(kblayersubscription.get_layer_subscription));
        common_entity_modal.show();
    },
    create_subscription: function(success_callback, error_callback, 
                                    type_id, workspace_id, name_id, description_id, enabled_id, 
                                    capabilities_url_id, user_name_id, user_password_id,
                                    connection_timeout_id, max_concurrent_connections_id, 
                                    read_timeout_id){
        
        const type = utils.validate_empty_input('type', $('#'+type_id).val());
        const workspace = utils.validate_empty_input('workspace', $('#'+workspace_id).val());
        // const catalogue = utils.validate_empty_input('catalogue', $('#'+catalogue_id).val());
        const name = utils.validate_empty_input('name', $('#'+name_id).val());
        const description = utils.validate_empty_input('description', $('#'+description_id).val());
        const enabled = utils.validate_empty_input('enabled', $('#'+enabled_id).val());
        // const auto_disable = utils.validate_empty_input('auto_disable', $('#'+auto_disable_id).val());
        const capabilities_url = utils.validate_empty_input('capabilities_url', $('#'+capabilities_url_id).val());
        const username = utils.validate_empty_input('user_name', $('#'+user_name_id).val());
        const userpassword = utils.validate_empty_input('user_password', $('#'+user_password_id).val());
        const connection_timeout = utils.validate_empty_input('connection_timeout', $('#'+connection_timeout_id).val());
        let max_connections = null;
        let read_timeout = null;
        if(type == 1){  //WMS
            max_connections = utils.validate_empty_input('max_concurrent_connections', $('#'+max_concurrent_connections_id).val()); 
            read_timeout = utils.validate_empty_input('read_timeout', $('#'+read_timeout_id).val());
        }
        
        // make data body
        var subscription_data = {
            type:type,
            workspace:workspace,
            name:name,
            description:description,
            enabled:enabled,
            url:capabilities_url,
            username:username,
            userpassword:userpassword,
            connection_timeout: connection_timeout,
            max_connections: max_connections,
            read_timeout: read_timeout
        };
        var url = kblayersubscription.var.layersubscription_data_url;
        var method = 'POST';

        // call POST API
        $.ajax({
            url: url,
            method: method,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            data: JSON.stringify(subscription_data),
            success: success_callback,
            error: error_callback
        });
    }
}
