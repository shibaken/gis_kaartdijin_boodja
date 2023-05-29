var common_pagination = { 
    var: {},
    make_page_btn_html : function(id, text, status){
        var html = '<li class="page-item{disabled1}{current1}"{current2}><a class="page-link" href="#" id="'+id+'"{disabled2}>'+text+'</a></li>'
        if (status == 'disabled'){
            html = html.replace("{disabled1}", ' disabled');
            html = html.replace("{disabled2}", ' aria-disabled="true"');
        }
        if (status == 'current'){
            html = html.replace("{current1}", ' active');
            html = html.replace("{current2}", ' aria-current="page"');
        }
        html = html.replace(/{disabled1}|{disabled2}|{current1}|{current2}/g, '');
        return html;
    },
    add_param : function(url_params, param_val, key){
        if (params && key in params){
            return;
        }
        if (param_val.length > 0) {
            url_params += "&"+key+"="+param_val;
        }
        return url_params;
    },
    make_get_params_str : function(params){
        var url_params = "";

        if (params){
            for (var key in params){
                url_params += "&" + key + "=" + params[key];
            }
        }
        return url_params;
    },
    make_page_range : function(current, total, max_shown){
        var beginning = 0;  // 0 means page 1
        let page_over = total > max_shown; 
        var end = page_over ? max_shown : total;
        if (page_over && current > max_shown/2){
            if (current < total - max_shown/2){
                beginning = current - Math.floor(max_shown/2);
                end = current + Math.ceil(max_shown/2);
            } else {
                beginning = total - max_shown;
                end = total;
            }
        }
        return {'beginning':beginning, 'end':end};
    },
    make_btn_html : function(current, total, paging_id){
        var prev_status = (current == 0) ? "disabled" : null;
        var next_status = (current+1 == total) ? "disabled" : null;
        var navi_html = "";
        navi_html+=make_page_btn_html("paging_btn_prev", "Previous", prev_status);
        for (let i=beginning ; i < end ; i++){
            var status = (i == current) ? 'current' : null ;
            navi_html+=make_page_btn_html('paging_btn_'+(i+1), (i+1), status);
        }
        navi_html+=make_page_btn_html("paging_btn_next", "Next", next_status);
        $(paging_id).html(navi_html);
    }
}