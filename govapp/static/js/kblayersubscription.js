var kblayersubscription = { 
    var: {
        layersubscription_data_url: '/api/catalogue/layers/subscriptions/',
        layersubscription_date_format: "dd/mm/yyyy",
        publish_workspace_url: '/api/publish/workspaces/',
        subscription_table_date_format: "DD MMM YYYY HH:mm:ss",
        workspace_map: {}, // will be filled later
        subscription_type_map: {1:"WMS", 2:"WFS", 3:"POST GIS"},
        status_map: {1:"NEW DRAFT", 2:"LOCKED", 3:"DECLINED", 4:"DRAFT", 5:"PENDING"},
        required_fields:{
            1:['type', 'workspace', 'name', 'description', 'enabled', 'url', 
                'connection_timeout', 'max_connections', 'read_timeout'],
            2:['type', 'workspace', 'name', 'description', 'enabled', 'url', 
                'connection_timeout',],
            3:['type', 'workspace', 'name', 'description', 'enabled', 'host', 'port', 
                'database', 'schema', 'connection_timeout', 
                'max_connections', 'min_connections', 'fetch_size']},
        optional_fields:['username', 'userpassword'],
        default_connection_timout: 10000,
        default_read_timout: 10000,
        default_max_concurrent_connections: 6,
        default_mim_concurrent_connections: 1,
        default_fetch_size: 1000,

        // for view  page
        subscription_save_url: '/api/catalogue/layers/subscriptions/',
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

        $('#subscription-assignedto').select2({
            placeholder: 'Select an option',
            minimumInputLength: 2,
            allowClear: true,
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
                enabled:    $('#subscription-enabled').prop('checked'),
                updated_after:  utils.convert_date_format($('#subscription-updated-from').val(), kblayersubscription.var.layersubscription_date_format, hh="00", mm="00", ss="00"),
                updated_before: utils.convert_date_format($('#subscription-updated-to').val(), kblayersubscription.var.layersubscription_date_format,hh="23", mm="59", ss="59"),
                type:       $('#subscription-type').val(),
                catalogue_entry__description__icontains:  $('#subscription-description').val(),
                id:         $('#subscription-number').val(),
                assigned_to:            +$('#subscription-assignedto').val(),
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
                    table.message_tbody($('#subscription-tbody'), "No results found");
                    return;
                }
                for(let i in response.results){
                    response.results[i]['created_at'] = utils.convert_datetime_format(response.results[i].created_at, kblayersubscription.var.subscription_table_date_format);
                    response.results[i]['type_str'] = kblayersubscription.var.subscription_type_map[+response.results[i].type];
                    response.results[i]['workspace_str'] = kblayersubscription.var.workspace_map[+response.results[i].workspace];
                    response.results[i]['status_str'] = kblayersubscription.var.status_map[+response.results[i].status];
                    response.results[i]['assigned_to_name'] = null;
                    if(response.results[i]['assigned_to_first_name'])
                        response.results[i]['assigned_to_name'] = response.results[i]['assigned_to_first_name'] + ' ' 
                                                                + response.results[i]['assigned_to_last_name'];
                    
                }
                // ID, Name, Status, Type, Workspace, Enabled, URL, Updated at, Assigned to
                buttons={View:(subscription)=>window.location.href = '/layer/subscriptions/'+subscription.id+'/',
                                         History:(subscription)=>kblayersubscription.get_layer_subscription()};
                if($('#is-administrator').val() == "True"){
                    buttons['Delete']=(subscription)=>kblayersubscription.delete_subscription(subscription);
                }
                table.set_tbody($('#subscription-tbody'), response.results, 
                                [{id:"text"}, {name:'text'}, {status_str:'text'}, {type_str:'text'},
                                {workspace_str:'text'}, {enabled:'text'}, {updated_at:'text'}, {assigned_to_name:'text'}],
                                buttons=buttons);
                common_pagination.init(response.count, params, kblayersubscription.get_layer_subscription, $('#subscription-navi'));
            },
            error: function (error){
                common_entity_modal.show_alert("An error occured while getting layer subscription.");
                console.log(error)
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
                common_entity_modal.show_alert("An error occured while getting workspace.");
                console.log(error);
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
        fields.username = {id:common_entity_modal.add_field(label="User Name(Optional)", type="text")};
        fields.userpassword = {id:common_entity_modal.add_field(label="User Password(Optional)", type="password")};
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

            const optional_fields = kblayersubscription.var.optional_fields;
            for(let i in optional_fields){
                common_entity_modal.show_entity(fields[optional_fields[i]].id);
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
                try{
                    subscription_data[key] = utils.validate_empty_input(common_entity_modal.get_label(fields[key].id), $('#'+fields[key].id).val());
                } catch (error){
                    common_entity_modal.show_alert("An error occured while creating a new subscription.");
                    console.log(error)
                    return;
                }
            }
        }
        optional_fields = kblayersubscription.var.optional_fields;
        for(let i in optional_fields){
            const key = optional_fields[i];
            const val = $('#'+fields[key].id).val();
            if(val){
                subscription_data[key] = val;
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
    delete_subscription: function(subscription){
        let delete_subscription_callback = function(success_callback, error_callback){
            var url = kblayersubscription.var.layersubscription_data_url+subscription.id+"/";
            var method = 'DELETE';

            // call POST API
            $.ajax({
                url: url,
                method: method,
                dataType: 'json',
                contentType: 'application/json',
                headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
                success: success_callback,
                error: error_callback
            });
        }

        common_entity_modal.init("Delete Subscription", "delete");
        common_entity_modal.add_field(label="ID", type="number", value=subscription.id);
        common_entity_modal.add_field(label="Name", type="text", value=subscription.name);
        common_entity_modal.add_field(label="Type", type="text", value=subscription.type_str);
        common_entity_modal.add_callbacks(submit_callback=(success_callback, error_callback)=> 
                                    delete_subscription_callback(success_callback, error_callback),
                                    success_callback=()=>table.refresh(kblayersubscription.get_layer_subscription));
        common_entity_modal.show();
        
    },

    // *** View page *** //
    init_subscription_item: function(){
        $( "#subscription-lock" ).click(() => kblayersubscription.change_subscription_status('lock'));
        $( "#subscription-unlock" ).click(() => kblayersubscription.change_subscription_status('unlock'));
        $( "#subsctiption-assigned-to-btn" ).click(() =>kblayersubscription.set_assigned_to());
        
        $("#log_actions_show").click(kblayersubscription.show_action_log);
        $("#log_communication_show").click(kblayersubscription.show_communication_log);
        $("#log_communication_add").click(kblayersubscription.add_communication_log);

        $( "#subscription-btn-save" ).click(function() {
            console.log("Save Publish Table");
            kblayersubscription.save_subscription('save');
        });
        $( "#subscription-btn-save-exit" ).click(function() {
            console.log("Save Publish Table");
            kblayersubscription.save_subscription('save-and-exit');
        });
        if([1,2].includes(+$('#subscription-type-num').val())){
            kblayersubscription.get_mappings('layer');
        }else{
            kblayersubscription.get_mappings('table');
        }
        if($('#subscription_enabled').val() == 'True'){
            $('#subscription-enabled').prop('checked', true);
        }
    },
    change_subscription_status: function(status){
        var status_url = "lock";
        if (status == 'unlock') {
            status_url = 'unlock';
        }

        var subscription_id = $('#subscription_id').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();

        $.ajax({
            url: kblayersubscription.var.subscription_save_url+subscription_id+"/"+status_url+"/",
            type: 'POST',
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response) {
                window.location = "/layer/subscriptions/"+subscription_id;
            },
            error: function (error) {
                common_entity_modal.show_alert("ERROR Changing Status");
            },
        });
    },
    set_assigned_to: function(){
        var assignedto = $('#subsctiption-assigned-to').val();
        var subscription_id = $('#subscription_id').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();

        if (assignedto.length > 0) {  
            $.ajax({
                url: kblayersubscription.var.subscription_save_url+subscription_id+"/assign/"+assignedto+"/",
                type: 'POST',
                headers: {'X-CSRFToken' : csrf_token},
                contentType: 'application/json',
                success: function (response) {
                    window.location = "/layer/subscriptions/"+subscription_id;
                },
                error: function (error) {
                    common_entity_modal.show_alert("ERROR Setting assigned person.");
                },
            });
    
            
        } else {
            common_entity_modal.show_alert("Please select an assigned to person first.");

        }
    },
    show_action_log: function(){
        common_entity_modal.init("Action log", "info");
        common_entity_modal.init_talbe();
        let thead = common_entity_modal.get_thead();
        table.set_thead(thead, {Who:3, What:5, When:4});
        common_entity_modal.get_limit().change(()=>kblayersubscription.get_action_log());
        common_entity_modal.get_search().keyup((event)=>{
            if (event.which === 13 || event.keyCode === 13){
                event.preventDefault();
                kblayersubscription.get_action_log()
            }
        });
        common_entity_modal.show();

        kblayersubscription.get_action_log();
    },
    get_action_log: function(params_str){
        if(!params_str){
            params = {
                limit:  common_entity_modal.get_limit().val(),
                search: common_entity_modal.get_search().val(),
            }

            params_str = utils.make_query_params(params);
        }
    
        var subscription_id = $('#subscription_id').val();
        $.ajax({
            url: kblayersubscription.var.subscription_save_url+subscription_id+"/logs/actions/?"+params_str,
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                if(!response || !response.results){
                    table.message_tbody(common_entity_modal.get_tbody(), "No results found");
                    return;
                }
                for(let i in response.results){
                    response.results[i]['when'] = utils.convert_datetime_format(response.results[i].when, kblayersubscription.var.subscription_table_date_format); 
                }
                table.set_tbody(common_entity_modal.get_tbody(), response.results, [{username:"text"}, {what:'text'}, {when:'text'}]);
                common_pagination.init(response.count, params, kblayersubscription.get_action_log, common_entity_modal.get_page_navi());
            },
            error: function (error){
                common_entity_modal.show_error_modal(error);
            }
        });
    },
    show_communication_log: function(){
        common_entity_modal.init("Communication log", "info");
        common_entity_modal.init_talbe();
        let thead = common_entity_modal.get_thead();
        table.set_thead(thead, {User:2, To:2, Cc:2, From:2, Subject:2, Text:2});
        common_entity_modal.get_limit().change(()=>kblayersubscription.get_communication_log());
        common_entity_modal.get_search().keyup((event)=>{
            if (event.which === 13 || event.keyCode === 13){
                event.preventDefault();
                kblayersubscription.get_communication_log()
            }
        });
        common_entity_modal.show();

        kblayersubscription.get_communication_log();
    },
    get_communication_log: function(params_str){
        if(!params_str){
            params = {
                limit:  common_entity_modal.get_limit().val(),
                search: common_entity_modal.get_search().val(),
            }

            params_str = utils.make_query_params(params);
        }
    
        var subscription_id = $('#subscription_id').val();
        $.ajax({
            url: kblayersubscription.var.subscription_save_url+subscription_id+"/logs/communications/?"+params_str,
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                if(!response || !response.results){
                    table.message_tbody(common_entity_modal.get_tbody(), "No results found");
                    return;
                }
                for(let i in response.results){
                    response.results[i]['created_at'] = utils.convert_datetime_format(response.results[i].created_at, kblayersubscription.var.subscription_table_date_format); 
                }
                table.set_tbody(common_entity_modal.get_tbody(), response.results, 
                                [{username:"text"}, {to:'text'}, {cc:'text'}, {from:'text'}, {subject:'text'}, {text:'text'}]);
                common_pagination.init(response.count, params, kblayersubscription.get_communication_log, common_entity_modal.get_page_navi());
            },
            error: function (error){
                common_entity_modal.show_error_modal(error);
            }
        });
    },
    add_communication_log: function(){
        common_entity_modal.init("Add New Communication log", "submit");
        let type_id = common_entity_modal.add_field(label="Communication Type", type="select", value=null, option_map=kbpublish.var.communication_type);
        let to_id = common_entity_modal.add_field(label="To", type="text");
        let cc_id = common_entity_modal.add_field(label="Cc", type="text");
        let from_id = common_entity_modal.add_field(label="From", type="text");
        let subject_id = common_entity_modal.add_field(label="Subject", type="text");
        let text_id = common_entity_modal.add_field(label="Text", type="text_area");

        common_entity_modal.add_callbacks(submit_callback=(success_callback, error_callback)=> 
                                        kblayersubscription.create_communication_log(
                                            success_callback, error_callback, type_id, 
                                            to_id, cc_id, from_id, subject_id, text_id));
        common_entity_modal.show();
    },
    create_communication_log: function(success_callback, error_callback, type_id, to_id, cc_id, from_id, subject_id, text_id){
        // get & validation check
        const type = utils.validate_empty_input('type', $('#'+type_id).val());
        const to = utils.validate_empty_input('to', $('#'+to_id).val());
        const cc = utils.validate_empty_input('cc', $('#'+cc_id).val());
        const from = utils.validate_empty_input('from', $('#'+from_id).val());
        const subject = utils.validate_empty_input('subject', $('#'+subject_id).val());
        const text = utils.validate_empty_input('text', $('#'+text_id).val());
        
        // make data body
        var communication_log_data = {
            type:type,
            to:to,
            cc:cc,
            from:from,
            subject:subject,
            text:text,
            user:$('#current-user').val(),
        };
        
        var subscription_id = $('#subscription_id').val();
        var url = kblayersubscription.var.subscription_save_url+subscription_id+"/logs/communications/";
        var method = 'POST';

        // call POST API
        $.ajax({
            url: url,
            method: method,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            data: JSON.stringify(communication_log_data),
            success: success_callback,
            error: error_callback
        });
    },
    save_subscription: function(mode){
        const type = $('#subscription-type-num').val();
        
        // make data body
        var update_subscription_data = {};
        const fields = kblayersubscription.var.required_fields;
        for( let i in fields[type] ){
            const key = fields[type][i];
            if( key == 'type'){
                continue;
            }
            const id = "subscription-"+key.replaceAll('_', '-');
            if(key == 'enabled'){
                update_subscription_data[key] = $('#'+id).prop('checked');
            } else {
                try{
                    update_subscription_data[key] = utils.validate_empty_input(key, $('#'+id).val());
                } catch (error){
                    common_entity_modal.show_alert(error);
                    return;
                }
            }
        }
        
        let optional_fields = kblayersubscription.var.optional_fields
        for( let i in optional_fields ){
            const key = optional_fields[i];
            const id = "subscription-"+key.replaceAll('_', '-');
            const val = $('#'+id).val();
            if(val){
                update_subscription_data[key] = val;
            }
        }

        var subscription_id = $('#subscription_id').val();
        var url = kblayersubscription.var.subscription_save_url+subscription_id+"/";
        var method = 'PUT';

        // call POST API
        $.ajax({
            url: url,
            method: method,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            data: JSON.stringify(update_subscription_data),
            success: function (response) {
                if(mode == "save"){
                    location.reload();
                } else if (mode == "save-and-exit"){
                    window.location.href = "/layer/subscriptions/";
                }
            },
            error: error => {
                common_entity_modal.show_alert("An error occured while updating a subscription.");
                console.log(error);
            }
        });
    },
    get_mappings: function(type){
        let url = kblayersubscription.var.layersubscription_data_url + $('#subscription_id').val() + "/mapping/";
        let method = 'GET';

        let thead = $("#subscription-layer-table-thead");
        let tbody = $("#subscription-layer-table-tbody");
        let title = "Native Layer";

        if(type == 'table'){
            thead = $("#subscription-dbtable-table-thead");
            tbody = $("#subscription-dbtable-table-tbody");
            title = "Table";
        }

        // call GET API
        $.ajax({
            url: url,
            method: method,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            success: (response) => {
                if(!response || !response.results){
                    table.message_tbody(tbody, "No results found");
                    return;
                }
                let buttons = null;
                if($('#has_edit_access').val() == "True"){
                    buttons={ADD:{callback:(mapping)=>kblayersubscription.show_add_mapping_modal(title, mapping, type), 
                                    is_valid:(mapping)=>!(mapping.name in response.results)},
                            EDIT:{callback:(mapping)=>kblayersubscription.show_edit_mapping_modal(title, mapping, response.results[mapping.name], type), 
                                    is_valid:(mapping)=>mapping.name in response.results}};
                    table.set_thead(thead, {[title+"s"]:5, "Catalogue Name":6, "Action":1});
                } else {
                    table.set_thead(thead, {[title+"s"]:6, "Catalogue Name":6});
                }
                let rows = []
                for(let i in kblayersubscription.var.mapping_names){
                    let mapping = {'name':kblayersubscription.var.mapping_names[i]};
                    mapping.catalogue = "";
                    if(mapping.name in response.results){
                        mapping.catalogue = response.results[mapping.name].name;
                    }
                    rows.push(mapping);
                }
                table.set_tbody(tbody, rows, [{name:"text"}, {catalogue:"text"}], buttons);
            },
            error: (error)=> {
                common_entity_modal.show_alert("An error occured while getting mappings.");
                // console.error(error);
            },
        });
    },
    show_add_mapping_modal: function(title, mapping, subscription_type){
        common_entity_modal.init("New Catalogue Subscription " + title);
        let fields = {}
        fields['name'] = common_entity_modal.add_field(label="Catalogue Entry Name", type="text");
        fields['description'] = common_entity_modal.add_field(label="Description", type="text");
        fields['mapping_name'] = common_entity_modal.add_field(label= title + " Name", type="text", mapping.name, null, true);
        common_entity_modal.add_callbacks(
            submit_callback=(success_callback, error_callback) => kblayersubscription.create_mapping(success_callback, error_callback, fields), 
            success_callback=() => kblayersubscription.get_mappings(subscription_type));
        common_entity_modal.show();
    },
    show_edit_mapping_modal: function(title, mapping, catalogue, subscription_type){
        const catalogue_id = catalogue.catalogue_entry_id;
        common_entity_modal.init("Update Catalogue Subscription " + title);
        let fields = {}
        fields['name'] = common_entity_modal.add_field(label="Catalogue Entry Name", type="text", catalogue.name);
        fields['description'] = common_entity_modal.add_field(label="Description", type="text", catalogue.description);
        fields['mapping_name'] = common_entity_modal.add_field(label=title + " Name", type="text", mapping.name, null, true);
        common_entity_modal.add_callbacks(
            submit_callback=(success_callback, error_callback) => kblayersubscription.update_mapping(success_callback, error_callback, fields, catalogue_id), 
            success_callback=() => kblayersubscription.get_mappings(subscription_type));
        common_entity_modal.show();
    },
    create_mapping: function(success_callback, error_callback, fields){
        // call create layer api via ajax
        mapping_data = {};

        for(const key in fields){
            mapping_data[key] = utils.validate_empty_input(key, $('#'+fields[key]).val());
        }
        
        var url = kblayersubscription.var.layersubscription_data_url + $('#subscription_id').val() + "/mapping/";
        var method = 'POST';

        // call POST API
        $.ajax({
            url: url,
            method: method,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            data: JSON.stringify(mapping_data),
            success: success_callback,
            error: error_callback
        });
    },
    update_mapping: function(success_callback, error_callback, fields, catalogue_id){
        // call update layer api via ajax
        mapping_data = {};

        for(const key in fields){
            mapping_data[key] = utils.validate_empty_input(key, $('#'+fields[key]).val());
        }
        
        var url = kblayersubscription.var.layersubscription_data_url + $('#subscription_id').val() + "/mapping/" + catalogue_id + "/";
        var method = 'PUT';

        // call PUT API
        $.ajax({
            url: url,
            method: method,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            data: JSON.stringify(mapping_data),
            success: success_callback,
            error: error_callback
        });
    },
}
