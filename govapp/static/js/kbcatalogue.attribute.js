var kbcatalogue_attribute = { 
    var: { 
         catalogue_attribute_url: "/api/catalogue/layers/attributes/",
    },
    init: function() {
        alert('test');
    },
    save_catalogue_attribute: function() {
        kbcatalogue.attribute.var.catalogue_attribute_url
        // Example code
        var catalogue_id = $('#catalogue_entry_id').val();
        var cataloguename = $('#catalogue-entry-name').val();
        var cataloguecustodianentry = $('#catalogue-custodian-entry').val();
        var cataloguedescription = $('#catalogue-entry-description').val();


        var post_data = {"name": cataloguename, "description": cataloguedescription, "custodian": cataloguecustodianentry};
        var csrf_token = $("#csrfmiddlewaretoken").val();
        var pagetab = $('#pagetab').val();

        $.ajax({
            url: kbcatalogue.attribute.var.catalogue_attribute_url+catalogue_id+"/",            
            type: 'PUT',
            headers: {'X-CSRFToken' : csrf_token},
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {
                kbcatalogue.attribute.var.get_catalogue_attribute();            
            },
            error: function (error) {
                 alert("ERROR Saving.");

        
            },
        });



    },
    get_catalogue_attribute: function() {


        params_str ={}
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
                            html+= " <td>"+response.results[i].id+"</td>";
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
                                           
                        $('#catalogue-attribute-tbody').html(html);
                        $('.publish-table-button').hide();

                        // navigation bar
                        common_pagination.init(response.count, params, kbcatalogue.get_catalogue, +params.limit, $('#paging_navi'));

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