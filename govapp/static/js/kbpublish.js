var kbpublish = {
    var: {
            publish_data_url: "/api/publish/entries/",
            publish_save_url: "/api/publish/entries/", 
            publish_data_geoserver_url: "/api/publish/channels/geoserver/",
            publish_save_geoserver_url: "/api/publish/channels/geoserver/",
            publish_data_cddp_url: "/api/publish/channels/cddp/",                       
            publish_save_cddp_url: "/api/publish/channels/cddp/",
            publish_email_notification_url: "/api/publish/notifications/emails/",
            publish_email_notification_type_url: "/api/publish/notifications/emails/type/",
            publish_status: {
                1: "Locked",
                2: "Unlocked"
            },
            publish_geoserver_format: {
                1: "WMS",  
                2: "WMS & WFS"
            },
            publish_geoserver_frequency: {
                1: "OnChange"
            },
            publish_workspace_list: [],
            publish_workspace_map: {},
            has_edit_access: false,
            publish_cddp_format: {
                1: "Geopackage",
                2: "Shapefile",
                3: "Geodatabase",
                4: "GeoJSON"
            },
            publish_cddp_mode: {
                1: "Azure",
                2: "Azure and Sharepoint"
            },
            publish_cddp_frequency: {
                1: "OnChange"
            },
            catalogue_entry_list: null,
            catalogue_entry_map: {},
            publish_date_format: "dd/mm/yyyy"
    },
    pagination: kbpublish_pagination,
    init_dashboard: function() {    

        $('#publish-custodian').select2({
            placeholder: 'Select an option',
            minimumInputLength: 2,
            allowClear: true,
            width: $( this ).data( 'width' ) ? $( this ).data( 'width' ) : $( this ).hasClass( 'w-100' ) ? '100%' : 'style',
            theme: 'bootstrap-5',
            ajax: {
                url: "/api/catalogue/custodians/",
                dataType: 'json',
                quietMillis: 100,
                data: function (params, page) {
        
                    return {
                        search: params.term,                        
                    };
                },    
                  processResults: function (data) {
                    // Transforms the top-level key of the response object from 'items' to 'results'
                    var results = [];
                    $.each(data.results, function(index, item){
                      results.push({
                        id: item.id,
                        text: item.name
                      });
                    });
                    return {
                        results: results
                    };
                  }                  
            },
        });

        $('#publish-assignedto').select2({
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


        $('#publish-lastupdatedfrom').datepicker({ dateFormat: this.var.publish_date_format, 
            format: this.var.publish_date_format,
        });
        $('#publish-lastupdatedto').datepicker({  dateFormat: this.var.publish_date_format, 
                format: this.var.publish_date_format,
        });


        $( "#publish-filter-btn" ).click(function() {
            console.log("Reload Publish Table");
            kbpublish.get_publish();
        });
        $( "#publish-new-btn" ).click(function() {
            common_entity_modal.init("New Publish", "submit");
            // let name_id = common_entity_modal.add_field(label="Name", type="text");
            let catalogue_entry_id = common_entity_modal.add_field(label="Catalogue Entry", type="select", value=null, option_map=kbpublish.var.catalogue_entry_map);
            let description_id = common_entity_modal.add_field(label="Description", type="text");
            common_entity_modal.add_callbacks(submit_callback=(success_callback, error_callback)=> 
                                                kbpublish.create_publish(success_callback, error_callback, catalogue_entry_id, description_id),
                                                success_callback=kbpublish.get_publish);
            common_entity_modal.show();
        });           
        $( "#publish-limit" ).change(function(){
            common_pagination.var.current_page=0;
            kbpublish.get_publish();
        })
        $( "#publish-order-by" ).change(function(){
            common_pagination.var.current_page=0;
            kbpublish.get_publish();
        })

        this.var.catalogue_entry_list = JSON.parse($('#catalogue_entry_list').data('list').replaceAll("'", '"'));
        for(let i in this.var.catalogue_entry_list){
            let entry = this.var.catalogue_entry_list[i];
            this.var.catalogue_entry_map[entry.id] = entry.name;
        }
        kbpublish.get_publish();
    },
    init_publish_item: function() {    
        $( "#publish-btn-save" ).click(function() {
            console.log("Save Publish Table");
            kbpublish.save_publish('save');
        });
        $( "#publish-btn-save-exit" ).click(function() {
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
        $( "#publish-manage-editors-btn" ).click(function() {
            console.log("Manage Editors");   
            kbpublish.get_publish_editors();
            $('#ManageEditorsModal').modal('show');
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

        this.var.publish_workspace_list = JSON.parse($('#publish_workspace_list').data('list').replaceAll("'", '"'));
        for(let i in this.var.publish_workspace_list){
            let entry = this.var.publish_workspace_list[i];
            this.var.publish_workspace_map[entry.id] = entry.name;
        }

        kbpublish.get_publish_geoservers();
        kbpublish.get_publish_cddp();
        this.retrieve_noti_types(()=>table.refresh(this.get_email_notification));
    },
    retrieve_noti_types: function(post_callback){
        $.ajax({
            url: kbpublish.var.publish_email_notification_type_url,
            type: 'GET',
            contentType: 'application/json',
            success: (response) => {
                var noti_type = {}
                for(let i in response.results){
                    const type = response.results[i];
                    noti_type[type.id] = type.label;
                }
                kbpublish.var.publish_email_notification_type = noti_type;
                post_callback();
            },
            error: (error)=> {
                alert("An error occured while getting email notification type.");
                console.error(error);
            },
        });
    },
    search_accounts_for_editor: function() { 
        
        
    },
    delete_publish_editor: function(user_id) {        
        var publish_id = $('#publish_id').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();

        $.ajax({
            url: kbpublish.var.publish_save_url+publish_id+"/editors/delete/"+user_id+"/",
            type: 'DELETE',
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response) {
                var html = '';
                console.log(response);
                alert(response);
                if (response != null) {
                    if (response.length > 0) {
                                           
        
                    } else {
        

                    }
                } else {
        
                }

       
            },
            error: function (error) {
                 alert("ERROR");

        
            },
        });


    },
    delete_publish_geoserver: function(geoserver_publish_id) {        
        var publish_id = $('#publish_id').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();

        $.ajax({
            url: kbpublish.var.publish_data_geoserver_url+geoserver_publish_id+"/",
            type: 'DELETE',
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response, status_code) {
                var html = '';
               
                kbpublish.get_publish_geoservers();                    
                

       
            },
            error: function (error) {
                 alert("ERROR");

        
            },
        });


    },
    delete_publish_cddp: function(cddp_publish_id) {        
        var publish_id = $('#publish_id').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();

        $.ajax({
            url: kbpublish.var.publish_save_cddp_url+cddp_publish_id+"/",
            type: 'DELETE',
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response, status_code) {               
                kbpublish.get_publish_cddp();                    
            },
            error: function (error) {
                 alert("ERROR");

        
            },
        });


    },
    set_assigned_to: function() { 
        var publishassignedto = $('#publish-assigned-to').val();
        var publish_id = $('#publish_id').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();

        if (publishassignedto.length > 0) {  
            $.ajax({
                url: kbpublish.var.publish_save_url+publish_id+"/assign/"+publishassignedto+"/",
                type: 'POST',
                headers: {'X-CSRFToken' : csrf_token},
                contentType: 'application/json',
                success: function (response) {
                    var html = '';
                    
                    window.location = "/publish/"+publish_id;
                    
                    
    
           
                },
                error: function (error) {
                     alert("ERROR Setting assigned person.");
    
            
                },
            });
    
            
        } else {
            alert('Please select an assigned to person first.')

        }

    },
    change_publish_status: function(status) {        
        var status_url = "lock";
        if (status == 'unlock') {
            status_url = 'unlock';
        }

        var publish_id = $('#publish_id').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();

        $.ajax({
            url: kbpublish.var.publish_save_url+publish_id+"/"+status_url+"/",
            //method: 'POST',
            type: 'POST',
            //dataType: 'json',
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response) {
                window.location = "/publish/"+publish_id;
       
            },
            error: function (error) {
                 alert("ERROR Changing Status");

        
            },
        });
    },
    create_publish_geoserver: function() {
        var publish_id = $('#publish_id').val();
        var newpublishspatialformat = $('#new-publish-spatial-format').val();
        var newpublishfrequencytype = $('#new-publish-frequency-type').val();
        var newpublishworkspace = $('#new-publish-workspace').val();

        var post_data = {"mode": newpublishspatialformat, "frequency": newpublishfrequencytype, "workspace": newpublishworkspace, "publish_entry": publish_id};
        var csrf_token = $("#csrfmiddlewaretoken").val();
       
        $('#new-publish-new-geoserver-popup-error').html("");
        $('#new-publish-new-geoserver-popup-error').hide();
        $('#new-publish-new-geoserver-success').html("");
        $('#new-publish-new-geoserver-success').hide();
        
        if (newpublishspatialformat.length < 1) {
            $('#new-publish-new-geoserver-popup-error').html("Please choose a spatial format.");
            $('#new-publish-new-geoserver-popup-error').show();
            return false;
        }

        if (newpublishfrequencytype.length < 1) {
            $('#new-publish-new-geoserver-popup-error').html("Please choose a frequency type.");
            $('#new-publish-new-geoserver-popup-error').show();
            return false;
        }

        if (newpublishworkspace.length < 1) {
            $('#new-publish-new-geoserver-popup-error').html("Please choose a workspace.");
            $('#new-publish-new-geoserver-popup-error').show();
            return false;
        }
       
        $('#new-publish-spatial-format').attr('disabled','disabled');
        $('#new-publish-frequency-type').attr('disabled','disabled');
        $('#new-publish-workspace').attr('disabled','disabled');

        
        $.ajax({
            url: kbpublish.var.publish_save_geoserver_url,        
            type: 'POST',
            headers: {'X-CSRFToken' : csrf_token},
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {
                    var html = '';
                    console.log(response);
                
                    $('#new-publish-new-geoserver-popup-success').html("Successfully created publish entry");
                    $('#new-publish-new-geoserver-popup-success').show();                
                    setTimeout("$('#PublishNewGeoserverModal').modal('hide');",1000);
                    kbpublish.get_publish_geoservers();

                    //$('#new-publish-spatial-format').removeAttr('disabled');
                    //$('#new-publish-frequency-type').removeAttr('disabled');
                    //$('#new-publish-workspace').removeAttr('disabled');                                       

            },
            error: function (response) {
                console.log(response);
                var jsonresponse = {};
                if (response.hasOwnProperty('responseJSON')) { 
                    jsonresponse = response.responseJSON;
                }

                if (jsonresponse.hasOwnProperty('publish_entry')) {
                    $('#new-publish-new-geoserver-popup-error').html(jsonresponse['publish_entry']);
                    $('#new-publish-new-geoserver-popup-error').show();        
                } else {
                    $('#new-publish-new-geoserver-popup-error').html("Error create to publish.");
                    $('#new-publish-new-geoserver-popup-error').show();        
                }
                $('#new-publish-spatial-format').removeAttr('disabled');
                $('#new-publish-frequency-type').removeAttr('disabled');
                $('#new-publish-workspace').removeAttr('disabled');  
            },
        });


    },
    create_publish_cddp: function() {
        var publish_id = $('#publish_id').val();
        var newpublishname = $('#new-publish-cddp-name').val();
        var newpublishspatialformat = $('#new-publish-cddp-spatial-format').val();
        var newpublishspatialmode = $('#new-publish-cddp-spatial-mode').val();
        var newpublishfrequencytype = $('#new-publish-cddp-frequency-type').val();        
        var newpublishcddppath =  $('#new-publish-cddp-path').val();      

        var post_data = {"format": newpublishspatialformat, "name" : newpublishname, "mode": newpublishspatialmode, "frequency": newpublishfrequencytype, "path": newpublishcddppath, "publish_entry": publish_id};
        var csrf_token = $("#csrfmiddlewaretoken").val();
       
        $('#new-publish-new-cddp-popup-error').html("");
        $('#new-publish-new-cddp-popup-error').hide();
        $('#new-publish-new-cddp-success').html("");
        $('#new-publish-new-cddp-success').hide();
        
        if (newpublishspatialformat.length < 1) {
            $('#new-publish-new-cddp-popup-error').html("Please choose a spatial format.");
            $('#new-publish-new-cddp-popup-error').show();
            return false;
        }

        if (newpublishspatialmode.length < 1) {
            $('#new-publish-new-cddp-popup-error').html("Please choose a Spatial Mode.");
            $('#new-publish-new-cddp-popup-error').show();
            return false;
        }

        if (newpublishfrequencytype.length < 1) {
            $('#new-publish-new-cddp-popup-error').html("Please choose a frequency type.");
            $('#new-publish-new-cddp-popup-error').show();
            return false;
        }

        if (newpublishcddppath.length < 3) {
            $('#new-publish-new-cddp-popup-error').html("Please choose a path");
            $('#new-publish-new-cddp-popup-error').show();
            return false;
        }
       
        $('#new-publish-cddp-spatial-format').attr('disabled','disabled');
        $('#new-publish-cddp-frequency-type').attr('disabled','disabled');
        $('#new-publish-cddp-spatial-mode').attr('disabled','disabled');
        $('#new-publish-cddp-path').attr('disabled','disabled');
        
        $.ajax({
            url: kbpublish.var.publish_save_cddp_url,        
            type: 'POST',
            headers: {'X-CSRFToken' : csrf_token},
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {
                    var html = '';
                    console.log(response);                
                    $('#new-publish-new-cddp-popup-success').html("Successfully created publish entry");
                    $('#new-publish-new-cddp-popup-success').show();                
                    setTimeout("$('#PublishNewCDDPModal').modal('hide');",1000);
                    kbpublish.get_publish_cddp();                                      
            },
            error: function (response) {
                console.log(response);
                var jsonresponse = {};
                if (response.hasOwnProperty('responseJSON')) { 
                    jsonresponse = response.responseJSON;
                }

                if (jsonresponse.hasOwnProperty('publish_entry')) {
                    $('#new-publish-new-cddp-popup-error').html(jsonresponse['publish_entry']);
                    $('#new-publish-new-cddp-popup-error').show();        
                } else {
                    $('#new-publish-new-cddp-popup-error').html("Error create to publish.");
                    $('#new-publish-new-cddp-popup-error').show();        
                }

                $('#new-publish-cddp-spatial-format').removeAttr('disabled');
                $('#new-publish-cddp-frequency-type').removeAttr('disabled');
                $('#new-publish-cddp-spatial-mode').removeAttr('disabled');  
                $('#new-publish-cddp-path').removeAttr('disabled');  

            },
        });


    },    
    create_publish: function(success_callback, error_callback, catalogue_entry_id, description_id){
        // get & validation check
        // const name = utils.validate_empty_input('name', $('#'+name_id).val());
        const catalogue_entry = utils.validate_empty_input('catalogue_entry', $('#'+catalogue_entry_id).val());
        const description = utils.validate_empty_input('description', $('#'+description_id).val());
        
        // make data body
        var publish_data = {
            // name:name,
            catalogue_entry:catalogue_entry,
            description:description,
        };

        // set request
        var url = this.var.publish_save_url;
        var method = 'POST';
        var csrf_token = $("#csrfmiddlewaretoken").val();

        // call POST API
        $.ajax({
            url: url,
            method: method,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : csrf_token},
            data: JSON.stringify(publish_data),
            success: success_callback,
            error: error_callback,
        });
    },
    save_publish: function(save_status) {        
        var publish_id = $('#publish_id').val();
        var publishname = $('#publish-name').val();
        var publishcatalogueentry_id = $('#publish-catalogue-entry').val();
        var publishdescription = $('#publish-description').val();
        var post_data = {"name": publishname, "description": publishdescription, "catalogue_entry": publishcatalogueentry_id};
        var csrf_token = $("#csrfmiddlewaretoken").val();

        $.ajax({
            url: kbpublish.var.publish_save_url+publish_id+"/",
            //method: 'POST',
            type: 'PUT',
            //dataType: 'json',
            headers: {'X-CSRFToken' : csrf_token},
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {

                if (save_status == 'save-and-exit') {
                    window.location = '/publish/';
                } else {
                   window.location = "/publish/"+publish_id;
                }
            },
            error: function (error) {
                 alert("ERROR Saving.");

        
            },
        });


    },
    get_publish: function(params_str) {
        params = {
            catalogue_entry__name__icontains:        $('#publish-name').val(),
            status:                 $('#publish-status').val(),
            description__icontains: $('#publish-description').val(),
            catalogue_entry__custodian__name__icontains: $('#publish-custodian').val(),
            assigned_to:            $('#publish-assignedto').val(),
            updated_after:          utils.convert_date_format($('#publish-lastupdatedfrom').val(), kbpublish.var.publish_date_format, hh="00", mm="00", ss="00"),
            updated_before:         utils.convert_date_format($('#publish-lastupdatedto').val(), kbpublish.var.publish_date_format, hh="23", mm="59", ss="59"),
            id:                     $('#publish-number').val().replace("PE", ""),
            limit:                  $('#publish-limit').val(),
            order_by:               $('#publish-order-by').val()
        }

        if (!params_str){
            params_str = utils.make_query_params(params);
        }

        //order_by=&limit=10" 
        $.ajax({
            url: kbpublish.var.publish_data_url+"?"+params_str,
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                var html = '';
                
                if (response != null) {
                    if (response.results.length > 0) {
                        for (let i = 0; i < response.results.length; i++) {
                            assigned_to_friendly = "";
                            if (response.results[i].first_name != null) {

                                console.log ("HERE");
                                
                                assigned_to_friendly = response.results[i].first_name;

                                if (response.results[i].last_name != null) {
                                    assigned_to_friendly += " "+response.results[i].last_name;
    
                                }

                            } 
                            
                            if (assigned_to_friendly.replace(" ","").length == 0) {
                                if (response.results[i].email != null) {
                                    assigned_to_friendly = response.results[i].email;
                                }

                            }


                            button_json = '{"id": "'+response.results[i].id+'"}'

                            html+= "<tr>";
                            html+= " <td>PE"+response.results[i].id+"</td>";
                            html+= " <td>"+response.results[i].name+"</td>";


                            html+= " <td>";
                            if (response.results[i].custodian_name != null) { 
                                html+= response.results[i].custodian_name;
                            } else {
                                html+= "";
                            }
                            html+= "</td>";                            
                            html+= " <td>"+kbpublish.var.publish_status[response.results[i].status]+"</td>";
                            html+= " <td>"+response.results[i].updated_at+"</td>";
                            html+= " <td>"+assigned_to_friendly+"</td>";
                            html+= " <td class='text-end'>";
                            if (response.results[i].status == 1) {
                                html+= " <button class='btn btn-primary btn-sm publish-to-geoserver-btn' id='publish-to-geoserver-btn-"+response.results[i].id+"' data-json='"+button_json+"' >Publish Geoserver</button>&nbsp;";
                                html+= " <button class='btn btn-primary btn-sm publish-to-cddp-btn' id='publish-to-cddp-btn-"+response.results[i].id+"' data-json='"+button_json+"'>Publish CDDP</button>&nbsp;";                        
                                html+= " <button class='btn btn-primary btn-sm publish-table-button' id='publish-external-loading-"+response.results[i].id+"' type='button' disabled><span class='spinner-grow spinner-grow-sm' role='status' aria-hidden='true'></span><span class='visually-hidden'>Loading...</span></button>&nbsp;";
                                html+= " <button class='btn btn-success btn-sm publish-table-button' id='publish-external-success-"+response.results[i].id+"' type='button' disabled><i class='bi bi-check'></i></button>&nbsp;";
                                html+= " <button class='btn btn-danger btn-sm publish-table-button' id='publish-external-error-"+response.results[i].id+"' type='button' disabled><i class='bi bi-x-lg'></i></button>&nbsp;";
                            }
                            html+="  <a class='btn btn-primary btn-sm' href='/publish/"+response.results[i].id+"'>View</a>";
                            html+="  <button class='btn btn-primary btn-sm'>History</button>";
                            html+="  </td>";
                            html+= "<tr>";
                        }
                                           
                        $('#publish-tbody').html(html);
                        $('.publish-table-button').hide();

                    } else {
                        $('#publish-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");
                    }
                    common_pagination.init(response.count, params, kbpublish.get_publish, $('#paging_navi'));
                } else {
                      $('#publish-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");
                }

                $( ".publish-to-geoserver-btn" ).click(function() {
                    console.log("Publish Geoserver");
                    console.log($(this).attr('data-json'));
                    var btndata_json = $(this).attr('data-json');
                    var btndata = JSON.parse(btndata_json);

                    kbpublish.publish_to_geoserver(btndata.id);
                });     
                
                $( ".publish-to-cddp-btn" ).click(function() {
                    console.log("Publish Geoserver");
                    console.log($(this).attr('data-json'));
                    var btndata_json = $(this).attr('data-json');
                    var btndata = JSON.parse(btndata_json);
                    kbpublish.publish_to_cddp(btndata.id);
                });                    

       
            },
            error: function (error) {
                $('#save-publish-popup-error').html("Error Loading publish data");
                $('#save-publish-popup-error').show();
                $('#save-publish-tbody').html('');

                console.log('Error Loading publish data');
            },
        });    
    },
    publish_to_cddp: function(btn_id) { 
        var csrf_token = $("#csrfmiddlewaretoken").val();
        
        $('#publish-to-geoserver-btn-'+btn_id).attr('disabled','disabled');
        $('#publish-to-cddp-btn-'+btn_id).attr('disabled','disabled');
        $("#publish-external-success-"+btn_id).hide();
        $("#publish-external-error-"+btn_id).hide();
        $('#publish-external-loading-'+btn_id).show();
        post_data = {};
        $.ajax({
            url: kbpublish.var.publish_data_url+btn_id+"/publish/cddp/?symbology_only=false",
            type: 'POST',
            //dataType: 'json',
            headers: {'X-CSRFToken' : csrf_token},
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {
                $('#publish-external-loading-'+btn_id).hide();
                $("#publish-external-success-"+btn_id).show();
                $('#publish-to-geoserver-btn-'+btn_id).removeAttr('disabled');
                $('#publish-to-cddp-btn-'+btn_id).removeAttr('disabled');                
            },
            error: function (error) {
                $('#publish-external-loading-'+btn_id).hide();
                $("#publish-external-error-"+btn_id).show();
                $('#publish-to-geoserver-btn-'+btn_id).removeAttr('disabled');
                $('#publish-to-cddp-btn-'+btn_id).removeAttr('disabled');   
            },
        });        
    },
    publish_to_geoserver: function(btn_id) { 
        var csrf_token = $("#csrfmiddlewaretoken").val();

        $('#publish-to-geoserver-btn-'+btn_id).attr('disabled','disabled');
        $('#publish-to-cddp-btn-'+btn_id).attr('disabled','disabled');
        $("#publish-external-success-"+btn_id).hide();
        $("#publish-external-error-"+btn_id).hide();
        $('#publish-external-loading-'+btn_id).show();

        post_data = {};
        $.ajax({
            url: kbpublish.var.publish_data_url+btn_id+"/publish/geoserver/?symbology_only=false",
            type: 'POST',
            //dataType: 'json',
            headers: {'X-CSRFToken' : csrf_token},
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {
                $('#publish-external-loading-'+btn_id).hide();
                $("#publish-external-success-"+btn_id).show();
                $('#publish-to-geoserver-btn-'+btn_id).removeAttr('disabled');
                $('#publish-to-cddp-btn-'+btn_id).removeAttr('disabled');  
            },
            error: function (error) {
                $('#publish-external-loading-'+btn_id).hide();
                $("#publish-external-error-"+btn_id).show();
                $('#publish-to-geoserver-btn-'+btn_id).removeAttr('disabled');
                $('#publish-to-cddp-btn-'+btn_id).removeAttr('disabled');   
            },
        });        
    },    
    get_publish_editors: function() {
        var publish_id = $('#publish_id').val();
        $.ajax({
            url: kbpublish.var.publish_data_url+publish_id+"/editors/",
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                var html = '';
                
                if (response != null) {
                    if (response.length > 0) {
                        for (let i = 0; i < response.length; i++) {
                            // assigned_to_friendly = "";
                            // if (response.results[i].first_name != null) {

                            //     assigned_to_friendly = response.results[i].first_name;

                            //     if (response.results[i].last_name != null) {
                            //         assigned_to_friendly += " "+response.results[i].last_name;
    
                            //     }

                            // } 
                            
                            // if (assigned_to_friendly.replace(" ","").length == 0) {
                            //     if (response.results[i].email != null) {
                            //         assigned_to_friendly = response.results[i].email;
                            //     }

                            // }
                            button_json = '{"id": "'+response[i].id+'"}'

                            html+= "<tr>";
                            html+= " <td>"+response[i].id+"</td>";
                            html+= " <td>"+response[i].first_name+"</td>";
                            html+= " <td>"+response[i].last_name+"</td>";                        
                            html+= " <td>"+response[i].email+"</td>";                                                    
                            html+= " <td class='text-end'><button class='btn btn-danger btn-sm publish-editors-delete' data-json='"+button_json+"' >Delete</button></td>";
                            html+= "<tr>";
                        }
                                                                   
                        $('#publish-editors-tbody').html(html);
                        $( ".publish-editors-delete" ).click(function() {
                            console.log($(this).attr('data-json'));
                            var btndata_json = $(this).attr('data-json');
                            var btndata = JSON.parse(btndata_json);
                            kbpublish.delete_publish_editor(btndata.id);
                            
                            
                        });                         
                    } else {
                        $('#publish-editors-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");

                    }
                } else {
                      $('#publish-editors-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");
                }

       
            },
            error: function (error) {
                $('#save-publish-popup-error').html("Error Loading publish data");
                $('#save-publish-popup-error').show();
                $('#save-publish-tbody').html('');

                console.log('Error Loading publish data');
            },
        });
    },
    get_publish_geoservers: function() {
        var publish_id = $('#publish_id').val();
        $.ajax({
            url: kbpublish.var.publish_data_url+publish_id+"/geoserver/",
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                var html = '';
                
                if (response != null) {
                    console.log(response);
                    if (response.length > 0) {
                        var responsejson = response;
                        for (let i = 0; i < responsejson.length; i++) {
                            
                            button_json = '{"id": "'+responsejson[i].id+'"}'

                            html+= "<tr>";
                            html+= " <td>"+responsejson[i].id+"</td>";                        
                            html+= " <td>"+kbpublish.var.publish_geoserver_format[responsejson[i].mode]+"</td>";                        
                            html+= " <td>"+kbpublish.var.publish_geoserver_frequency[responsejson[i].frequency]+"</td>";                                                    
                            html+= " <td>"+responsejson[i].workspace_name+"</td>"; 
                            html+= " <td>";
                            if (responsejson[i].published_at == null) {
                                html+= "Not Published";   
                            } else {
                                html+= responsejson[i].published_at;
                            }
                            html+= "</td>";
                            html+= " <td class='text-end'>";
                            if (kbpublish.var.has_edit_access == true) {
                                html+= "<button class='btn btn-primary btn-sm publish-geoserver-update' data-json='"+button_json+"' >Update</button> ";
                                html+= "<button class='btn btn-danger btn-sm publish-geoserver-delete' data-json='"+button_json+"' >Delete</button>";
                            }
                            html+= "</td>";
                            html+= "<tr>";
                            console.log(html);                                       
                            $('#publish-geoserver-tbody').html(html);
                            $( ".publish-geoserver-delete" ).click(function() {
                                console.log($(this).attr('data-json'));
                                var btndata_json = $(this).attr('data-json');
                                var btndata = JSON.parse(btndata_json);
                                kbpublish.delete_publish_geoserver(btndata.id);                                                        
                            });
                            $( ".publish-geoserver-update" ).click(function() {
                                kbpublish.show_update_geoserver_modal(responsejson[i]);
                            });
                        }
                    } else {
                        $('#publish-geoserver-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");

                    }
                } else {
                      $('#publish-geoserver-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");
                }

       
            },
            error: function (error) {
                $('#save-publish-popup-error').html("Error Loading publish data");
                $('#save-publish-popup-error').show();
                $('#save-publish-tbody').html('');

                console.log('Error Loading publish data');
            },
        });
    },
    show_update_geoserver_modal: function(prev){
        common_entity_modal.init("Update Geoserver Notification", "submit");
        common_entity_modal.add_field(label="Name", type="text", value=$('#catalogue-name-id').val(), option_map=null, disabled=true);
        let format_id = common_entity_modal.add_field(label="Spatial Format", type="select", value=prev.mode, option_map=kbpublish.var.publish_geoserver_format);
        let frequency_id = common_entity_modal.add_field(label="Frequency Type", type="select", value=prev.frequency, option_map=kbpublish.var.publish_geoserver_frequency);
        let workspace_id = common_entity_modal.add_field(label="Workspace", type="select", value=prev.workspace_id, option_map=kbpublish.var.publish_workspace_map);
        
        common_entity_modal.add_callbacks(submit_callback=(success_callback, error_callback)=> 
                                            this.write_geoserver(success_callback, error_callback, format_id, frequency_id, workspace_id, prev.id),
                                            success_callback=this.get_publish_geoservers);
        common_entity_modal.show();
    },
    write_geoserver: function(success_callback, error_callback, format_id, frequency_id, workspace_id, geoserver_id){
        // get & validation check
        const mode = utils.validate_empty_input('format', $('#'+format_id).val());
        const frequency = utils.validate_empty_input('frequency', $('#'+frequency_id).val());
        const workspace = utils.validate_empty_input('workspace', $('#'+workspace_id).val());
        
        // make data body
        var geoserver_data = {
            mode:mode,
            frequency:frequency,
            workspace:workspace,
            publish_entry:$('#publish-entry-id')
        };
        var url = this.var.publish_save_geoserver_url;
        var method = 'POST';
        if(geoserver_id){
            delete geoserver_data['publish_entry'];
            url += geoserver_id+'/';
            method = 'PUT';
        }

        // call POST API
        $.ajax({
            url: url,
            method: method,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            data: JSON.stringify(geoserver_data),
            success: success_callback,
            error: error_callback
        });
    },

    get_publish_cddp: function() {
        var publish_id = $('#publish_id').val();
        $.ajax({
            url: kbpublish.var.publish_data_url+publish_id+"/cddp/",
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                var html = '';
                
                if (response != null) {
                    console.log(response);
                    if (response.length > 0) {
                        var responsejson = response;
                        for (let i = 0; i < responsejson.length; i++) {
                            
                            button_json = '{"id": "'+responsejson[i].id+'"}'

                            html+= "<tr>";
                            html+= " <td>"+responsejson[i].id+"</td>";                        
                            html+= " <td>"+kbpublish.var.publish_cddp_format[responsejson[i].format]+"</td>";                        
                            html+= " <td>"+kbpublish.var.publish_cddp_mode[responsejson[i].mode]+"</td>";     
                            html+= " <td>"+kbpublish.var.publish_cddp_frequency[responsejson[i].frequency]+"</td>";                                                    
                            html+= " <td>"+responsejson[i].path+"</td>"; 
                            html+= " <td>";
                            if (responsejson[i].published_at == null) {
                                html+= "Not Published";   
                            } else {
                                html+= responsejson[i].published_at;
                            }
                            html+= "</td>";
                            html+= " <td class='text-end'>";
                            if (kbpublish.var.has_edit_access == true) {
                                html+= "<button class='btn btn-primary btn-sm publish-cddp-update' data-json='"+button_json+"' >Update</button> ";
                                html+= "<button class='btn btn-danger btn-sm publish-cddp-delete' data-json='"+button_json+"' >Delete</button>";
                            }
                            html+= "</td>";
                            html+= "<tr>";
                            console.log(html);                                       
                            $('#publish-cddp-tbody').html(html);
                            $( ".publish-cddp-delete" ).click(function() {
                                console.log($(this).attr('data-json'));
                                var btndata_json = $(this).attr('data-json');
                                var btndata = JSON.parse(btndata_json);
                                kbpublish.delete_publish_cddp(btndata.id);                                                        
                            });
                            $( ".publish-cddp-update" ).click(function() {
                                kbpublish.show_update_cddp_modal(responsejson[i]);
                            });
                        }
                    } else {
                        $('#publish-cddp-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");

                    }
                } else {
                      $('#publish-cddp-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");
                }

       
            },
            error: function (error) {
                $('#save-publish-popup-error').html("Error Loading publish data");
                $('#save-publish-popup-error').show();
                $('#save-publish-tbody').html('');

                console.log('Error Loading publish data');
            },
        });
    },
    show_update_cddp_modal: function(prev){
        common_entity_modal.init("Update Cddp Notification", "submit");
        let name_id = common_entity_modal.add_field(label="Name", type="text", value=prev.name);
        let format_id = common_entity_modal.add_field(label="Spatial Format", type="select", value=prev.format, option_map=kbpublish.var.publish_cddp_format);
        let mode_id = common_entity_modal.add_field(label="Spatial Mode", type="select", value=prev.mode, option_map=kbpublish.var.publish_cddp_mode);
        let frequency_id = common_entity_modal.add_field(label="Frequency Type", type="select", value=prev.frequency, option_map=kbpublish.var.publish_cddp_frequency);
        let path_id = common_entity_modal.add_field(label="Path", type="text", value=prev.path);

        common_entity_modal.add_callbacks(submit_callback=(success_callback, error_callback)=> 
                                            this.write_cddp(success_callback, error_callback, name_id, format_id, mode_id, frequency_id, path_id, prev.id),
                                            success_callback=this.get_publish_cddp);
        common_entity_modal.show();
    },
    write_cddp: function(success_callback, error_callback, name_id, format_id, mode_id, frequency_id, path_id, cddp_id){
        // get & validation check
        const name = utils.validate_empty_input('name', $('#'+name_id).val());
        const format = utils.validate_empty_input('format', $('#'+format_id).val());
        const mode = utils.validate_empty_input('mode', $('#'+mode_id).val());
        const frequency = utils.validate_empty_input('frequency', $('#'+frequency_id).val());
        const path = utils.validate_empty_input('path', $('#'+path_id).val());
        
        // make data body
        var cddp_data = {
            name:name,
            format:format,
            mode:mode,
            frequency:frequency,
            path:path,
            publish_entry:$('#publish-entry-id')
        };
        var url = this.var.publish_save_cddp_url;
        var method = 'POST';
        if(cddp_id){
            delete cddp_data['publish_entry'];
            url += cddp_id+'/';
            method = 'PUT';
        }

        // call POST API
        $.ajax({
            url: url,
            method: method,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            data: JSON.stringify(cddp_data),
            success: success_callback,
            error: error_callback
        });
    },

    show_add_email_notification_modal: function(){
        common_entity_modal.init("Add New Email Notification", "submit");
        let name_id = common_entity_modal.add_field(label="Name", type="text");
        let type_id = common_entity_modal.add_field(label="Type", type="select", value=null, option_map=this.var.publish_email_notification_type);
        let email_id = common_entity_modal.add_field(label="Email", type="email");
        let active_id = common_entity_modal.add_field(label="Active", type="switch");
        common_entity_modal.add_callbacks(submit_callback=(success_callback, error_callback)=> 
                                            this.write_email_notification(success_callback, error_callback, name_id, type_id, email_id, active_id),
                                            success_callback=()=>table.refresh(this.get_email_notification));
        common_entity_modal.show();
    },
    show_update_email_notification_modal: function(prev){
        common_entity_modal.init("Update Email Notification", "submit");
        let name_id = common_entity_modal.add_field(label="Name", type="text", value=prev.name);
        let type_id = common_entity_modal.add_field(label="Type", type="select", value=prev.type, option_map=this.var.publish_email_notification_type);
        let email_id = common_entity_modal.add_field(label="Email", type="email", value=prev.email);
        let active_id = common_entity_modal.add_field(label="Active", type="switch", value=prev.active);
        common_entity_modal.add_callbacks(submit_callback=(success_callback, error_callback)=> 
                                            this.write_email_notification(success_callback, error_callback, name_id, type_id, email_id, active_id, prev.id),
                                            success_callback=()=>table.refresh(this.get_email_notification));
        common_entity_modal.show();
    },
    write_email_notification: function(success_callback, error_callback, name_id, type_id, email_id, active_id, noti_id){
        // get & validation check
        const name = utils.validate_empty_input('name', $('#'+name_id).val());
        const type = utils.validate_empty_input('type', $('#'+type_id).val());
        const email = utils.validate_empty_input('email', $('#'+email_id).val());
        utils.validate_email(email);
        const active = $('#'+active_id).prop('checked');
        
        // make data body
        var email_noti_data = {
            name:name,
            type:type,
            email:email,
            active:active,
            publish_entry:$('#publish-entry-id').val()
        };
        var url = this.var.publish_email_notification_url;
        var method = 'POST';
        if(noti_id){
            delete email_noti_data['publish_entry'];
            url += noti_id+'/';
            method = 'PUT';
        }

        // call POST API
        $.ajax({
            url: url,
            method: method,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            data: JSON.stringify(email_noti_data),
            success: success_callback,
            error: error_callback
        });
    },

    show_delete_email_notification_modal: function(target){
        common_entity_modal.init("Delte Email Notification", "delete");
        common_entity_modal.add_field(label="Name", type="text", value=target.name);
        common_entity_modal.add_field(label="Type", type="select", value=target.type, option_map=this.var.publish_email_notification_type);
        common_entity_modal.add_field(label="Email", type="email", value=target.email);
        common_entity_modal.add_field(label="Active", type="switch", value=target.active);
        common_entity_modal.add_callbacks(submit_callback=(success_callback, error_callback)=> 
                                            this.delete_email_notification(success_callback, error_callback, target.id),
                                            success_callback=()=>table.refresh(this.get_email_notification));
        common_entity_modal.show();
    },

    delete_email_notification: function(success_callback, error_callback, noti_id){
        $.ajax({
            url: kbpublish.var.publish_email_notification_url+noti_id+"/",
            method: 'DELETE',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            success: success_callback, 
            error: error_callback
        });
    },
    get_email_notification: function(params_str) {
        if (!params_str){
            params = {
                publish_id:     $('#publish-entry_id').val(),
                limit:          $('#publish-notification-limit').val(),
                order_by:       $('#publish-notification-order-by').val()
            }

            params_str = utils.make_query_params(params);
        }

        $.ajax({
            url: kbpublish.var.publish_email_notification_url+"?"+params_str,
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                if(!response){
                    $('#publish-notification-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");
                    return;
                }
                // change type number to name
                let buttons={};
                for(let i in response.results){
                    response.results[i].type_str = kbpublish.var.publish_email_notification_type[response.results[i].type];
                }

                if(kbpublish.var.has_edit_access){
                    buttons = {Update:(noti)=>kbpublish.show_update_email_notification_modal(noti),
                               Delete:(noti)=>kbpublish.show_delete_email_notification_modal(noti)};
                }

                table.set_tbody($('#publish-notification-tbody'), response.results, 
                                columns=[{id:'text'}, {name:'text'}, {type_str:'text'}, {email:'text'}, {active:'switch'}], 
                                buttons=buttons);
                common_pagination.init(response.count, params, kbpublish.get_email_notification, $('#notification-paging-navi'));
            },
            error: function (error) {
                alert('Error occured.');
                console.log('Error occured.'+ error);
            },
        });
    }
// create_publish: function() {
    //     var publishname = $('#new-publish-name').val();
    //     var publishcatalogueentry_id = $('#new-catalogue-entry').val();
    //     var publishdescription = $('#new-publish-description').val();
    //     var post_data = {"name": publishname, "description": publishdescription, "catalogue_entry": publishcatalogueentry_id};
    //     var csrf_token = $("#csrfmiddlewaretoken").val();
       
    //     $('#new-publish-popup-error').html("");
    //     $('#new-publish-popup-error').hide();
    //     $('#new-publish-popup-success').html("");
    //     $('#new-publish-popup-success').hide();
        
    //     if (publishname.length < 1) {
    //         $('#new-publish-popup-error').html("Please enter a publish name.");
    //         $('#new-publish-popup-error').show();
    //         return false;
    //     }

    //     if (publishdescription.length < 10) {
    //         $('#new-publish-popup-error').html("Please enter a valid publish description. (min 10 characters)");
    //         $('#new-publish-popup-error').show();
    //         return false;
    //     }

    //     if (publishcatalogueentry_id.length < 1) {
    //         $('#new-publish-popup-error').html("Please select a catalogue entry.");
    //         $('#new-publish-popup-error').show();
    //         return false;
    //     }

       
    //     $('#new-publish-name').attr('disabled','disabled');
    //     $('#new-catalogue-entry').attr('disabled','disabled');
    //     $('#new-publish-description').attr('disabled','disabled');

        

    //     $.ajax({
    //         url: kbpublish.var.publish_save_url,        
    //         type: 'POST',
    //         headers: {'X-CSRFToken' : csrf_token},
    //         data: JSON.stringify(post_data),
    //         contentType: 'application/json',
    //         success: function (response) {
    //             var html = '';
    //             console.log(response);
                
    //             if (response != null) {

    //                 $('#new-publish-popup-success').html("Successfully created publish entry");
    //                 $('#new-publish-popup-success').show();

    //                 setTimeout("window.location = '/publish/"+response.id+"';", 2000); 
                    
                    
    //             } else {                
    //                 $('#new-publish-popup-error').html("Error no response ID.");
    //                 $('#new-publish-popup-error').show();       
                    
    //                 $('#new-publish-name').removeAttr('disabled');
    //                 $('#new-catalogue-entry').removeAttr('disabled');
    //                 $('#new-publish-description').removeAttr('disabled');                    
    //             }

       
    //         },
    //         error: function (error) {

    //             $('#new-publish-popup-error').html("Error create to publish.");
    //             $('#new-publish-popup-error').show();        

    //             $('#new-publish-name').removeAttr('disabled');
    //             $('#new-catalogue-entry').removeAttr('disabled');
    //             $('#new-publish-description').removeAttr('disabled');
               
    //         },
    //     });


    // },
}
