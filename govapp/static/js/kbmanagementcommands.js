var kbmanagementcommands = {
    var: {
        "scan_url" :"/api/management/commands/scan_dir/",
        "get_sharepoint_submission_url" :"/api/management/commands/get_sharepoint_submissions/",
        "geoserver_queue_cron_job" :"/api/management/commands/excute_geoserver_queue/",
        "geoserver_queue_sync_job" : "/api/management/commands/excute_geoserver_sync/",
    },
    run_scanner: function() {
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
    run_geoserver_queue_cron_job: function() {
        console.log("RUNNING GEOSERVER QUEUE CRON JOB")
        $('#geoserver-queue-job-response-success').html('');
        $('#geoserver-queue-job-response-error').html('');
        var csrf_token = $("#csrfmiddlewaretoken").val();
        $('#run-geoserver-queue').attr('disabled','disabled');
        $('#run-geoserver-queue-loader').show();
        $.ajax({
            url: kbmanagementcommands.var.geoserver_queue_cron_job,
            type: 'POST',
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response) {                            
                $('#geoserver-queue-job-response-success').html("Completed");                   
                $('#run-geoserver-queue').removeAttr('disabled');
                $('#run-geoserver-queue-loader').hide();
                
            },
            error: function (error) {                    
                $('#geoserver-queue-job-response-error').html("Error running job");
                $('#run-geoserver-queue').removeAttr('disabled');
                $('#run-geoserver-queue-loader').hide();
            },
        });
    },
    run_geoserver_sync_cron_job: function(items_to_sync) {
        console.log("RUNNING GEOSERVER SYNC CRON JOB for: " + items_to_sync)
        $('#geoserver-sync-' + items_to_sync + '-job-response-success').html('');
        $('#geoserver-sync-' + items_to_sync + '-job-response-error').html('');
        var csrf_token = $("#csrfmiddlewaretoken").val();
        $('#run-geoserver-sync-' + items_to_sync).attr('disabled','disabled');
        $('#run-geoserver-sync-' + items_to_sync + '-loader').show();
        $.ajax({
            url: kbmanagementcommands.var.geoserver_queue_sync_job,
            type: 'POST',
            data: JSON.stringify({'items_to_sync': items_to_sync}),
            dataType: 'json',
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response) {                            
                $('#geoserver-sync-' + items_to_sync + '-job-response-success').html("Completed");                   
                $('#run-geoserver-sync-' + items_to_sync).removeAttr('disabled');
                $('#run-geoserver-sync-' + items_to_sync + '-loader').hide();
                
            },
            error: function (error) {                    
                $('#geoserver-sync-' + items_to_sync + '-job-response-error').html("Error running job");
                $('#run-geoserver-sync-' + items_to_sync).removeAttr('disabled');
                $('#run-geoserver-sync-' + items_to_sync + '-loader').hide();
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

        $( "#run-geoserver-queue" ).click(function() {
            console.log("Running GeoServer Queue");
            
            kbmanagementcommands.run_geoserver_queue_cron_job();
        });
        $( "#run-geoserver-sync" ).click(function() {
            console.log("Running GeoServer sync");
            kbmanagementcommands.run_geoserver_sync_cron_job('layers');
        });
        $( "#run-geoserver-sync-roles" ).click(function() {
            console.log("Running GeoServer sync roles");
            kbmanagementcommands.run_geoserver_sync_cron_job('roles');
        });
        $( "#run-geoserver-sync-groups" ).click(function() {
            console.log("Running GeoServer sync groups");
            kbmanagementcommands.run_geoserver_sync_cron_job('groups');
        });
        $( "#run-geoserver-sync-rules" ).click(function() {
            console.log("Running GeoServer sync rules");
            kbmanagementcommands.run_geoserver_sync_cron_job('rules');
        });
        $('#run-scanner-loader').hide();
        $('#run-sharepoint-scanner-loader').hide();
        $('#run-geoserver-queue-loader').hide();
        // $('#run-geoserver-sync-loader').hide();
    }

}