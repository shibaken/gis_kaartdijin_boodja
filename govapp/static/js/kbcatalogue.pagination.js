var kbcatalogue_pagination = { 
    var: {
        "max_showon_pages" : 9,
        pagination: common_pagination,
    },
    make_get_catalogue_params_str : function(params){
        var url_params = pagination.make_get_params_str(params);

        url_params += pagination.add_param($('#catalogue-name').val(), 'name__icontains');
        url_params += pagination.add_param($('#catalogue-status').val(), 'status');
        url_params += pagination.add_param($('#catalogue-description').val(), 'description__icontains');
        url_params += pagination.add_param($('#catalogue-number').val().replace("PE", ""), 'id');
        url_params += pagination.add_param($('#catalogue-limit').val(), 'limit');
        url_params += pagination.add_param($('#catalogue-order-by').val(), 'order_by');

        return url_params;
    },
    init:  function(kbcatalogue) {
        // let make_page_btn = function(id, text, status){
        //     var html = '<li class="page-item{disabled1}{current1}"{current2}><a class="page-link" href="#" id="'+id+'"{disabled2}>'+text+'</a></li>'
        //     if (status == 'disabled'){
        //         html = html.replace("{disabled1}", ' disabled');
        //         html = html.replace("{disabled2}", ' aria-disabled="true"');
        //     }
        //     if (status == 'current'){
        //         html = html.replace("{current1}", ' active');
        //         html = html.replace("{current2}", ' aria-current="page"');
        //     }
        //     html = html.replace(/{disabled1}|{disabled2}|{current1}|{current2}/g, '');
        //     return html;
        // }
        let limit = kbcatalogue.var.limit;

        // set html of page navigation buttons
        let range = common_pagination.make_page_range(kbcatalogue.var.current_page, kbcatalogue.var.total_pages, this.var.max_showon_pages);
        let beginning = range.beginning;
        let end = end;

        // var beginning = 0;  // 0 means page 1
        // let page_over = kbcatalogue.var.total_pages > this.var.max_showon_pages; 
        // var end = page_over ? this.var.max_showon_pages : kbcatalogue.var.total_pages;
        // if (page_over &&
        //     kbcatalogue.var.current_page > this.var.max_showon_pages/2){
        //     if (kbcatalogue.var.current_page < kbcatalogue.var.total_pages - this.var.max_showon_pages/2){
        //         beginning = kbcatalogue.var.current_page - Math.floor(this.var.max_showon_pages/2);
        //         end = kbcatalogue.var.current_page + Math.ceil(this.var.max_showon_pages/2);
        //     } else {
        //         beginning = kbcatalogue.var.total_pages - this.var.max_showon_pages;
        //         end = kbcatalogue.var.total_pages;
        //     }
        // }

        common_pagination.make_btn_html(kbcatalogue.var.current_page, kbcatalogue.var.total_pages, '#paging_navi')

        // var prev_status = (kbcatalogue.var.current_page == 0) ? "disabled" : null;
        // var next_status = (kbcatalogue.var.current_page+1 == kbcatalogue.var.total_pages) ? "disabled" : null;
        // var navi_html = "";
        // navi_html+=common_pagination.make_page_btn_html("paging_btn_prev", "Previous", prev_status);
        // for (let i=beginning ; i < end ; i++){
        //     var status = (i == kbcatalogue.var.current_page) ? 'current' : null ;
        //     navi_html+=common_pagination.make_page_btn_html('paging_btn_'+(i+1), (i+1), status);
        // }
        // navi_html+=common_pagination.make_page_btn_html("paging_btn_next", "Next", next_status);
        // $('#paging_navi').html(navi_html);

        // add onclick event
        // for page number buttons 
        let set_btn_event = function(id, page_number){
            $(id).off('click').on('click', function(event){
                event.preventDefault();
                kbcatalogue.var.current_page = page_number;
                let url_params = make_get_catalogue_params_str({'limit':limit, 'offset':page_number*limit});
                kbcatalogue.get_catalogue(kbcatalogue.var.catalogue_data_url+"?"+url_params);
            });
        }

        for (let i=beginning ; i < end ; i++){
            set_btn_event('#paging_btn_'+(i+1), i);
            // $('#paging_btn_'+(i+1)).off('click').on('click', function(event){
            //     event.preventDefault();
            //     kbcatalogue.var.current_page = i;
            //     let url_params = make_get_catalogue_params_str({'limit':limit, 'offset':i*limit});
            //     kbcatalogue.get_catalogue(kbcatalogue.var.catalogue_data_url+"?"+url_params);
            // });
        }

        //prev and next buttons
        set_btn_event('#paging_btn_prev', kbcatalogue.var.current_page - 1);
        // $('#paging_btn_prev').off('click').on('click', function(event){
        //     event.preventDefault();
        //     kbcatalogue.var.current_page -= 1;
        //     let url_params = make_get_catalogue_params_str({'limit':limit, 'offset':kbcatalogue.var.current_page*limit});
        //     kbcatalogue.get_catalogue(kbcatalogue.var.catalogue_data_url+"?"+url_params);
        // });
        set_btn_event('#paging_btn_next', kbcatalogue.var.current_page + 1);
        // $('#paging_btn_next').off('click').on('click', function(event){
        //     event.preventDefault();
        //     kbcatalogue.var.current_page += 1;
        //     let url_params = make_get_catalogue_params_str({'limit':limit, 'offset':kbcatalogue.var.current_page*limit});
        //     kbcatalogue.get_catalogue(kbcatalogue.var.catalogue_data_url+"?"+url_params);
        // });
    }
}
