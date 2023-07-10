var table={
    // common_table.set_rows('#catalogue-detail-notification-tbody', response.results, {key:'active', type:'switch'},
                //                         buttons={Update:kbcatalogue_detail.show_update_email_notification_modal, 
                //                                 Delete:kbcatalogue_detail.show_delete_email_notification_modal});

                // <div id='publish-table'>
                //         <table id="example" class="table" style="width:100%">
                //               <thead class='table-dark'>
                //                     <tr>
                //                           <th class="col-2">Id</th>
                //                           <th class="col-4">Name</th>
                //                           <th class="col-2">Type</th>
                //                           <th class="col-2">Order</th>
                //                           <th class="col-2">Action</th>
                //                     </tr>
                //               </thead>
                //               <tbody id='catalogue-attribute-tbody'></tbody>
    set_table: function (div, table_id, columns){
        let table = $('<table>');
        table.attr('id', table_id);
        table.attr('class', 'table');
        table.attr('style', 'width:100%');

        let thrad = $('<thead>');
        thrad.attr('class', 'table-dark');

        let tr = $('<tr>');

        for(key in columns){
            let th = $('<th>');
            th.attr('class', 'col-'+columns[key]);
            th.text(key);
            tr.append(th);
        }
        
    },
    set_tbody: function (tbody, list, columns, buttons=null){
        tbody.empty();

        for(let i in list){
            let row = this.make_row(list[i], columns);
            if(buttons){
                row.append(this.make_button_cell(buttons, tbody.attr("id")+'-row-'+i, list[i]));
            }
            tbody.append(row);
        }
    },

    // ('#catalogue-detail-notification-tbody', response.results, {active:'switch'},
    //                                     buttons={Update:kbcatalogue_detail.show_update_email_notification_modal, 
    //                                             Delete:kbcatalogue_detail.show_delete_email_notification_modal});

    make_row: function (obj, columns){
        let row = $('<tr>');
        for(let i in columns){
            let key = Object.keys(columns[i])[0];
            if(key in obj){
                if(columns[i][key] == 'switch')
                    row.append(this.make_switch_cell(obj[key]));
                else if(columns[i][key] == 'text')
                    row.append(this.make_text_cell(obj[key]));
            }
        }
        return row;
    },
    make_text_cell: function(text){
        return $('<td>').text(text);
    },
    make_switch_cell: function(checked, disabled=true){
        let div = $('<div>').attr("class", "form-check form-switch");
        let input = $('<input>').attr("class", "form-check-input").attr("type", "checkbox").attr("role", "switch")
                    .prop("checked", checked).prop("disabled", disabled);
        div.append(input);
        return $('<td>').append(div);
    },
    make_button_cell: function(buttons, id_prefix, data){
        // e.g. : buttons={Update:callback(data)}
        let td = $('<td>');
        for(let key in buttons){
            let button = $('<button>').attr("class", "btn btn-primary btn-sm").attr("id", id_prefix+"-"+key.toLowerCase()).text(key);
            button.click(()=>buttons[key](data));
            td.append(button);
            td.append(" ")
        }
        return td;
    },
    refresh: function(draw_table_callback){
        common_pagination.var.current_page = 0;
        draw_table_callback();
    }
}