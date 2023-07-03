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
    }
}
