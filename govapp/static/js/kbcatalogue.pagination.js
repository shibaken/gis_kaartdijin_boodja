var kbcatalogue_pagination = { 
    var: {
        "max_showon_pages" : 10,
        "beginning_of_pagenumber" : 0
    },
    init:  function(kbcatalogue, response) {
        let limit = +$('#catalogue-limit').val();
        
        let make_page_btn = function(id, text, status){
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
        }

        // set html of page navigation buttons
        let beginning = this.var.beginning_of_pagenumber;
        let too_many = kbcatalogue.var.total_pages - beginning > this.var.max_showon_pages;
        let end = too_many ? this.var.beginning_of_pagenumber + this.var.max_showon_pages : kbcatalogue.var.total_pages;
        var prev_status = (beginning > 0) ? null : "disabled";
        var next_status = too_many ? null : "disabled";
        var navi_html = "";
        navi_html+=make_page_btn("paging_btn_prev", "Previous", prev_status);
        for (let i=beginning ; i < end ; i++){
            var status = (i == kbcatalogue.var.offset_page) ? 'current' : null ;
            navi_html+=make_page_btn('paging_btn_'+(i+1), (i+1), status);
        }
        navi_html+=make_page_btn("paging_btn_next", "Next", next_status);
        $('#paging_navi').html(navi_html);

        // add onclick event
        // for page number buttons 
        for (let i=beginning ; i < end ; i++){
            $('#paging_btn_'+(i+1)).off('click').on('click', function(event){
                event.preventDefault();
                kbcatalogue.var.offset_page = i;
                let url_params = kbcatalogue.make_get_catalogue_params_str({'limit':limit, 'offset':i*limit});
                kbcatalogue.get_catalogue(kbcatalogue.var.catalogue_data_url+"?"+url_params);
            });
        }

        //prev and next buttons
        $('#paging_btn_prev').off('click').on('click', function(event){
            event.preventDefault();
            kbcatalogue_pagination.var.beginning_of_pagenumber -= kbcatalogue_pagination.var.max_showon_pages;
            kbcatalogue_pagination.init(kbcatalogue, response);
        });
        $('#paging_btn_next').off('click').on('click', function(event){
            event.preventDefault();
            kbcatalogue_pagination.var.beginning_of_pagenumber += kbcatalogue_pagination.var.max_showon_pages;
            kbcatalogue_pagination.init(kbcatalogue, response);
        });
    }
}
