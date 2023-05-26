var kbcatalogue = { 
    var: {
         "catalogue_data_url": "/api/catalogue/entries/",
         "catalogue_layer_symbology_url": "/api/catalogue/layers/symbologies/",
         catalogue_status: {
            1: "New Draft",
            2: "Locked",
            3: "Declined",
            4: "Draft",
            5: "Pending"
        },
        "total_pages":0,
        "offset_page":0
    },
    pagination: kbcatalogue_pagination,
    init_dashboard: function() { 
        $( "#catalogue-filter-btn" ).click(function() {
            console.log("Reload Catalogue Table");
            kbcatalogue.var.offset_page = 0;
            kbcatalogue.pagination.var.beginning_of_pagenumber = 0;
            kbcatalogue.get_catalogue();
        });
        $( "#catalogue-limit" ).change(function() {
            console.log("Reload Catalogue");
            kbcatalogue.var.offset_page = 0;
            kbcatalogue.pagination.var.beginning_of_pagenumber = 0;
            kbcatalogue.get_catalogue();
        });
        $( "#catalogue-order-by" ).change(function() {
            console.log("Reload Catalogue");
            kbcatalogue.var.offset_page = 0;
            kbcatalogue.pagination.var.beginning_of_pagenumber = 0;
            kbcatalogue.get_catalogue();
        });
        
        kbcatalogue.get_catalogue();
    },
    init_catalogue_item: function() { 
        $( "#catalogue-entry-btn-save" ).click(function() {
            console.log("Save Publish Table");
            kbcatalogue.save_catalogue('save');
        });
        $( "#catalogue-entry-btn-save-exit" ).click(function() {
            console.log("Save Publish Table");
            kbcatalogue.save_catalogue('save-and-exit');
        });      

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
        $( "#catalogue-attribute-new-btn" ).click(function() {
            console.log("New Catalogue Attribute");
            $('#NewCatalogueAttributeModal').modal('show');
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
                 alert("ERROR Changing Status");

        
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
                     alert("ERROR Setting assigned person.");
    
            
                },
            });            
        } else {
            alert('Please select an assigned to person first.')

        }

    },
    save_catalogue: function(save_status) {        
        var catalogue_id = $('#catalogue_entry_id').val();
        var cataloguename = $('#catalogue-entry-name').val();
        var cataloguecustodianentry = $('#catalogue-custodian-entry').val();
        
        var cataloguedescription = $('#catalogue-entry-description').val();
        var post_data = {"name": cataloguename, "description": cataloguedescription, "custodian": cataloguecustodianentry};
        var csrf_token = $("#csrfmiddlewaretoken").val();
        var pagetab = $('#pagetab').val();

        $.ajax({
            url: kbcatalogue.var.catalogue_data_url+catalogue_id+"/",
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
                 alert("ERROR Saving.");

        
            },
        });


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
                 alert("ERROR Saving.");

        
            },
        });


    },
    make_get_catalogue_params_str : function(params){
        var url_params = "";

        if (params){
            for (var key in params){
                url_params += "&" + key + "=" + params[key];
            }
        }

        let add_param = function(param_val, key){
            if (params && key in params){
                return;
            }
            if (param_val.length > 0) {
                url_params += "&"+key+"="+param_val;
            }
            return;
        };

        add_param($('#catalogue-name').val(), 'name__icontains');
        add_param($('#catalogue-status').val(), 'status');
        add_param($('#catalogue-description').val(), 'description__icontains');
        add_param($('#catalogue-number').val().replace("PE", ""), 'id');
        add_param($('#catalogue-limit').val(), 'limit');
        add_param($('#catalogue-order-by').val(), 'order_by');

        return url_params;
    },
    get_catalogue: function(url) {
        if (!url){
            let url_params = kbcatalogue.make_get_catalogue_params_str();
            url = kbcatalogue.var.catalogue_data_url+"?"+url_params;
        }

        $.ajax({
            url: url,
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
                            html+= " <td>CE"+response.results[i].id+"</td>";
                            html+= " <td>"+response.results[i].name+"</td>";
                            html+= " <td>NONE</td>";
                            html+= " <td>"+kbcatalogue.var.catalogue_status[response.results[i].status]+"</td>";
                            html+= " <td>"+response.results[i].updated_at+"</td>";
                            html+= " <td>"+assigned_to_friendly+"</td>";
                            html+= " <td class='text-end'>";                        
                            html+="  <a class='btn btn-primary btn-sm' href='/catalogue/entries/"+response.results[i].id+"/details/'>View</a>";
                            html+="  <button class='btn btn-primary btn-sm'>History</button>";
                            html+="  </td>";
                            html+= "<tr>";
                        }
                                           
                        $('#publish-tbody').html(html);
                        $('.publish-table-button').hide();

                        // navigation bar
                        kbcatalogue.var.total_pages = response.count / +$('#catalogue-limit').val();
                        kbcatalogue.pagination.init(kbcatalogue, response);

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
}