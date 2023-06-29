var kbcatalogue = { 
    var: {
         "catalogue_data_url": "/api/catalogue/entries/",
         "catalogue_layer_symbology_url": "/api/catalogue/layers/symbologies/",
         "catalogue_email_notification":"/api/catalogue/notifications/emails/",
         "catalogue_email_notification_type":"/api/catalogue/notifications/emails/type",
         catalogue_status: {
            1: "New Draft",
            2: "Locked",
            3: "Declined",
            4: "Draft",
            5: "Pending"
        },
    },
    attribute: kbcatalogue_attribute,
    init_dashboard: function() { 
        $( "#catalogue-filter-btn" ).click(function() {
            console.log("Reload Catalogue Table");
            kbcatalogue.get_catalogue();
        });
        $( "#catalogue-limit" ).change(function() {
            console.log("Reload Catalogue");
            kbcatalogue.get_catalogue();
        });
        $( "#catalogue-order-by" ).change(function() {
            console.log("Reload Catalogue");
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
    },
    init_catalogue_detail: async function(){
        $( "#catalogue-detail-btn-add-notification" ).click(function() {
            console.log("New Catalogue Email Notification");
            kbcatalogue.show_add_email_notification_modal();
        });

        $('#catalogue-detail-notification-order-by').change(function(){
            kbcatalogue.get_email_notification();
        });

        $('#catalogue-detail-notification-limit').change(function(){
            kbcatalogue.get_email_notification();
        });

        var has_edit_access = $('#has_edit_access').val();
        if (has_edit_access == 'True') {
            kbcatalogue.var.has_edit_access = true;
        }
        
        let call = () => new Promise((resolve, reject)=> $.ajax({
            url: kbcatalogue.var.catalogue_email_notification_type,
            type: 'GET',
            contentType: 'application/json',
            success: (response) => {resolve(response);},
            error: (xhr, status, error) => {reject(error);},
        }));

        try{
            const response = await call();
            var noti_type = {}
            for(let i in response.results){
                const type = response.results[i];
                noti_type[type.id] = type.label;
            }
            kbcatalogue.var.catalogue_email_notification_type = noti_type;
            kbcatalogue.get_email_notification();
        } catch (error){
            alert("An error occured while getting email notification type.");
            console.error(error);
        }

        
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
            type: 'PUT',
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
    get_catalogue: function(params_str) {
        params = {
            name__icontains:        $('#catalogue-name').val(),
            status:                 $('#catalogue-status').val(),
            description__icontains: $('#catalogue-description').val(),
            id:                     $('#catalogue-number').val().replace("PE", ""),
            limit:                  $('#catalogue-limit').val(),
            order_by:               $('#catalogue-order-by').val()
        }

        if (!params_str){
            params_str = common_pagination.make_get_params_str(params);
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
                            if (response.results[i].first_name != null) {

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
                        common_pagination.init(response.count, params, kbcatalogue.get_catalogue, +params.limit, $('#paging_navi'));

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
    //-- for Email Notification --//
    get_email_notification: function(params_str){
        params = {
            catalogue_id:   $('#catalogue_entry_id').val(),
            limit:          $('#catalogue-detail-notification-limit').val(),
            order_by:       $('#catalogue-detail-notification-order-by').val()
        }

        if (!params_str){
            params_str = common_pagination.make_get_params_str(params);
        }

        $.ajax({
            url: kbcatalogue.var.catalogue_email_notification+'?'+params_str,
            method: 'GET',
            contentType: 'application/json',
            success: function (response) {
                console.log(response.results);
                $('#catalogue-detail-notification-tbody').empty();
                for(let i in response.results){
                    const noti = response.results[i];
                    const btn_update_id = 'btn-update-email-noti-'+i;
                    const btn_delete_id = 'btn-delete-email-noti-'+i;
                    var row = $('<tr>');
                    row.append("<td>"+noti.id+"</td>");
                    row.append("<td>"+noti.name+"</td>");
                    row.append("<td>"+kbcatalogue.var.catalogue_email_notification_type[noti.type]+"</td>");
                    row.append("<td>"+noti.email+"</td>");
                    if(kbcatalogue.var.has_edit_access){
                        row.append("<td>" +
                                    " <button class='btn btn-primary btn-sm' id='"+btn_update_id+"'>Update</button>" +
                                    " <button class='btn btn-primary btn-sm' id='"+btn_delete_id+"'>Disable</button>" +
                                "</td>");
                    } else {
                        row.append("<td></td>");
                    }
                    $('#catalogue-detail-notification-tbody').append(row);
                    $('#'+btn_update_id).click(()=> kbcatalogue.show_update_email_notification_modal(noti))
                }
                // navigation bar
                common_pagination.init(response.count, params, kbcatalogue.get_email_notification, +params.limit, $('#notification-paging-navi'));
            },
            error: function (error) {
                alert('Error occured.');
                console.log('Error occured.'+ error);
            },
        });
    },
    //-- for Email Notification modal --//
    show_error_modal: function(msg){
        $('#catalogue-detail-notification-popup-error').html(msg);
        $('#catalogue-detail-notification-popup-error').show();
    },
    validate_email: function (email) {
        if(!email) return false;
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        $('#catalogue-detail-notification-popup-error').hide();
        if (!emailRegex.test(email)) {
            kbcatalogue.show_error_modal("wrong email format.");
            return false;
        }
        return true;
    },
    validate_empty_input: function(key, val){
        if(!val){
            kbcatalogue.show_error_modal(key+" is required.");
            return false;
        }
        return true;
    },
    show_add_email_notification_modal: function(){
        kbcatalogue.show_email_notification_modal(()=>kbcatalogue.write_email_notification(), "Add New Email Notification");
    },
    show_update_email_notification_modal: function(prev){
        kbcatalogue.show_email_notification_modal(
            ()=>kbcatalogue.write_email_notification(prev.id), 
            "Update Email Notification",
            prev.name, prev.type, prev.email);
    },
    show_email_notification_modal: function(submit_callback, title="", name='', type='', email=''){
        $('#catalogue-detail-notification-modal-label').html(title);
        $('#catalogue-detail-notification-name').val(name);
        $('#catalogue-detail-notification-type').val(type);
        $('#catalogue-detail-notification-email').val(email);

        $('#catalogue-detail-notification-type').empty();
        for(let key in kbcatalogue.var.catalogue_email_notification_type){
            const text = kbcatalogue.var.catalogue_email_notification_type[key];
            $('#catalogue-detail-notification-type').append('<option value="'+key+'">'+text+'</option>');
        }

        $('#catalogue-detail-notification-email').off('focusout');
        $('#catalogue-detail-notification-email').focusout(function(){
            const email = $('#catalogue-detail-notification-email').val();
            kbcatalogue.validate_email(email);
        });

        $('#catalogue-detail-notification-submit-btn').off('click');
        $('#catalogue-detail-notification-submit-btn').click(submit_callback);

        $('#catalogue-detail-notification-modal').modal('show');
    },
    write_email_notification: function(noti_id){
        // validation check
        const name = $('#catalogue-detail-notification-name').val();
        if (!kbcatalogue.validate_empty_input('name', name)) { return; }
        
        const type = $('#catalogue-detail-notification-type').val();
        if (!kbcatalogue.validate_empty_input('type', type)) { return; }
        
        const email = $('#catalogue-detail-notification-email').val();
        if (!kbcatalogue.validate_empty_input('email', email)) { return; }
        if (!kbcatalogue.validate_email(email)) { return; }
        
        // make data body
        var email_noti_data = {
            name:name,
            type:type,
            email:email,
            catalogue_entry:$('#catalogue_entry_id').val()
        };
        var url = kbcatalogue.var.catalogue_email_notification;
        var method = 'POST';
        if(noti_id){
            delete email_noti_data['catalogue_entry'];
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
            success: function (response) {
                $('#catalogue-detail-notification-modal').modal('hide');
                kbcatalogue.get_email_notification();
            },
            error: function (error) {
                alert('Error occured.');
                console.log('Error occured.'+ error);
            },
        });
    }
}