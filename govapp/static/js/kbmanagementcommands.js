var kbmanagementcommands = {
    var: {
        "scan_url" :"/api/management/commands/scan/",
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
                    $('#scanner-job-response-success').html("Successfully Completed");                   
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
    init: function() {
        $( "#run-scanner" ).click(function() {
            console.log("Running Scanner");
            
            kbmanagementcommands.run_scanner();
        });
        $('#run-scanner-loader').hide();
    }

}