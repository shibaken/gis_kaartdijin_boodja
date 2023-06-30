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
            this.get_email_notification();
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
        params = {
            catalogue_id:   $('#catalogue_entry_id').val(),
            limit:          $('#catalogue-detail-notification-limit').val(),
            order_by:       $('#catalogue-detail-notification-order-by').val()
        }

        if (!params_str){
            params_str = common_pagination.make_get_params_str(params);
        }

        $.ajax({
            url: kbcatalogue_detail.var.catalogue_email_notification+'?'+params_str,
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
                    $('#'+btn_update_id).click(()=> kbcatalogue_detail.show_update_email_notification_modal(noti))
                    $('#'+btn_delete_id).click(()=> kbcatalogue_detail.show_delete_email_notification_modal(noti))
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
    show_error_modal: function(msg){
        $('#catalogue-detail-notification-popup-error').html(msg);
        $('#catalogue-detail-notification-popup-error').show();
    },

    validate_email: function (email) {
        if(!email) return false;
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        $('#catalogue-detail-notification-popup-error').hide();
        if (!emailRegex.test(email)) {
            this.show_error_modal("wrong email format.");
            return false;
        }
        return true;
    },

    validate_empty_input: function(key, val){
        if(!val){
            this.show_error_modal(key+" is required.");
            return false;
        }
        return true;
    },

    show_add_email_notification_modal: function(){
        this.show_email_notification_modal(()=>this.write_email_notification(), "Add New Email Notification");
    },

    show_update_email_notification_modal: function(prev){
        this.show_email_notification_modal(
            ()=>this.write_email_notification(prev.id), 
            "Update Email Notification",
            prev.name, prev.type, prev.email, prev.active);
    },

    show_email_notification_modal: function(submit_callback, title="", name='', type='', email='', active='true'){
        $('#catalogue-detail-notification-modal-label').html(title);
        $('#catalogue-detail-notification-name').val(name);
        $('#catalogue-detail-notification-email').val(email);
        $('#catalogue-detail-notification-active').prop('checked', active);
        
        $('#catalogue-detail-notification-type').empty();
        for(let key in this.var.catalogue_email_notification_type){
            const text = this.var.catalogue_email_notification_type[key];
            $('#catalogue-detail-notification-type').append('<option value="'+key+'">'+text+'</option>');
        }
        $('#catalogue-detail-notification-type').val(type);

        $('#catalogue-detail-notification-email').off('focusout');
        $('#catalogue-detail-notification-email').focusout(function(){
            const email = $('#catalogue-detail-notification-email').val();
            this.validate_email(email);
        });

        $('#catalogue-detail-notification-submit-btn').off('click');
        $('#catalogue-detail-notification-submit-btn').click(submit_callback);

        $('#catalogue-detail-notification-modal').modal('show');
    },

    write_email_notification: function(noti_id){
        // validation check
        const name = $('#catalogue-detail-notification-name').val();
        if (!this.validate_empty_input('name', name)) { return; }
        
        const type = $('#catalogue-detail-notification-type').val();
        if (!this.validate_empty_input('type', type)) { return; }
        
        const email = $('#catalogue-detail-notification-email').val();
        if (!this.validate_empty_input('email', email)) { return; }
        if (!this.validate_email(email)) { return; }

        const active = $('#catalogue-detail-notification-active').prop('checked');
        
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
        $.ajax({
            url: url,
            method: method,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            data: JSON.stringify(email_noti_data),
            success: function (response) {
                $('#catalogue-detail-notification-modal').modal('hide');
                kbcatalogue_detail.get_email_notification();
            },
            error: function (error) {
                alert('Error occured.');
                console.log('Error occured.'+ error);
            },
        });
    },

    show_delete_email_notification_modal: function(target){
        $('#delete_target').html('Id: '+target.id+'</br>Name: '+target.name+'</br>Type: '+target.type+'</br>Email: '+target.email+'</br>Active: '+target.active);
        $('#btn-delete-confirm').off('click');
        $('#btn-delete-confirm').click(() => kbcatalogue_detail.delete_email_notification(target.id));
        $('#confirmation-delete-modal').modal('show');
    },

    delete_email_notification: function(noti_id){
        $.ajax({
            url: kbcatalogue_detail.var.catalogue_email_notification+noti_id+"/",
            method: 'DELETE',
            contentType: 'application/json',
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            success: function (response) {
                $('#confirmation-delete-modal').modal('hide');
                kbcatalogue_detail.get_email_notification();
            },
            error: function (error) {
                alert('Error occured.');
                console.log('Error occured.'+ error);
            },
        });
    },

}