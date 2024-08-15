var kbcatalogue = { 
    var: {
         catalogue_data_url: "/api/catalogue/entries/",
         catalogue_permission_url: "/api/catalogue/permission/",
         catalogue_layer_symbology_url: "/api/catalogue/layers/symbologies/",
         catalogue_status: {
            1: {"name": "New Draft", "colour": "darkgray", "class": "badge bg-secondary"},
            2: {"name": "Locked", "colour": "green", "class": "badge bg-success"},
            3: {"name": "Declined", "colour": "darkgray", "class": "badge bg-danger"},
            4: {"name": "Draft", "colour": "darkgray", "class": "badge bg-secondary"},
            5: {"name": "Pending", "colour": "darkgray", "class": "badge bg-warning"}
        },
        spatial_type: {
            1: "Special File",
            2: "Subscription WFS",
            3: "Subscription WMS",
            4: "Subscription PostGIS",
            5: "Custom Query"
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

        utils.enter_keyup($('#catalogue-name'), kbcatalogue.get_catalogue);
        utils.enter_keyup($('#catalogue-description'), kbcatalogue.get_catalogue);
        utils.enter_keyup($('#catalogue-number'), kbcatalogue.get_catalogue);
        
        kbcatalogue.get_catalogue();
        
        // *** Upload Catalogue ***
        // Show modal
        $( "#upload-catalogue-btn" ).click(function() {
            $('#modal_upload_catalogue').modal('show');
        });
        // Start uploading
        $("#fileInput").change(function(){
            var files = $("#fileInput")[0].files;
            // for (var i = 0; i < files.length; i++) {
                // Show progress bar
                // $("#progressBars").append('<div class="progress mt-2"><div class="progress-bar" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div></div>');
            // }
            kbcatalogue.uploadFiles(files);
        });
        // Select by drag-and-drop
        $("#modalContent").on('dragover', function(event) {
            event.preventDefault();
            $("#modalContent").addClass('dragover');
        });
        $("#modalContent").on('dragleave drop', function(event) {
            event.preventDefault();
            $("#modalContent").removeClass('dragover');
        });
        $("#modalContent").on('drop', function(event) {
            event.preventDefault();
            $("#modalContent").removeClass('dragover');
            var files = event.originalEvent.dataTransfer.files;
            kbcatalogue.uploadFiles(files);
        });
        $("#cancel_upload_catalogue_btn").on('click', function(event){
            kbcatalogue.cancelUploadCatalogue();
        }),
        $("#submit_upload_catalogue_btn").on('click', function(event){
            kbcatalogue.submitUploadCatalogue();
        })
        $('#modal_upload_catalogue').on('hidden.bs.modal', function (e) {
            kbcatalogue.modalClosed()
          });
    },

    init_catalogue_item: function() { 
        $( "#catalogue-entry-symbology-btn-save" ).click(function() {
            kbcatalogue.save_symbology('save');
        });
        $( "#ccatalogue-entry-symbology-btn-save-exit" ).click(function() {
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
                        text: `${item.first_name} ${item.last_name} (${item.email})`
                      });
                    });
                    return {
                        results: results
                    };
                }
            },
        };

        $( "#catalogue-manage-editors-btn" ).click(function(){
            kbcatalogue.get_catalogue_entry_permissions();
            $('#manage-editors-search').val("").trigger('change');
            $('#manage-popup-error').hide();
            $('#ManageEditorsModal').modal('show');
        });

        $( '#catalogue-show-permission-btn' ).click(function(){
            kbcatalogue.get_catalogue_entry_permissions(false);
            $('#manage-editors-add-area').hide();
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
            type: 'PUT',
            headers: {'X-CSRFToken' : csrf_token},
            data: post_data,
            success: function (response) {
                console.log({response})
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

    addDateTimeToFilename: function(filename) {
        // Get current date and time
        const currentDate = new Date();
    
        // Format date
        const year = currentDate.getFullYear();
        const month = String(currentDate.getMonth() + 1).padStart(2, '0'); // Pad month with leading zero
        const day = String(currentDate.getDate()).padStart(2, '0'); // Pad day with leading zero
        const hours = String(currentDate.getHours()).padStart(2, '0'); // Pad hours with leading zero
        const minutes = String(currentDate.getMinutes()).padStart(2, '0'); // Pad minutes with leading zero
        const seconds = String(currentDate.getSeconds()).padStart(2, '0'); // Pad seconds with leading zero
    
        // Insert date and time between filename and extension
        const extensionIndex = filename.lastIndexOf('.');
        const newFilename = filename.slice(0, extensionIndex) + '.' + year + month + day + '_' + hours + minutes + seconds + filename.slice(extensionIndex);
    
        return newFilename;
    },

    createProgressBar: function(fileName, newFileName) {
        console.log('creating progress bar')
        var progressBarContainer = $('<div class="progress-container mt-2"></div>');
        var progressBarRow = $('<div class="row  d-flex align-items-center"></div>');
        var fileNameColumn = $('<div class="col-6"></div>');
        // var progressBarColumn = $('<div class="col-5"></div>');
        var progressBarColumn = $('<div class="col-4"></div>');
        var progressBarTextColumn = $('<div class="col-1"><span class="progress-text"></span></div>');
        var deleteIconColumn = $('<div class="col-1"></div>');
    
        var progressBar = $('<div class="progress"><div class="progress-bar" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div></div>');
        var fileNameElement = $('<div class="file-name">' + fileName + '</div>');
        var deleteIcon = $('<span class="delete-icon" data-newFileName="' + newFileName + '"><svg width="24" height="24" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 12L12 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M12 12L4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></span>')
    
        fileNameColumn.append(fileNameElement);
        progressBarColumn.append(progressBar);
        deleteIconColumn.append(deleteIcon);
    
        progressBarRow.append(fileNameColumn);
        progressBarRow.append(progressBarTextColumn);
        progressBarRow.append(progressBarColumn);
        progressBarRow.append(deleteIconColumn);
    
        progressBarContainer.append(progressBarRow);
    
        return {
            progressBar: progressBar,
            progressBarContainer: progressBarContainer,
            deleteIcon: deleteIcon
        };
    },
    
    deleteFile: function(fileName) {
        // Make an AJAX request to delete the file
        var csrf_token = $("#csrfmiddlewaretoken").val();
        var xhr = $.ajax({
            url: kbcatalogue.var.catalogue_data_url + "delete_file/", // Change the URL to your delete file endpoint
            type: 'POST',
            headers: {'X-CSRFToken' : csrf_token}, // Include CSRF token in headers
            data: {'newFileName': fileName},
            success: function(data){

            },
            error: function(xhr, status, error) {
                console.error("Error deleting file:", error);
            }
        });
    },
    modalClosed: function(){
        kbcatalogue.cancelUploadCatalogue();
    },
    submitUploadCatalogue: function(){
        var progressBarContainer = $('#progressBars')
        progressBarContainer.empty();
    },
    cancelUploadCatalogue: function(){
        $(".cross-sign").each(function() {
            var newFilename = $(this).data("newfilename");
            kbcatalogue.deleteFile(newFilename);
        });
        var progressBarContainer = $('#progressBars')
        progressBarContainer.empty();
    },

    // Function for uploading files
    uploadFiles: function(files) {
        var xhrList = []
        var csrf_token = $("#csrfmiddlewaretoken").val();
    
        for (var i = 0; i < files.length; i++) {
            var fileName = files[i].name;
            var newFileName = kbcatalogue.addDateTimeToFilename(fileName)
    
            // Generate progressbar per file
            var { progressBar, progressBarContainer, deleteIcon } = kbcatalogue.createProgressBar(fileName, newFileName);
            $("#progressBars").append(progressBarContainer);
            
            (function(index, progressBar, progressBarContainer) {
                var formData = new FormData();
                formData.append('file', files[index]);
                formData.append('newFileName', newFileName)
    
                // Delete 
                deleteIcon.on('click', function() {
                    // Abort uploading
                    if (xhrList[index] && xhrList[index].readyState !== 4) {
                        xhrList[index].abort();
                    }
                    // Delete uploaded file from the server
                    else {
                        var newFileName = $(this).attr("data-newfilename");
                        kbcatalogue.deleteFile(newFileName)
                    }
                    // Delete progressbar
                    progressBarContainer.fadeOut('slow', function(){
                        $(this).remove();
                    })
                });
    
                // Upload
                var xhr = $.ajax({
                    url: kbcatalogue.var.catalogue_data_url + "upload_file/",
                    type: 'POST',
                    headers: {'X-CSRFToken' : csrf_token},
                    data: formData,
                    cache: false,
                    contentType: false,
                    processData: false,
                    xhr: function() {
                        var xhr = new window.XMLHttpRequest();
                        xhr.upload.addEventListener("progress", function(evt) {
                            if (evt.lengthComputable) {
                                var percentComplete = (evt.loaded / evt.total) * 100;
                                // Update progressbar
                                progressBar.find(".progress-bar").width(percentComplete + '%');
                                progressBar.find(".progress-bar").attr('aria-valuenow', percentComplete);
                                // Display percentage text
                                progressBarContainer.find(".progress-text").text(percentComplete.toFixed(0) + '%');
                            }
                        }, false);
                        return xhr;
                    },
                    success: function(response){

                    },
                    error: function(xhr, status, error){
                        var errorResponse = JSON.parse(xhr.responseText);
                        progressBar.fadeOut('slow', function(){
                            progressBar.replaceWith($('<span class="error-message">' + errorResponse.error + '</span>'))
                        });
                    }
                });
                xhrList.push(xhr);
            })(i, progressBar, progressBarContainer);
        }
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
                limit:                  $('#catalogue-limit').val(),
                order_by:               $('#catalogue-order-by').val(),
                type_in:                   "1,5"
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
                            let catalogue_entry = response.results[i]
                            console.log(catalogue_entry)
                            assigned_to_friendly = "";

                            if (catalogue_entry.assigned_to_first_name != null) {
                                assigned_to_friendly = catalogue_entry.assigned_to_first_name;
                                if (catalogue_entry.assigned_to_last_name != null) {
                                    assigned_to_friendly += " "+catalogue_entry.assigned_to_last_name;
                                }
                            } 
                            
                            if (assigned_to_friendly.replace(" ","").length == 0) {
                                if (catalogue_entry.assigned_to_email != null) {
                                    assigned_to_friendly = catalogue_entry.assigned_to_email;
                                }
                            }

                            button_json = '{"id": "'+catalogue_entry.id+'"}'
                            let restricted_icon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="16" height="16" style="fill: gray;"><!--!Font Awesome Free 6.6.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path d="M367.2 412.5L99.5 144.8C77.1 176.1 64 214.5 64 256c0 106 86 192 192 192c41.5 0 79.9-13.1 111.2-35.5zm45.3-45.3C434.9 335.9 448 297.5 448 256c0-106-86-192-192-192c-41.5 0-79.9 13.1-111.2 35.5L412.5 367.2zM0 256a256 256 0 1 1 512 0A256 256 0 1 1 0 256z"/></svg>'
                            let public_icon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="16" height="16" style="fill: gray;"><path d="M352 256c0 22.2-1.2 43.6-3.3 64l-185.3 0c-2.2-20.4-3.3-41.8-3.3-64s1.2-43.6 3.3-64l185.3 0c2.2 20.4 3.3 41.8 3.3 64zm28.8-64l123.1 0c5.3 20.5 8.1 41.9 8.1 64s-2.8 43.5-8.1 64l-123.1 0c2.1-20.6 3.2-42 3.2-64s-1.1-43.4-3.2-64zm112.6-32l-116.7 0c-10-63.9-29.8-117.4-55.3-151.6c78.3 20.7 142 77.5 171.9 151.6zm-149.1 0l-176.6 0c6.1-36.4 15.5-68.6 27-94.7c10.5-23.6 22.2-40.7 33.5-51.5C239.4 3.2 248.7 0 256 0s16.6 3.2 27.8 13.8c11.3 10.8 23 27.9 33.5 51.5c11.6 26 20.9 58.2 27 94.7zm-209 0L18.6 160C48.6 85.9 112.2 29.1 190.6 8.4C165.1 42.6 145.3 96.1 135.3 160zM8.1 192l123.1 0c-2.1 20.6-3.2 42-3.2 64s1.1 43.4 3.2 64L8.1 320C2.8 299.5 0 278.1 0 256s2.8-43.5 8.1-64zM194.7 446.6c-11.6-26-20.9-58.2-27-94.6l176.6 0c-6.1 36.4-15.5 68.6-27 94.6c-10.5 23.6-22.2 40.7-33.5 51.5C272.6 508.8 263.3 512 256 512s-16.6-3.2-27.8-13.8c-11.3-10.8-23-27.9-33.5-51.5zM135.3 352c10 63.9 29.8 117.4 55.3 151.6C112.2 482.9 48.6 426.1 18.6 352l116.7 0zm358.1 0c-30 74.1-93.6 130.9-171.9 151.6c25.5-34.2 45.2-87.7 55.3-151.6l116.7 0z"/></svg>'
                            html += "<tr>";
                            html += "<td>CE" + catalogue_entry.id + "</td>";
                            html += "<td>" + catalogue_entry.name + "</td>";
                            html += "<td>" + kbcatalogue.var.spatial_type[catalogue_entry.type] + "</td>";
                            html += "<td>" + (catalogue_entry.permission_type == 1 ? public_icon + ' ' + catalogue_entry.permission_type_str: restricted_icon + ' ' + catalogue_entry.permission_type_str) + "</td>"
                            // html += "<td>" + catalogue_entry.permission_type_str + "</td>"
                            html += "<td>" + (catalogue_entry.custodian_name != null ? catalogue_entry.custodian_name : "") + "</td>"
                            html += "<td><span class='" + kbcatalogue.var.catalogue_status[catalogue_entry.status].class + "'>" + kbcatalogue.var.catalogue_status[catalogue_entry.status].name + "<span></td>";
                            html += "<td>" + catalogue_entry.updated_at + "</td>";
                            html += "<td>" + assigned_to_friendly + "</td>";
                            html += "<td class='text-end'>";
                            html += "<a class='btn btn-primary btn-sm' href='/catalogue/entries/" + catalogue_entry.id + "/details/'>View</a>";
                            html += "<button class='btn btn-secondary btn-sm ml-1'>History</button>";
                            html += "</td>";
                            html += "<tr>";
                        }

                        $('#publish-tbody').html(html);
                        $('.publish-table-button').hide();

                    } else {
                        $('#publish-tbody').html("<tr><td colspan='8' class='text-center'>No results found</td></tr>");
                    }

                    common_pagination.init(response.count, params, kbcatalogue.get_catalogue, $('#paging_navi'));
                } else {
                      $('#publish-tbody').html("<tr><td colspan='8' class='text-center'>No results found</td></tr>");
                }

                $( ".publish-to-geoserver-btn" ).click(function() {
                    var btndata_json = $(this).attr('data-json');
                    var btndata = JSON.parse(btndata_json);

                    kbpublish.publish_to_geoserver(btndata.id);
                });     
                
                $( ".publish-to-cddp-btn" ).click(function() {
                    var btndata_json = $(this).attr('data-json');
                    var btndata = JSON.parse(btndata_json);
                    kbpublish.publish_to_cddp(btndata.id);
                });                    
            },
            error: function (error) {
                $('#save-publish-popup-error').html("Error Loading publish data");
                $('#save-publish-popup-error').show();
                $('#save-publish-tbody').html('');
            },
        });    
    },
    get_catalogue_entry_permissions: function(permissioned=true){
        var catalogue_id = $('#catalogue_entry_id').val();
        $.ajax({
            url: kbcatalogue.var.catalogue_permission_url + "?catalogue_entry=" + catalogue_id,
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            success: function (response) {
                if (response != null && response.length > 0) {
                    $('#manage-editors-tbody').empty();
                    for (let i = 0; i < response.length; i++) {
                        let catalogue_entry_permission = response[i]
                        button_json = '{"id": "' + catalogue_entry_permission.id + '"}'

                        let tr_elem = $('<tr>')
                        tr_elem.append($('<td>').text(catalogue_entry_permission.id))
                        tr_elem.append($('<td>').text(catalogue_entry_permission.first_name))
                        tr_elem.append($('<td>').text(catalogue_entry_permission.last_name))
                        tr_elem.append($('<td>').text(catalogue_entry_permission.email))
                        tr_elem.append($('<td class="text-center">').append(catalogue_entry_permission.active ? '<img src="/static/admin/img/icon-yes.svg" alt="True">' : '<img src="/static/admin/img/icon-no.svg" alt="False">'))
                        tr_elem.append($('<td>').text(catalogue_entry_permission.access_permission_label))
                        tr_elem.append(permissioned ? $(`<td class='text-center'><button class='btn btn-danger btn-sm manage-editors-delete' data-json='${button_json}'>Delete</button></td>`) : $('<td>'))
                        $('#manage-editors-tbody').append(tr_elem);
                    }

                    $(".manage-editors-delete").click(function() {
                        console.log($(this).attr('data-json'));
                        var btndata_json = $(this).attr('data-json');
                        var btndata = JSON.parse(btndata_json);
                        kbcatalogue.delete_catalogue_editors(btndata.id);
                    });
                } else {
                      $('#manage-editors-tbody').html("<tr><td colspan='7' class='text-center'>No results found</td></tr>");
                }
            },
            error: function (error) {
                $('#manage-popup-error').text(error.responseText);
                $('#manage-popup-error').show();
                $('#manage-editors-tbody').html('');
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
                kbcatalogue.get_catalogue_entry_permissions();
            },
            error: function (error) {
                $('#manage-popup-error').text(error.responseText);
                $('#manage-popup-error').show();
            },
        });


    },
    add_catalogue_editor: function(user_id) {        
        var catalogue_id = $('#catalogue_entry_id').val();
        var user_access_permission_value = $('#user-access-permission').val();
        var csrf_token = $("#csrfmiddlewaretoken").val();

        $.ajax({
            url: kbcatalogue.var.catalogue_permission_url,
            type: 'POST',
            data: JSON.stringify({
                'user':user_id,
                'catalogue_entry':catalogue_id,
                'access_permission': user_access_permission_value
            }),
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response) {
                console.log(response);
                kbcatalogue.get_catalogue_entry_permissions();
            },
            error: function (error) {
                $('#manage-popup-error').text(JSON.parse(error.responseText).user[0]);
                $('#manage-popup-error').show();
            },
        });
    },
}