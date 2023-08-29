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
    },
   convert_date_format: function(date_str, format, hh, mm, ss){
        if(!date_str) return null;
        // make a moment object by original format
        let original_format = format.toUpperCase()+'-hh:mm:ss';
        date_str = date_str + '-' + hh + ":" + mm + ":" + ss;
        let target_format = 'YYYY-MM-DDTHH:mm:ss';
        let converted_str = this.convert_datetime_format(date_str, target_format, original_format);
        return converted_str
    },
    convert_datetime_format: function(datetime_str, target_format, original_format){
        if(!datetime_str) return null;
        let original_datetime;
        if(original_format){
            // make a moment object by original format
            original_datetime = moment(datetime_str, original_format);
        }else{
            original_datetime = moment(datetime_str);
        }
        
        return original_datetime.format(target_format);
    },
    call_get_api: function(url, success_callback, error_callback){
        $.ajax({
            url: url,
            type: 'GET',
            contentType: 'application/json',
            success: (response) => {
                if(!response || !response.results){
                    error_callback();
                    return;
                }
                success_callback();
            },
            error: error_callback,
        });
    },
    enter_keyup: function(text_input, callback){
        text_input.on("keyup", function(e) {
            if (e.keyCode === 13) { // eneter key
                callback();
            }
          });
    }
}
