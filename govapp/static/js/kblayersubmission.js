var kblayersubmission = { 
    var: {
         "layersubmission_data_url": "/api/catalogue/layers/submissions/",
         "layersubmission_symbology_url": "/api/catalogue/layers/submissions/",
    },
    init_dashboard: function() { 
        $( "#layer-submission-filter-btn" ).click(function() {
            kblayersubmission.get_layer_submissions();
        });
        $( "#layer-submission-limit" ).change(function() {
            kblayersubmission.get_layer_submissions();
        });
        $( "#layer-submission-order-by" ).change(function() {
            kblayersubmission.get_layer_submissions();
        });
        $( "#layer-submission-status" ).change(function() {
            kblayersubmission.get_layer_submissions();
        });
        kblayersubmission.get_layer_submissions();
    },    
    get_layer_submissions: function(params_str) {
        console.log("Reload layer submission page.");
        params = {
            status:        $('#layer-submission-status').val(),
            limit:         $('#layer-submission-limit').val(),
            order_by:      $('#layer-submission-order-by').val(),
        }

        if (!params_str){
            params_str = common_pagination.make_get_params_str(params);
        }

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

                            const date = new Date(response.results[i].submitted_at);
                            const year = date.getFullYear();
                            const month = String(date.getMonth() + 1).padStart(2, '0');
                            const day = String(date.getDate()).padStart(2, '0');
                            const hours = String(date.getHours()).padStart(2, '0');
                            const minutes = String(date.getMinutes()).padStart(2, '0');
                            const seconds = String(date.getSeconds()).padStart(2, '0');
                            
                            const formattedDate = `${day}-${month}-${year} ${hours}:${minutes}:${seconds}`;

                            button_json = '{"id": "'+response.results[i].id+'"}'

                            // Number, Name, Submitted Date, Time, Catalogue, Status, Action
                            html+= "<tr>";
                            html+= " <td>LM"+response.results[i].id+"</td>";
                            html+= " <td>"+response.results[i].name+"</td>";
                            html+= " <td>"+formattedDate+"</td>";
                            html+= " <td>CE"+response.results[i].catalogue_entry+"</td>";
                            html+= " <td>"+response.results[i].status_name+"</td>";
                            html+= " <td class='text-end'>";
                            html+="  <a class='btn btn-primary btn-sm' href='/layer-submission/"+response.results[i].id+"'>View</a>";
                            html+="  </td>";
                            html+= "<tr>";
                        }

                        $('#layersubmission-tbody').html(html);
                        $('.layersubmission-table-button').hide();

                        // navigation bar
                        common_pagination.init(response.count, params, kblayersubmission.get_layer_submissions, +params.limit, $('#paging_navi'));

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