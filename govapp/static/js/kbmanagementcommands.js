var kbmanagementcommands = {
    var: {
        "scan_url" :"/api/management/commands/scan_dir/",
        "get_sharepoint_submission_url" :"/api/management/commands/get_sharepoint_submissions/",
    },
    run_scanner: function() {
            console.log("RUNNING SCANNER")
            $('#scanner-job-response-success').html('');
            $('#scanner-job-response-error').html('');
            var csrf_token = $("#csrfmiddlewaretoken").val();
            $('#run-scanner').attr('disabled','disabled');
            $('#run-scanner-loader').show();
            $.ajax({
                url: kbmanagementcommands.var.scan_url,
                type: 'POST',
                headers: {'X-CSRFToken' : csrf_token},
                contentType: 'application/json',
                success: function (response) {                            
                    $('#scanner-job-response-success').html("Completed");                   
                    $('#run-scanner').removeAttr('disabled');
                    $('#run-scanner-loader').hide();
                    
                },
                error: function (error) {                    
                    $('#scanner-job-response-error').html("Error running job");
                    $('#run-scanner').removeAttr('disabled');
                    $('#run-scanner-loader').hide();
                },
            });
    },
    run_sharepoint_submissions: function() {
        console.log("RUNNING SHAREPOINT COLLECTOR")
        $('#sharepoint-scanner-job-response-success').html('');
        $('#sharepoint-scanner-job-response-error').html('');
        var csrf_token = $("#csrfmiddlewaretoken").val();
        $('#run-sharepoint-scanner').attr('disabled','disabled');
        $('#run-sharepoint-scanner-loader').show();
        $.ajax({
            url: kbmanagementcommands.var.get_sharepoint_submission_url,
            type: 'POST',
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response) {                            
                $('#sharepoint-scanner-job-response-success').html("Completed");                   
                $('#run-sharepoint-scanner').removeAttr('disabled');
                $('#run-sharepoint-scanner-loader').hide();
                
            },
            error: function (error) {                    
                $('#sharepoint-scanner-job-response-error').html("Error running job");
                $('#run-sharepoint-scanner').removeAttr('disabled');
                $('#run-sharepoint-scanner-loader').hide();
            },
        });
    },
    init: function() {
        $( "#run-scanner" ).click(function() {
            console.log("Running Scanner");
            
            kbmanagementcommands.run_scanner();
        });
        $( "#run-sharepoint-scanner" ).click(function() {
            console.log("Running Scanner");
            
            kbmanagementcommands.run_sharepoint_submissions();
        });
        $('#run-scanner-loader').hide();
        $('#run-sharepoint-scanner-loader').hide();
    }

}