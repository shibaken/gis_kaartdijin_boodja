var kbpublish = {
    var: {
            publish_data_url: "/api/publish/entries/",
            publish_save_url: "/api/publish/entries/", 
            publish_data_geoserver_url: "/api/publish/channels/geoserver/",
            publish_save_geoserver_url: "/api/publish/channels/geoserver/",
            publish_data_cddp_url: "/api/publish/channels/cddp/",                       
            publish_save_cddp_url: "/api/publish/channels/cddp/",
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
    },
    pagination: kbpublish_pagination,
    init_dashboard: function() {    

        $('#publish-custodian').select2({
            placeholder: 'Select an option',
            minimumInputLength: 2,
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


        $('#publish-lastupdatedfrom').datepicker({ dateFormat: 'yyyy-mm-dd', 
            format: 'dd/mm/yyyy',
        });
        $('#publish-lastupdatedto').datepicker({  dateFormat: 'yyyy-mm-dd', 
                format: 'dd/mm/yyyy',
        });


        $( "#publish-filter-btn" ).click(function() {
            console.log("Reload Publish Table");
            kbpublish.get_publish();
        });
        $( "#publish-new-btn" ).click(function() {
            console.log("New Publish");
            $('#new-publish-popup-error').html("");
            $('#new-publish-popup-error').hide();
            $('#new-publish-popup-success').html("");
            $('#new-publish-popup-success').hide();

            $('#new-publish-name').val("");
            $('#new-catalogue-entry').val("");
            $('#new-publish-description').val("");
            
            $('#NewPublishModal').modal('show');
        });           
        $( "#create-publish-btn" ).click(function() {
            kbpublish.create_publish(); 
        }); 
        $( "#publish-limit" ).change(function(){
            common_pagination.var.current_page=0;
            kbpublish.get_publish();
        })
        $( "#publish-order-by" ).change(function(){
            common_pagination.var.current_page=0;
            kbpublish.get_publish();
        })

      

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

        kbpublish.get_publish_geoservers();
        kbpublish.get_publish_cddp();
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
    create_publish: function() {
        var publishname = $('#new-publish-name').val();
        var publishcatalogueentry_id = $('#new-catalogue-entry').val();
        var publishdescription = $('#new-publish-description').val();
        var post_data = {"name": publishname, "description": publishdescription, "catalogue_entry": publishcatalogueentry_id};
        var csrf_token = $("#csrfmiddlewaretoken").val();
       
        $('#new-publish-popup-error').html("");
        $('#new-publish-popup-error').hide();
        $('#new-publish-popup-success').html("");
        $('#new-publish-popup-success').hide();
        
        if (publishname.length < 1) {
            $('#new-publish-popup-error').html("Please enter a publish name.");
            $('#new-publish-popup-error').show();
            return false;
        }

        if (publishdescription.length < 10) {
            $('#new-publish-popup-error').html("Please enter a valid publish description. (min 10 characters)");
            $('#new-publish-popup-error').show();
            return false;
        }

        if (publishcatalogueentry_id.length < 1) {
            $('#new-publish-popup-error').html("Please select a catalogue entry.");
            $('#new-publish-popup-error').show();
            return false;
        }

       
        $('#new-publish-name').attr('disabled','disabled');
        $('#new-catalogue-entry').attr('disabled','disabled');
        $('#new-publish-description').attr('disabled','disabled');

        

        $.ajax({
            url: kbpublish.var.publish_save_url,        
            type: 'POST',
            headers: {'X-CSRFToken' : csrf_token},
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {
                var html = '';
                console.log(response);
                
                if (response != null) {

                    $('#new-publish-popup-success').html("Successfully created publish entry");
                    $('#new-publish-popup-success').show();

                    setTimeout("window.location = '/publish/"+response.id+"';", 2000); 
                    
                    
                } else {                
                    $('#new-publish-popup-error').html("Error no response ID.");
                    $('#new-publish-popup-error').show();       
                    
                    $('#new-publish-name').removeAttr('disabled');
                    $('#new-catalogue-entry').removeAttr('disabled');
                    $('#new-publish-description').removeAttr('disabled');                    
                }

       
            },
            error: function (error) {

                $('#new-publish-popup-error').html("Error create to publish.");
                $('#new-publish-popup-error').show();        

                $('#new-publish-name').removeAttr('disabled');
                $('#new-catalogue-entry').removeAttr('disabled');
                $('#new-publish-description').removeAttr('disabled');
               
            },
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
            id:                     $('#publish-number').val().replace("PE", ""),
            limit:                  $('#publish-limit').val(),
            order_by:               $('#publish-order-by').val()
        }

        if (!params_str){
            params_str = common_pagination.make_get_params_str(params);
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
                            html+= " <td>NONE</td>";
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

                        common_pagination.init(response.count, params, kbpublish.get_publish, +params.limit, $('#paging_navi'));

                    } else {
                        $('#publish-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");

                    }
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


    

}