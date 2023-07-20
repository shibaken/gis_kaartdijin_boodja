var kbcatalogue = { 
    var: {
         catalogue_data_url: "/api/catalogue/entries/",
         catalogue_permission_url: "/api/catalogue/permission/",
         catalogue_layer_symbology_url: "/api/catalogue/layers/symbologies/",
         catalogue_status: {
            1: "New Draft",
            2: "Locked",
            3: "Declined",
            4: "Draft",
            5: "Pending"
        },
        catalogue_Type: {
            1: "Special File",
            2: "Subscription",
        },
        catalogue_date_format: "dd/mm/yyyy",
        catalogue_table_date_format: "DD MMM YYYY HH:mm:ss",
    },
    
    init_dashboard: function() { 

        $('#catalogue-lastupdatedfrom').datepicker({ dateFormat: 'yyyy-mm-dd', 
                                                    format: 'dd/mm/yyyy',
                                                });
        $('#catalogue-lastupdatedto').datepicker({  dateFormat: 'yyyy-mm-dd', 
                                                    format: 'dd/mm/yyyy',
                                                });
        
        $('#catalogue-custodian').select2({
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

        $('#catalogue-assignedto').select2({
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

        $( "#catalogue-filter-btn" ).click(function() {
            kbcatalogue.get_catalogue();
        });
        $( "#catalogue-limit" ).change(function() {
            common_pagination.var.current_page=0;
            kbcatalogue.get_catalogue();
        });
        $( "#catalogue-order-by" ).change(function() {
            common_pagination.var.current_page=0;
            kbcatalogue.get_catalogue();
        });
        kbcatalogue.get_catalogue();
    },

    init_catalogue_item: function() { 
        $( "#catalogue-entry-symbology-btn-save" ).click(function() {
            console.log("Save Publish Table");
            kbcatalogue.save_symbology('save');
        });
        $( "#ccatalogue-entry-symbology-btn-save-exit" ).click(function() {
            console.log("Save Publish Table");
            kbcatalogue.save_symbology('save-and-exit');
        });           

        $( "#catalogue-lock" ).click(function() {
            console.log("Locking");
            kbcatalogue.change_catalogue_status('lock');
        });
        $( "#catalogue-unlock" ).click(function() {
            console.log("Unlocking");
            kbcatalogue.change_catalogue_status('unlock');
        });
        $( "#catalogue-assigned-to-btn" ).click(function() {
            console.log("Assign To");
            kbcatalogue.set_assigned_to();
        });

        let select2_setting = {
            placeholder: "User's name",
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
        };

        $( "#catalogue-manage-editors-btn" ).click(function(){
            kbcatalogue.get_catalogue_editors();
            $('#manage-editors-search').val("").trigger('change');
            $('#manage-popup-error').hide();
            $('#ManageEditorsModal').modal('show');
        });
        
        $('#manage-editors-search').select2(select2_setting);
        
        $('#manage-editors-add-btn').click(function(e){
            kbcatalogue.add_catalogue_editor($('#manage-editors-search').val());
        });
    },

    change_catalogue_status: function(status) {        
        var status_url = "lock";
        if (status == 'unlock') {
            status_url = 'unlock';
        }

        var catalogue_entry_id = $('#catalogue_entry_id').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();
        var pagetab = $('#pagetab').val();

        $.ajax({
            url: kbcatalogue.var.catalogue_data_url+catalogue_entry_id+"/"+status_url+"/",
            //method: 'POST',
            type: 'POST',
            //dataType: 'json',
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response) {
                window.location = "/catalogue/entries/"+catalogue_entry_id+"/"+pagetab+"/";       
            },
            error: function (error) {
                common_entity_modal.show_alert("ERROR Changing Status");
            },
        });
    },

    set_assigned_to: function() { 
        var catalogueassignedto = $('#catalogue-assigned-to').val();
        var catalogue_entry_id = $('#catalogue_entry_id').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();
        var pagetab = $('#pagetab').val();

        if (catalogueassignedto.length > 0) {  
            $.ajax({
                url: kbcatalogue.var.catalogue_data_url+catalogue_entry_id+"/assign/"+catalogueassignedto+"/",
                type: 'POST',
                headers: {'X-CSRFToken' : csrf_token},
                contentType: 'application/json',
                success: function (response) {
                    var html = '';
                   
                    window.location = "/catalogue/entries/"+catalogue_entry_id+"/"+pagetab+"/"; 
           
                },
                error: function (error) {
                     common_entity_modal.show_alert("ERROR Setting assigned person.");
                },
            });            
        } else {
            common_entity_modal.show_alert("Please select an assigned to person first.");
        }
    },

    save_symbology: function(save_status) {        
        var catalogue_id = $('#catalogue_entry_id').val();
        var cataloguesymbologydefinition = $('#catalogue-entry-symbology-definition').val();    
        var post_data = {"sld": cataloguesymbologydefinition};
        var layer_symbology_id = $('#catalogue-entry-symbology-definition-id').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();
        var pagetab = $('#pagetab').val();

        $.ajax({
            url: kbcatalogue.var.catalogue_layer_symbology_url+layer_symbology_id+"/",
            //method: 'POST',
            type: 'PUT',
            //dataType: 'json',
            headers: {'X-CSRFToken' : csrf_token},
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {

                if (save_status == 'save-and-exit') {
                    window.location = '/catalogue/entries/';
                } else {
                   window.location = "/catalogue/entries/"+catalogue_id+"/"+pagetab+"/"; 
                }
            },
            error: function (error) {
                common_entity_modal.show_alert("ERROR Saving."); 
            },
        });
    },

    get_catalogue: function(params_str) {
        if (!params_str){
            params = {
                name__icontains:        $('#catalogue-name').val(),
                status:                 $('#catalogue-status').val(),
                description__icontains: $('#catalogue-description').val(),
                custodian:              +$('#catalogue-custodian').val(),
                assigned_to:            +$('#catalogue-assignedto').val(),
                updated_after:          utils.convert_date_format($('#catalogue-lastupdatedfrom').val(), kbcatalogue.var.catalogue_date_format, hh="00", mm="00", ss="00"),
                updated_before:         utils.convert_date_format($('#catalogue-lastupdatedto').val(), kbcatalogue.var.catalogue_date_format, hh="23", mm="59", ss="59"),
                id:                     $('#catalogue-number').val().replace("PE", ""),
                type:                   $('#catalogue-type').val(),
                limit:                  $('#catalogue-limit').val(),
                order_by:               $('#catalogue-order-by').val()
            }

            params_str = utils.make_query_params(params);
        }

        $.ajax({
            url: kbcatalogue.var.catalogue_data_url+"?"+params_str,
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                var html = '';
                
                if (response != null) {
                    if (response.results.length > 0) {
                        for (let i = 0; i < response.results.length; i++) {
                            assigned_to_friendly = "";
                            if (response.results[i].assigned_to_first_name != null) {

                                assigned_to_friendly = response.results[i].assigned_to_first_name;

                                if (response.results[i].assigned_to_last_name != null) {
                                    assigned_to_friendly += " "+response.results[i].assigned_to_last_name;
                                }

                            } 
                            
                            if (assigned_to_friendly.replace(" ","").length == 0) {
                                if (response.results[i].assigned_to_email != null) {
                                    assigned_to_friendly = response.results[i].assigned_to_email;
                                }
                            }

                            button_json = '{"id": "'+response.results[i].id+'"}'

                            html+= "<tr>";
                            html+= " <td>CE"+response.results[i].id+"</td>";
                            html+= " <td>"+response.results[i].name+"</td>";
                            
                            html+= " <td>";
                            if (response.results[i].custodian_name != null) { 
                                html+= response.results[i].custodian_name;
                            } else {
                                html+= "";
                            }
                            html+= "</td>";
                            html+= " <td>"+kbcatalogue.var.catalogue_status[response.results[i].status]+"</td>";
                            html+= " <td>"+kbcatalogue.var.catalogue_Type[response.results[i].type]+"</td>";
                            html+= " <td>"+response.results[i].updated_at+"</td>";
                            html+= " <td>"+assigned_to_friendly+"</td>";
                            html+= " <td class='text-end'>";                        
                            html+="  <a class='btn btn-primary btn-sm' href='/catalogue/entries/"+response.results[i].id+"/details/'>View</a>";
                            html+="  <button class='btn btn-secondary  btn-sm'>History</button>";
                            html+="  </td>";
                            html+= "<tr>";
                        }
                                           
                        $('#publish-tbody').html(html);
                        $('.publish-table-button').hide();

                    } else {
                        $('#publish-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");
                    }

                    common_pagination.init(response.count, params, kbcatalogue.get_catalogue, $('#paging_navi'));
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
    get_catalogue_editors: function(){
        var catalogue_id = $('#catalogue_entry_id').val();
        $.ajax({
            url: kbcatalogue.var.catalogue_permission_url+"?catalogue_entry="+catalogue_id,
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                var html = '';
                
                if (response != null) {
                    if (response.length > 0) {
                        for (let i = 0; i < response.length; i++) {
                            button_json = '{"id": "'+response[i].id+'"}'

                            html+= "<tr>";
                            html+= " <td>"+response[i].id+"</td>";
                            html+= " <td>"+response[i].first_name+"</td>";
                            html+= " <td>"+response[i].last_name+"</td>";                        
                            html+= " <td>"+response[i].email+"</td>";                                                    
                            html+= " <td class='text-end'><button class='btn btn-danger btn-sm manage-editors-delete' data-json='"+button_json+"' >Delete</button></td>";
                            html+= "<tr>";
                        }
                                                                   
                        $('#manage-editors-tbody').html(html);
                        $( ".manage-editors-delete" ).click(function() {
                            console.log($(this).attr('data-json'));
                            var btndata_json = $(this).attr('data-json');
                            var btndata = JSON.parse(btndata_json);
                            kbcatalogue.delete_catalogue_editors(btndata.id);
                        });                         
                    } else {
                        $('#manage-editors-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");
                    }
                } else {
                      $('#manage-editors-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");
                }

       
            },
            error: function (error) {
                $('#manage-popup-error').text(error.responseText);
                $('#manage-popup-error').show();
                $('#manage-editors-tbody').html('');

                console.log('Error Loading manage data');
            },
        });
    },
    delete_catalogue_editors: function(permission_id) {        
        // var catalogue_id = $('#catalogue_entry_id').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();

        $.ajax({
            url: kbcatalogue.var.catalogue_permission_url+permission_id+"/",
            type: 'DELETE',
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response) {
                console.log(response);
                kbcatalogue.get_catalogue_editors();
            },
            error: function (error) {
                $('#manage-popup-error').text(error.responseText);
                $('#manage-popup-error').show();
            },
        });


    },
    add_catalogue_editor: function(user_id) {        
        var catalogue_id = $('#catalogue_entry_id').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();

        $.ajax({
            url: kbcatalogue.var.catalogue_permission_url,
            type: 'POST',
            data: JSON.stringify({'user':user_id, 'catalogue_entry':catalogue_id}),
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response) {
                console.log(response);
                kbcatalogue.get_catalogue_editors();
            },
            error: function (error) {
                $('#manage-popup-error').text(JSON.parse(error.responseText).user[0]);
                $('#manage-popup-error').show();
            },
        });
    },
}