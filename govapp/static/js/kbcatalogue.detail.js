var kbcatalogue_detail = {
    var: {
        catalogue_email_notification:"/api/catalogue/notifications/emails/",
        catalogue_email_notification_type:"/api/catalogue/notifications/emails/type",
    },

    init_catalogue_detail: async function(){
        $( "#catalogue-entry-btn-save" ).click(function() {
            console.log("Save Publish Table");
            kbcatalogue_detail.save_catalogue('save');
        });

        $( "#catalogue-entry-btn-save-exit" ).click(function() {
            console.log("Save Publish Table");
            kbcatalogue_detail.save_catalogue('save-and-exit');
        });      

        $( "#catalogue-detail-btn-add-notification" ).click(function() {
            console.log("New Catalogue Email Notification");
            kbcatalogue_detail.show_add_email_notification_modal();
        });

        $('#catalogue-detail-notification-order-by').change(function(){
            common_pagination.var.current_page=0;
            kbcatalogue_detail.get_email_notification();
        });

        $('#catalogue-detail-notification-limit').change(function(){
            common_pagination.var.current_page=0;
            kbcatalogue_detail.get_email_notification();
        });

        var has_edit_access = $('#has_edit_access').val();
        if (has_edit_access == 'True') {
            this.var.has_edit_access = true;
        }
        
        await this.retrieve_noti_types();
        this.get_email_notification();
    },
    retrieve_noti_types: async function(){
        let call = () => new Promise((resolve, reject)=> $.ajax({
            url: kbcatalogue_detail.var.catalogue_email_notification_type,
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
            this.var.catalogue_email_notification_type = noti_type;
        } catch (error){
            alert("An error occured while getting email notification type.");
            console.error(error);
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
            url: kbcatalogue_detail.var.catalogue_data_url+catalogue_id+"/",            
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

    //-- for Email Notification --//
    get_email_notification: function(params_str){
        if (!params_str){
            params = {
                catalogue_id:   $('#catalogue_entry_id').val(),
                limit:          $('#catalogue-detail-notification-limit').val(),
                order_by:       $('#catalogue-detail-notification-order-by').val()
            }

            params_str = utils.make_query_params(params);
        }

        $.ajax({
            url: kbcatalogue_detail.var.catalogue_email_notification+'?'+params_str,
            method: 'GET',
            contentType: 'application/json',
            success: function (response) {
                console.log(response.results);
                // common_table.set_rows('#catalogue-detail-notification-tbody', response.results, {key:'active', type:'switch'},
                //                         buttons={Update:kbcatalogue_detail.show_update_email_notification_modal, 
                //                                 Delete:kbcatalogue_detail.show_delete_email_notification_modal});
                common_pagination.init(response.count, params, kbcatalogue_detail.get_email_notification, +params.limit, $('#notification-paging-navi'));

                $('#catalogue-detail-notification-tbody').empty();
                for(let i in response.results){
                    const noti = response.results[i];
                    const btn_update_id = 'btn-update-email-noti-'+i;
                    const btn_delete_id = 'btn-delete-email-noti-'+i;

                    // common_table.add_row(table_id, 
                    //                     [noti.id, noti,name, kbcatalogue_detail.var.catalogue_email_notification_type[noti.type], noti.email,
                    //                     {val:noti.active, type:'switch'}, 
                    //                     {type:'button', data:{Update:{id:btn_update_id, callback:kbcatalogue_detail.show_update_email_notification_modal(noti)},
                    //                                             Delete:{id:btn_update_id, callback:kbcatalogue_detail.show_update_email_notification_modal(noti)}
                    //                                         }}]);

                    var row = $('<tr>');
                    var td = $('<td>');
                    td.text(noti.id);
                    row.append(td);
                    // row.append("<td>"+noti.id+"</td>");
                    row.append("<td>"+noti.name+"</td>");
                    row.append("<td>"+kbcatalogue_detail.var.catalogue_email_notification_type[noti.type]+"</td>");
                    row.append("<td>"+noti.email+"</td>");
                    row.append("<td><div class='form-check form-switch'>"+
                                "<input class='form-check-input' type='checkbox' role='switch' "+(noti.active ? "checked" : "")+" disabled>"+
                                "</div></td>");
                    if(kbcatalogue_detail.var.has_edit_access){
                        row.append("<td>" +
                                    "<button class='btn btn-primary btn-sm' id='"+btn_update_id+"'>Update</button> " +
                                    "<button class='btn btn-primary btn-sm' id='"+btn_delete_id+"'>Delete</button>" +
                                "</td>");
                    } else {
                        row.append("<td></td>");
                    }
                    $('#catalogue-detail-notification-tbody').append(row);
                    $('#'+btn_update_id).click(()=> kbcatalogue_detail.show_update_email_notification_modal(noti));
                    $('#'+btn_delete_id).click(()=> kbcatalogue_detail.show_delete_email_notification_modal(noti));
                }
                common_pagination.init(response.count, params, kbcatalogue_detail.get_email_notification, +params.limit, $('#notification-paging-navi'));
            },
            error: function (error) {
                alert('Error occured.');
                console.log('Error occured.'+ error);
            },
        });
    },

    //-- for Email Notification modal --//
    show_add_email_notification_modal: function(){
        common_entity_modal.init("Add New Email Notification", "submit");
        let name_id = common_entity_modal.add_field(label="Name", type="text");
        let type_id = common_entity_modal.add_field(label="Type", type="select", value=null, option_map=this.var.catalogue_email_notification_type);
        let email_id = common_entity_modal.add_field(label="Email", type="email");
        let active_id = common_entity_modal.add_field(label="Active", type="switch");
        common_entity_modal.add_callbacks(submit_callback=()=> this.write_email_notification(name_id, type_id, email_id, active_id),
                                            success_callback=this.get_email_notification);
        common_entity_modal.show();
    },

    show_update_email_notification_modal: function(prev){
        common_entity_modal.init("Update Email Notification", "submit");
        let name_id = common_entity_modal.add_field(label="Name", type="text", value=prev.name);
        let type_id = common_entity_modal.add_field(label="Type", type="select", value=prev.type, option_map=this.var.catalogue_email_notification_type);
        let email_id = common_entity_modal.add_field(label="Email", type="email", value=prev.email);
        let active_id = common_entity_modal.add_field(label="Active", type="switch", value=prev.active);
        common_entity_modal.add_callbacks(submit_callback=()=> this.write_email_notification(name_id, type_id, email_id, active_id, prev.id),
                                            success_callback=this.get_email_notification);
        common_entity_modal.show();
    },
    write_email_notification: async function(name_id, type_id, email_id, active_id, noti_id){
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
            catalogue_entry:$('#catalogue_entry_id').val()
        };
        var url = this.var.catalogue_email_notification;
        var method = 'POST';
        if(noti_id){
            delete email_noti_data['catalogue_entry'];
            url += noti_id+'/';
            method = 'PUT';
        }

        // call POST API
        return await $.ajax({
            url: url,
            method: method,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            data: JSON.stringify(email_noti_data),
        });
    },

    show_delete_email_notification_modal: function(target){
        common_entity_modal.init("Delte Email Notification", "delete");
        common_entity_modal.add_field(label="Name", type="text", value=target.name);
        common_entity_modal.add_field(label="Type", type="select", value=target.type, option_map=this.var.catalogue_email_notification_type);
        common_entity_modal.add_field(label="Email", type="email", value=target.email);
        common_entity_modal.add_field(label="Active", type="switch", value=target.active);
        common_entity_modal.add_callbacks(submit_callback=()=> this.delete_email_notification(target.id),
                                            success_callback=this.get_email_notification);
        common_entity_modal.show();
    },

    delete_email_notification: async function(noti_id){
        return await $.ajax({
            url: kbcatalogue_detail.var.catalogue_email_notification+noti_id+"/",
            method: 'DELETE',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
        });
    },
}