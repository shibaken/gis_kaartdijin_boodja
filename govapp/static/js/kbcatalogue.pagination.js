var kbcatalogue_pagination = { 
    var: {
        "max_showon_pages" : 9,
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
        var beginning = 0;  // 0 means page 1
        let page_over = kbcatalogue.var.total_pages > this.var.max_showon_pages; 
        var end = page_over ? this.var.max_showon_pages : kbcatalogue.var.total_pages;
        if (page_over &&
            kbcatalogue.var.current_page > this.var.max_showon_pages/2){
            if (kbcatalogue.var.current_page < kbcatalogue.var.total_pages - this.var.max_showon_pages/2){
                beginning = kbcatalogue.var.current_page - Math.floor(this.var.max_showon_pages/2);
                end = kbcatalogue.var.current_page + Math.ceil(this.var.max_showon_pages/2);
            } else {
                beginning = kbcatalogue.var.total_pages - this.var.max_showon_pages;
                end = kbcatalogue.var.total_pages;
            }
        }

        var prev_status = (kbcatalogue.var.current_page == 0) ? "disabled" : null;
        var next_status = (kbcatalogue.var.current_page+1 == kbcatalogue.var.total_pages) ? "disabled" : null;
        var navi_html = "";
        navi_html+=make_page_btn("paging_btn_prev", "Previous", prev_status);
        for (let i=beginning ; i < end ; i++){
            var status = (i == kbcatalogue.var.current_page) ? 'current' : null ;
            navi_html+=make_page_btn('paging_btn_'+(i+1), (i+1), status);
        }
        navi_html+=make_page_btn("paging_btn_next", "Next", next_status);
        $('#paging_navi').html(navi_html);

        // add onclick event
        // for page number buttons 
        for (let i=beginning ; i < end ; i++){
            $('#paging_btn_'+(i+1)).off('click').on('click', function(event){
                event.preventDefault();
                kbcatalogue.var.current_page = i;
                let url_params = kbcatalogue.make_get_catalogue_params_str({'limit':limit, 'offset':i*limit});
                kbcatalogue.get_catalogue(kbcatalogue.var.catalogue_data_url+"?"+url_params);
            });
        }

        //prev and next buttons
        $('#paging_btn_prev').off('click').on('click', function(event){
            event.preventDefault();
            kbcatalogue.var.current_page -= 1;
            let url_params = kbcatalogue.make_get_catalogue_params_str({'limit':limit, 'offset':kbcatalogue.var.current_page*limit});
            kbcatalogue.get_catalogue(kbcatalogue.var.catalogue_data_url+"?"+url_params);
        });
        $('#paging_btn_next').off('click').on('click', function(event){
            event.preventDefault();
            kbcatalogue.var.current_page += 1;
            let url_params = kbcatalogue.make_get_catalogue_params_str({'limit':limit, 'offset':kbcatalogue.var.current_page*limit});
            kbcatalogue.get_catalogue(kbcatalogue.var.catalogue_data_url+"?"+url_params);
        });
    }
}
