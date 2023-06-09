var kblayersubmission = { 
    var: {
         "layersubmission_data_url": "/api/catalogue/layers/submissions/",
         "layersubmission_symbology_url": "/api/catalogue/layers/submissions/",
    },
    init_dashboard: function() { 
        $( "#layer-submission-filter-btn" ).click(function() {
            console.log("Reload Catalogue Table");
            kblayersubmission.get_layer_submissions();
        });
        $( "#layer-submission-limit" ).change(function() {
            console.log("Reload Catalogue");
            kblayersubmission.get_layer_submissions();
        });
        $( "#layer-submission-order-by" ).change(function() {
            console.log("Reload Catalogue");
            kblayersubmission.get_layer_submissions();
        });
        kblayersubmission.get_layer_submissions();
    },    
    get_layer_submissions: function(params_str) {
        params = {
            status:        $('#layer-submission-status').val(),
        }

        if (!params_str){
            params_str = common_pagination.make_get_params_str(params);
        }

        //order_by=&limit=10" 
        $.ajax({
            url: kblayersubmission.var.layersubmission_data_url+"?"+params_str,
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
                            html+= " <td>LM"+response.results[i].id+"</td>";
                            html+= " <td>"+response.results[i].name+"</td>";
                            html+= " <td>NONE</td>";
                            html+= " <td>"+kbpublish.var.publish_status[response.results[i].status]+"</td>";
                            html+= " <td>"+response.results[i].updated_at+"</td>";
                            html+= " <td>"+assigned_to_friendly+"</td>";
                            html+= " <td class='text-end'>";
                            html+="  <a class='btn btn-primary btn-sm' href='/layer-submission/"+response.results[i].id+"'>View</a>";
                            html+="  <button class='btn btn-primary btn-sm'>History</button>";
                            html+="  </td>";
                            html+= "<tr>";
                        }
                                           
                        $('#layersubmission-tbody').html(html);
                        $('.layersubmission-table-button').hide();

                        // navigation bar
                        common_pagination.init(response.count, params, kbpublish.get_publish, +params.limit, $('#paging_navi'));

                    } else {
                        $('#layersubmission-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");

                    }
                } else {
                      $('#layersubmission-tbody').html("<tr><td colspan='7' class='text-center'>No results found<td></tr>");
                }               

       
            },
            error: function (error) {
                $('#save-layersubmission-popup-error').html("Error Loading publish data");
                $('#save-layersubmission-popup-error').show();
                $('#save-layersubmission-tbody').html('');

                console.log('Error Loading publish data');
            },
        });    
    }
}