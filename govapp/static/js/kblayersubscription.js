var kblayersubscription = { 
    var: {
        layersubscription_data_url: '/api/catalogue/layers/subscriptions/',
        layersubscription_date_format: "dd/mm/yyyy",
        publish_workspace_url: '/api/publish/workspaces/',
        subscription_table_date_format: "DD MMM YYYY HH:mm:ss",
        workspace_map: {}, // will be filled later
        subscription_type_map: {1:"WMS", 2:"WFS", 3:"POST GIS"},
        required_fields:{
            1:['type', 'workspace', 'name', 'description', 'enabled', 'url', 
                'username', 'userpassword', 'connection_timeout', 'max_connections', 'read_timeout'],
            2:['type', 'workspace', 'name', 'description', 'enabled', 'url', 
                'username', 'userpassword', 'connection_timeout',],
            3:['type', 'workspace', 'name', 'description', 'enabled', 'host', 'port', 
                'database', 'schema', 'username', 'userpassword', 'connection_timeout', 
                'max_connections', 'min_connections', 'fetch_size']},
        default_connection_timout: 30000,
        default_read_timout: 30000,
        default_max_concurrent_connections: 6,
        default_mim_concurrent_connections: 1,
        default_fetch_size: 1000,
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

        utils.enter_keyup($('#subscription-name'), kblayersubscription.get_layer_subscription);
        utils.enter_keyup($('#subscription-description'), kblayersubscription.get_layer_subscription);
        utils.enter_keyup($('#subscription-number'), kblayersubscription.get_layer_subscription);

        kblayersubscription.get_workspace(kblayersubscription.get_layer_subscription);
    },
    get_layer_subscription: function(param_str){
        if(!param_str){
            params = {
                limit:      $('#subscription-limit').val(),
                order_by:   $('#subscription-order-by').val(),
                
                catalogue_entry__name__icontains:  $('#subscription-name').val(),
                workspace:  $('#subscription-workspace').val(),
                enabled:    $('#subscription-enabled').val(),
                updated_after:  utils.convert_date_format($('#subscription-updated-from').val(), kblayersubscription.var.layersubscription_date_format, hh="00", mm="00", ss="00"),
                updated_before: utils.convert_date_format($('#subscription-updated-to').val(), kblayersubscription.var.layersubscription_date_format,hh="23", mm="59", ss="59"),
                type:       $('#subscription-type').val(),
                catalogue_entry__description__icontains:  $('#subscription-description').val(),
                id:         $('#subscription-number').val(),
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
                    response.results[i]['workspace_str'] = kblayersubscription.var.workspace_map[+response.results[i].workspace];
                }
                table.set_tbody($('#subscription-tbody'), response.results, 
                                [{id:"text"}, {name:'text'}, {description:'text'}, {workspace_str:'text'}, 
                                {type_str:'text'}, {enabled:'text'}, {created_at:'text'}],
                                buttons={View:(att)=>window.location.href = '/layer/subscriptions/'+att.id+'/',
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
                if(callback){
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

        fields = {};
        fields.type = {id:common_entity_modal.add_field(label="Type", type="select", value=1, option_map=kblayersubscription.var.subscription_type_map)};    //publish workspace
        fields.workspace = {id:common_entity_modal.add_field(label="Workspace", type="select", value=null, option_map=kblayersubscription.var.workspace_map)};    //publish workspace
        fields.name = {id:common_entity_modal.add_field(label="Name", type="text")};
        fields.description = {id:common_entity_modal.add_field(label="Description", type="text_area")};
        fields.enabled = {id:common_entity_modal.add_field(label="Enabled", type="switch")};
        fields.url = {id:common_entity_modal.add_field(label="capabilities URL", type="text")};
        fields.host = {id:common_entity_modal.add_field(label="Host", type="text")};
        fields.port = {id:common_entity_modal.add_field(label="Port", type="number")};
        fields.database = {id:common_entity_modal.add_field(label="Database", type="text")};
        fields.schema = {id:common_entity_modal.add_field(label="Schema", type="text")};
        fields.username = {id:common_entity_modal.add_field(label="User Name", type="text")};
        fields.userpassword = {id:common_entity_modal.add_field(label="User Password", type="password")};
        fields.connection_timeout = {id:common_entity_modal.add_field(label="Connection Timeout(ms)", type="number", value=kblayersubscription.var.default_connection_timout)};
        fields.max_connections = {id:common_entity_modal.add_field(label="Max Concurrent Connections", type="number", value=kblayersubscription.var.default_max_concurrent_connections)};
        fields.min_connections = {id:common_entity_modal.add_field(label="Min Concurrent Connections", type="number", value=kblayersubscription.var.default_mim_concurrent_connections)};
        fields.read_timeout = {id:common_entity_modal.add_field(label="Read Timeout(ms)", type="number", value=kblayersubscription.var.default_read_timout)};
        fields.fetch_size = {id:common_entity_modal.add_field(label="Fetch Size", type="number", value=kblayersubscription.var.default_fetch_size)};

        set_entities = function(type){
            for(let key in fields){
                common_entity_modal.hide_entity(fields[key].id);
            }
            
            const required_fields = kblayersubscription.var.required_fields[type];
            for(let i in required_fields){
                common_entity_modal.show_entity(fields[required_fields[i]].id);
            }
        }
        
        set_entities(1); //WMS

        // change feilds by type change
        $('#'+fields.type.id).change(function(){
            const type = $('#'+fields.type.id).val();
            set_entities(type);
        });

        common_entity_modal.add_callbacks(
                submit_callback=(success_callback, error_callback)=> kblayersubscription.create_subscription(success_callback, error_callback, fields),
                success_callback=()=>table.refresh(kblayersubscription.get_layer_subscription));
        common_entity_modal.show();
    },
    create_subscription: function(success_callback, error_callback, fields){
        const type = $('#'+fields.type.id).val();
        var subscription_data = {};
        required_fields = kblayersubscription.var.required_fields[type];
        for(let i in required_fields){
            const key = required_fields[i];
            if(key == 'enabled'){
                subscription_data[key] = $('#'+fields[key].id).prop('checked');
            } else {
                subscription_data[key] = utils.validate_empty_input(common_entity_modal.get_label(fields[key].id), $('#'+fields[key].id).val());
            }
        }
        
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
    },

    // *** View page *** //
    init_subscription_item: function(){
        $( "#subscription-btn-save" ).click(function() {
            console.log("Save Publish Table");
            kblayersubscription.save_subscription('save');
        });
        $( "#subscription-btn-save-exit" ).click(function() {
            console.log("Save Publish Table");
            kbpublish.save_publish('save-and-exit');
        });       
        $( "#publish-lock" ).click(function() {
            console.log("Locking");
            kbpublish.change_publish_status('lock');
        });
        $( "#publish-unlock" ).click(function() {
            console.log("Unlocking");
            kbpublish.change_publish_status('unlock');
        });
        $( "#publish-assigned-to-btn" ).click(function() {
            console.log("Assign To");
            kbpublish.set_assigned_to();
        });             
        $( "#publish-new-geoserver-btn" ).click(function() {
            console.log("New Geoserver");              
            $('#new-publish-spatial-format').removeAttr('disabled');
            $('#new-publish-frequency-type').removeAttr('disabled');
            $('#new-publish-workspace').removeAttr('disabled');  
                        
            $('#new-publish-spatial-format').val('');
            $('#new-publish-frequency-type').val('');
            $('#new-publish-workspace').val('');             

            $('#PublishNewGeoserverModal').modal('show');
        });      
        $( "#publish-new-cddp-btn" ).click(function() {
            console.log("New CDDP");  
            $('#new-publish-cddp-spatial-format').removeAttr('disabled');
            $('#new-publish-cddp-frequency-type').removeAttr('disabled');
            $('#new-publish-cddp-spatial-mode').removeAttr('disabled');  
            $('#new-publish-cddp-path').removeAttr('disabled'); 

            $('#new-publish-cddp-spatial-format').val('');
            $('#new-publish-cddp-frequency-type').val('');
            $('#new-publish-cddp-spatial-mode').val('');
            $('#new-publish-cddp-path').val(''); 
           
            $('#PublishNewCDDPModal').modal('show');
        });            

        $( "#create-publish-geoserver-btn" ).click(function() {
            console.log("Create new geoserver");             
            kbpublish.create_publish_geoserver();
        });

        $( "#create-publish-cddp-btn" ).click(function() {
            console.log("Create new CDDP");

            kbpublish.create_publish_cddp();
        });
        
        var has_edit_access = $('#has_edit_access').val();
        if (has_edit_access == 'True') {
            kbpublish.var.has_edit_access = true;
        }

        $('#publish-btn-add-notification').click(function(){
            kbpublish.show_add_email_notification_modal();
        })

        $('#publish-notification-order-by').change(()=>table.refresh(this.get_email_notification));
        $('#publish-notification-limit').change(()=>table.refresh(this.get_email_notification));

        const publish_workspace_list = $('#publish_workspace_list').data('list');
        if(!publish_workspace_list && typeof publish_workspace_list == 'string' && publish_workspace_list.length > 0){
            this.var.publish_workspace_list = JSON.parse(publish_workspace_list.replaceAll("'", '"'));
        } else if(publish_workspace_list instanceof Array){
            this.var.publish_workspace_list = publish_workspace_list
        }
        if(this.var.publish_workspace_list){
            for(let i in this.var.publish_workspace_list){
                let entry = this.var.publish_workspace_list[i];
                this.var.publish_workspace_map[entry.id] = entry.name;
            }
        }

        $("#log_actions_show").click(kbpublish.show_action_log);
        $("#log_communication_show").click(kbpublish.show_communication_log);
        $("#log_communication_add").click(kbpublish.add_communication_log);
        

        $('#manage-editors-search').select2({
            placeholder: 'Select an option',
            minimumInputLength: 2,
            allowClear: true,
            dropdownParent: $('#ManageEditorsModal'),
            width: $( this ).data( 'width' ) ? $( this ).data( 'width' ) : $( this ).hasClass( 'w-100' ) ? '100%' : 'style',
            theme: 'bootstrap-5',
            ajax: {
                url: "/api/accounts/users/",
                dataType: 'json',
                quietMillis: 100,
                data: function (params, page) {
                    return {
                        q: params.term,                        
                    };
                },          
                  processResults: function (data) {
                    // Transforms the top-level key of the response object from 'items' to 'results'
                    var results = [];
                    $.each(data.results, function(index, item){
                      results.push({
                        id: item.id,
                        text: item.first_name+' '+item.last_name
                      });
                    });
                    return {
                        results: results
                    };
                  }                  
            },
        });

        $('#manage-editors-add-btn').click(function(e){
            kbpublish.add_publish_editor($('#manage-editors-search').val());
        });

        kbpublish.get_publish_geoservers();
        kbpublish.get_publish_cddp();
        kbpublish.retrieve_communication_types();
        // this.retrieve_noti_types(()=>table.refresh(this.get_email_notification));
    }
}
