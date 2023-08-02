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
                'username', 'userpassword', 'connection_timeout', 'max_connections', 'read_timeout'],
            2:['type', 'workspace', 'name', 'description', 'enabled', 'url', 
                'username', 'userpassword', 'connection_timeout',],
            3:['type', 'workspace', 'name', 'description', 'enabled', 'host', 'port', 
                'database', 'schema', 'username', 'userpassword', 'connection_timeout', 
                'max_connections', 'min_connections', 'fetch_size']},
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
                    response.results[i]['status_str'] = kblayersubscription.var.status_map[+response.results[i].status];
                }
                // ID, Name, Status, Type, Workspace, Enabled, URL, Updated at, Assigned to
                table.set_tbody($('#subscription-tbody'), response.results, 
                                [{id:"text"}, {name:'text'}, {status_str:'text'}, {type_str:'text'},
                                {workspace_str:'text'}, {enabled:'text'}, {created_at:'text'}, {assigned_to:'text'}],
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
                    table.message_tbody("No results found");
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
                    table.message_tbody("No results found");
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
                update_subscription_data[key] = utils.validate_empty_input(key, $('#'+id).val());
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
                    window.open("#");
                } else if (mode == "save-and-exit"){
                    window.open("/layer/subscriptions/");
                }
            },
            error: error => common_entity_modal.show_error_modal(error)
        });
    }
}
