var kbcatalogue_attribute = { 
    var: { 
         catalogue_attribute_url: "/api/catalogue/layers/attributes/",
    },
    init: function() {
        $( "#create-catalogue-attribute-btn" ).click(function(){
            console.log("Create New Catalogue Attribute");
            kbcatalogue_attribute.save_catalogue_attribute();
        });
        $( "#catalogue-attribute-limit" ).change(function() {
            console.log("Reload Catalogue Attribute");
            kbcatalogue_attribute.get_catalogue_attribute();
        });
        $( "#catalogue-attribute-order-by" ).change(function() {
            console.log("Reload Catalogue Attribute");
            kbcatalogue_attribute.get_catalogue_attribute();
        });
    },
    save_catalogue_attribute: function() {
        let popup_error = $('#new-catalogue-attribute-popup-error');
        let popup_success = $('#new-catalogue-attribute-popup-success');

        popup_error.html("");
        popup_error.hide();
        popup_success.html("");
        popup_success.hide();
        let show_message = function(target, message){
            target.html(message);
            target.show();
        }

        let name = $('#new-catalogue-attribute-name').val();
        let type = $('#new-catalogue-attribute-type').val();
        let order = $('#new-catalogue-attribute-order').val();
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
        if(isNaN(order)){
            show_message(popup_error, "Please enter a valid new catalogue attribute order. (must be positive number)");
            return false;
        }

        $('#new-catalogue-attribute-name').attr('disabled','disabled');
        $('#new-catalogue-attribute-type').attr('disabled','disabled');
        $('#new-catalogue-attribute-order').attr('disabled','disabled');

        var catalogue_entry_id = $('#catalogue_entry_id').val();
        var post_data = {"name": name, "type": type, "order": +order, "catalogue_entry":catalogue_entry_id};
        var csrf_token = $("#csrfmiddlewaretoken").val();
        

        $.ajax({
            url: kbcatalogue.var.catalogue_layer_attribute_url,
            //method: 'POST',
            type: 'POST',
            //dataType: 'json',
            headers: {'X-CSRFToken' : csrf_token},
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {

                // if (save_status == 'save-and-exit') {
                //     window.location = '/publish/';
                // } else {
                //    window.location = "/publish/"+publish_id;
                // }

                location.reload();
            },
            error: function (error) {
                 alert("ERROR Saving.");

        
            },
        });
    },
    get_catalogue_attribute: function(params_str) {
        params = {
            catalogue_entry__in:       $('#catalogue_entry_id').val(),
            // name__icontains:        $('#catalogue-name').val(),
            // status:                 $('#catalogue-status').val(),
            // description__icontains: $('#catalogue-description').val(),
            // id:                     $('#catalogue-number').val().replace("PE", ""),
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
                        for (let i = 0; i < response.results.length; i++) {
                            let att = response.results[i];
                            html+= "<tr>";
                            html+= " <td>"+att.id+"</td>";
                            html+= " <td>"+att.name+"</td>";
                            html+= " <td>"+att.type+"</td>";
                            html+= " <td>"+att.order+"</td>";
                            // html+= " <td class='text-end'>";                        
                            html+="  <td><a class='btn btn-primary btn-sm' href='/catalogue/entries/"+1+"/details/'>View</a>";
                            html+="  <button class='btn btn-primary btn-sm'>History</button>";
                            html+="  </td>";
                            html+= "<tr>";
                        }
                                           
                        $('#catalogue-attribute-tbody').html(html);
                        $('.publish-table-button').hide();

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
                $('#save-catalogue-attribute-popup-error').html("Error Loading publish data");
                $('#save-catalogue-attribute-popup-error').show();
                $('#save-catalogue-attribute-tbody').html('');

                console.log('Error Loading publish data');
            },
        });    


    }

}