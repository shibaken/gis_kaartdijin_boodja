var utils={
    make_query_params: function (params){
        var url_params = "";
    
        if (params){
            for (var key in params){
                if(params[key])
                    url_params += "&" + key + "=" + params[key];
            }
        }
        return url_params;
    },
    validate_email: function (email) {
        if(!email) return false;
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        $('#common-entity-modal-error').hide();
        if (!emailRegex.test(email)) {
            throw new Error("Wrong email format.");
        }
        return email;
    },
    validate_empty_input: function(key, val, msg=key+" is required."){
        if(!val){
            throw new Error(msg);
        }
        return val;
    },
    validate_number: function(key, val, msg="Please enter a valid "+key+". (must be positive number)"){
        if(isNaN(val) || val < 0){
            throw new Error(msg);
        }
        return val;
    }
}
