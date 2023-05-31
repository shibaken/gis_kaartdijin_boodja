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
        // var catalogue_id = $('#catalogue_entry_id').val();
        // var cataloguename = $('#catalogue-entry-name').val();
        // var cataloguecustodianentry = $('#catalogue-custodian-entry').val();
        // var cataloguedescription = $('#catalogue-entry-description').val();


        // var post_data = {"name": cataloguename, "description": cataloguedescription, "custodian": cataloguecustodianentry};
        // var csrf_token = $("#csrfmiddlewaretoken").val();
        // var pagetab = $('#pagetab').val();

        // $.ajax({
        //     url: kbcatalogue.attribute.var.catalogue_attribute_url+catalogue_id+"/",            
        //     type: 'PUT',
        //     headers: {'X-CSRFToken' : csrf_token},
        //     data: JSON.stringify(post_data),
        //     contentType: 'application/json',
        //     success: function (response) {

        //         if (save_status == 'save-and-exit') {
        //             window.location = '/catalogue/entries/';
        //         } else {
        //            window.location = "/catalogue/entries/"+catalogue_id+"/"+pagetab+"/"; 
        //         }
        //     },
        //     error: function (error) {
        //          alert("ERROR Saving.");

        
        //     },
        // });



    }

}