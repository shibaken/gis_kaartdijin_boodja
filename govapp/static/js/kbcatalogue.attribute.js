var kbcatalogue_attribute = { 
    var: { 
         catalogue_attribute_url: "/api/catalogue/layers/attributes/",
    },
    init: function() {
        $( "#catalogue-attribute-limit" ).change(function() {
            console.log("Reload Catalogue Attribute");
            kbcatalogue_attribute.get_catalogue_attribute();
        });
        $( "#catalogue-attribute-order-by" ).change(function() {
            console.log("Reload Catalogue Attribute");
            kbcatalogue_attribute.get_catalogue_attribute();
        });
        $( "#catalogue-attribute-new-btn" ).click(function() {
            console.log("New Catalogue Attribute");
            kbcatalogue_attribute.init_create_att_modal();
            $('#catalogue-attribute-modal').modal('show');
        });
        $( "#catalogue-attribute-order" ).on('input',function(){
            $(this).val($(this).val().replace(/\D/g, ""));
        });
    },
    init_create_att_modal: function(){
        $( "#catalogue-attribute-submit-btn" ).text("Create");
        $( "#catalogue-attribute-modal-label" ).text("New Catalogue Attribute");
        
        $( "#catalogue-attribute-name" ).val("");
        $( "#catalogue-attribute-type" ).val("");
        $( "#catalogue-attribute-order" ).val("");

        $( "#catalogue-attribute-submit-btn" ).click(function(){
            console.log("Create New Catalogue Attribute");
            kbcatalogue_attribute.save_catalogue_attribute();
        });
    },
    set_update_att_modal: function(att){
        $( "#catalogue-attribute-submit-btn" ).text("Update");
        $( "#catalogue-attribute-modal-label" ).text("Update Catalogue Attribute");

        $( "#catalogue-attribute-name" ).val(att.name);
        $( "#catalogue-attribute-type" ).val(att.type);
        $( "#catalogue-attribute-order" ).val(att.order);

        $( "#catalogue-attribute-submit-btn" ).click(function(){
            console.log("Update Catalogue Attribute");
            kbcatalogue_attribute.update_catalogue_attribute(att.id);
        });
    },
    preprocess_catalogue_attribute: function(){
        let popup_error = $('#catalogue-attribute-popup-error');

        popup_error.html("");
        popup_error.hide();
        let show_message = function(target, message){
            target.html(message);
            target.show();
        }

        let name = $('#catalogue-attribute-name').val();
        let type = $('#catalogue-attribute-type').val();
        let order = +$('#catalogue-attribute-order').val();
        if(!name || name.length == 0){
            show_message(popup_error, "Please enter a new catalogue attribute name.");
            return false;
        }
        if(!type || type.length == 0){
            show_message(popup_error, "Please select a type.");
            return false;
        }
        if(!order || order.length == 0){
            show_message(popup_error, "Please enter a new catalogue attribute order.");
            return false;
        }
        if(isNaN(order) || order < 0){
            show_message(popup_error, "Please enter a valid new catalogue attribute order. (must be positive number)");
            return false;
        }

        $('#catalogue-attribute-name').attr('disabled','disabled');
        $('#catalogue-attribute-type').attr('disabled','disabled');
        $('#catalogue-attribute-order').attr('disabled','disabled');

        return {"name": name, "type": type, "order": +order};
    },
    save_catalogue_attribute: function() {
        var post_data = this.preprocess_catalogue_attribute();
        if(!post_data) {
            return false;
        }

        post_data["catalogue_entry"] = $('#catalogue_entry_id').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();
        
        $.ajax({
            url: kbcatalogue_attribute.var.catalogue_attribute_url,
            type: 'POST',
            headers: {'X-CSRFToken' : csrf_token},
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {
                location.reload();
            },
            error: function (error) {
                alert("ERROR occured while creating.");
            },
        });
    },
    update_catalogue_attribute: function(id) {
        var post_data = this.preprocess_catalogue_attribute();
        if(!post_data) {
            return false;
        }

        var csrf_token = $("#csrfmiddlewaretoken").val();
        
        $.ajax({
            url: kbcatalogue_attribute.var.catalogue_attribute_url+id+'/',
            type: 'PUT',
            headers: {'X-CSRFToken' : csrf_token},
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {
                location.reload();
            },
            error: function (error) {
                 alert("ERROR occured while updating.");
            },
        });
    },
    get_catalogue_attribute: function(params_str) {
        params = {
            catalogue_entry__in:       $('#catalogue_entry_id').val(),
            limit:                     $('#catalogue-attribute-limit').val(),
            order_by:                  $('#catalogue-attribute-order-by').val()
        }

        if (!params_str){
            params_str = common_pagination.make_get_params_str(params);
        }

        $.ajax({
            url: kbcatalogue.attribute.var.catalogue_attribute_url+"?"+params_str,
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                var html = '';
                
                if (response != null) {
                    if (response.results.length > 0) {
                        var update_event_handlers = {};
                        var delete_event_handlers = {};
                        for (let i = 0; i < response.results.length; i++) {
                            let att = response.results[i];
                            let btn_update_id = 'btn-update-attribute_'+i;
                            let btn_delete_id = 'btn-delete-attribute_'+i;
                            html+= "<tr>";
                            html+= " <td>"+att.id+"</td>";
                            html+= " <td>"+att.name+"</td>";
                            html+= " <td>"+att.type+"</td>";
                            html+= " <td>"+att.order+"</td>";
                            // html+= " <td class='text-end'>";                        
                            html+="  <td>";
                            html+="   <button class='btn btn-primary btn-sm' id='"+btn_update_id+"'>Update</button>";
                            html+="   <button class='btn btn-primary btn-sm' id='"+btn_delete_id+"'>Delete</button>";
                            html+="  </td>";
                            html+= "<tr>";

                            update_event_handlers[btn_update_id] = function(){
                                kbcatalogue_attribute.set_update_att_modal(att);
                                $('#catalogue-attribute-modal').modal('show');
                            };
                            delete_event_handlers[btn_delete_id] = function(){
                                $('#deleted_att').html('Id: '+att.id+'</br>Name: '+att.name+'</br>Type: '+att.type+'</br>Order: '+att.order);
                                $('#btn-delete-confirm').click(function(){
                                    kbcatalogue_attribute.delete_attribute(att.id);
                                });
                                $('#confirm-delete-att').modal('show');
                            };
                        }
                                           
                        $('#catalogue-attribute-tbody').html(html);
                        $('.publish-table-button').hide();

                        for(let id in update_event_handlers){
                            $('#'+id).click(update_event_handlers[id]);
                        }
                        for(let id in delete_event_handlers){
                            $('#'+id).click(delete_event_handlers[id]);
                        }

                        // navigation bar
                        common_pagination.init(response.count, params, kbcatalogue_attribute.get_catalogue_attribute, +params.limit, $('#paging_navi'));

                    } else {
                        $('#catalogue-attribute-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");
                    }
                } else {
                      $('#catalogue-attribute-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");
                }      
            },
            error: function (error) {
                $('#catalogue-attribute-popup-error').html("Error Loading catalogue attribute data");
                $('#catalogue-attribute-popup-error').show();
                $('#catalogue-attribute-tbody').html('');

                console.log('Error Loading catalogue attribute data');
            },
        });    


    },
    delete_attribute: function(att_id){
        $.ajax({
            url: kbcatalogue.attribute.var.catalogue_attribute_url+att_id,
            headers: {'X-CSRFToken' : $("#csrfmiddlewaretoken").val()},
            type: 'DELETE',
            success: function (response) {
                $('#confirm-delete-att').modal('hide');
                kbcatalogue_attribute.get_catalogue_attribute();
            },
            error: function (error) {
                alert("ERROR occured while deleting.");
                console.log('ERROR occured while deleting.');
            },
        });
    },
}