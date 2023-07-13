var common_entity_modal = { 
    var: {
        type: "submit",
        fields: [],
    },
    init: function(title, type="submit"){
        $('#common-entity-modal-table').hide();
        $('#common-entity-modal-error').hide();
        $('#common-entity-modal-label').text(title);
        if(type=="submit"){
            $('#common-entity-modal-submit-btn').show();
            $('#common-entity-modal-delete-btn').hide();
            $('#common-entity-modal-cancel-btn').show();
        } else if(type=="delete"){
            $('#common-entity-modal-submit-btn').hide();
            $('#common-entity-modal-delete-btn').show();
            $('#common-entity-modal-cancel-btn').show();
        } else if(type="info"){
            $('#common-entity-modal-submit-btn').hide();
            $('#common-entity-modal-delete-btn').hide();
            $('#common-entity-modal-cancel-btn').hide();
        }
        this.var.type = type;

        // remove all previous fields
        $('#common-entity-modal-content').empty();
        common_entity_modal.set_all_disabled(false);
    },
    add_field: function(label, type="text", value=null, option_map={}, disabled=false){
        let contents = $('#common-entity-modal-content');
        
        //label
        contents.append($('<label>').text(label));
        
        //field
        disabled = common_entity_modal.var.type == "delete" ? true: disabled;
        let field = this.maker[type](label, value, disabled, option_map);
        contents.append(field);
        common_entity_modal.var.fields.push(field);
        return this.get_id(field, type);
    },
    init_talbe: function(){
        $('#modal-table thead').empty();
        $('#modal-table tbody').empty();
        this.get_limit().off('change');
        this.get_limit().val("10");
        this.get_search().val("");
        $('#common-entity-modal-table').show();
    },
    maker: {
        make_common_field: (label, value, disabled, type="text", element="<input>") => {
            let field = $(element);
            field.attr("type", type);
            field.attr("class", "form-control");
            field.attr("id", "common-entity-modal-"+label.replace(' ', '-').toLowerCase());
            if(value != null) 
                field.val(value);
            if (disabled) 
                field.prop("disabled", true);
            return field;
        },
        text: (label, value, disabled) => {
            value = value ? value: "";
            return common_entity_modal.maker.make_common_field(label, value, disabled);
        },
        text_area: (label, value, disabled) => {
            let field = common_entity_modal.maker.make_common_field(label, value, disabled, type="text", element="<textarea>");
            field.attr("row", 10);
            return field;
            // <textarea class="form-control" id="exampleFormControlTextarea1" rows="3"></textarea>
        },
        number: (label, value, disabled) => {
            value = value ? value: "";
            let field = common_entity_modal.maker.make_common_field(label, value, disabled, type="number");
            field.on('input',function(){
                $(this).val($(this).val().replace(/\D/g, ""));
            });
            return field;
        },
        email: (label, value, disabled) => {
            return common_entity_modal.maker.make_common_field(label, value=value, disabled, type="email");
        },
        select: (label, value, disabled, option_map) => {
            let field = common_entity_modal.maker.make_common_field(label, value, disabled, type="text", element="<select>");
            for(let key in option_map)
                field.append('<option value="'+key+'">'+option_map[key]+'</option>');
            field.val(value);
            return field;

        },
        switch: (label, value, disabled) => {
            let div = $('<div>');
            div.attr("class", "form-check form-switch");

            value = value != null ? value: true;
            let field = common_entity_modal.maker.make_common_field(label, value, disabled, type="checkbox", element="<input>");
            field.attr("role", "switch");
            field.attr("class", "form-check-input");
            field.prop('checked', value);

            div.append(field);
            return div;
        },
        // option_map = {label:{width:int, type:str}} e.g) {Name:{width:2, type:'text'}}
        // table: (label, value, disabled, option_map) => {
        //     let div = $('<div>');
        //     column_thead = {};
        //     for(let key in option_map){
        //         column_thead[key] = option_map[key][width];
        //     }
        //     let tbody = table.set_table(div, label+"-table", column_thead);

        //     column_tbody = {};
        //     for(let key in option_map){
        //         column_tbody[key] = option_map[key][type];
        //     }
        //     table.set_tbody(tbody, value, column_tbody);
        //     if (disabled){ 
        //         div.prop("disabled", true);
        //     }
        //     return div
        // },
        empty: () => {
            let div = $('<div>');
            div.attr('id', 'modal-table');
            return div;
        }
    },
    get_id: function(element, type){
        if(element.is('input') || element.is('select') || type == 'empty'){
            return element.attr("id");
        } else if(element.is('div')){
            let children = element.children();
            for(let i in children){
                let res = this.get_id($(children[i]));
                if(res)
                    return res; 
            }
        }
        return null
    },
    add_callbacks: function(submit_callback, success_callback){
        let error_handler = (error)=>{
            common_entity_modal.set_all_disabled(false);
            if('status' in error){
                let error_obj = JSON.parse(error.responseText);
                let msg;
                for(let key in error_obj)
                    msg = error_obj[key];
                common_entity_modal.show_error_modal(msg);
            }
            else
                common_entity_modal.show_error_modal(error.message);
        };
        
        let callback_with_close = () =>{
            common_entity_modal.set_all_disabled(true);
            try{
                submit_callback(
                    (response)=>{   //success_callback
                            if(success_callback){
                                success_callback(response);
                            }
                            common_entity_modal.hide();
                        },
                        error_handler); //error callback
                }catch(error){
                    error_handler(error);
                }
        };
        $('#common-entity-modal-submit-btn').off('click');
        $('#common-entity-modal-delete-btn').off('click');
        if(this.var.type == 'submit'){
            $('#common-entity-modal-submit-btn').click(callback_with_close);
        } else if (this.var.type == 'delete'){
            $('#common-entity-modal-delete-btn').click(callback_with_close);
        }
    },
    show_error_modal: function(error){
        $('#common-entity-modal-error').text(error);
        $('#common-entity-modal-error').show();
        console.log(error);
    },
    show: function(){
        $('#common-entity-modal').modal('show');
    },
    hide: function(){
        $('#common-entity-modal').modal('hide');
    },
    get_thead: function(){
        return $('#modal-table-thead');
    },
    get_tbody: function(){
        return $('#modal-table-tbody');
    },
    get_limit: function(){
        return $('#modal-table-limit');
    },
    get_search: function(){
        return $('#modal-table-search');
    },
    get_page_navi: function(){
        return $('#modal-table-page-navi');
    },
    set_all_disabled: function(disabled){
        for(let i in common_entity_modal.var.fields){
            common_entity_modal.var.fields[i].prop("disabled", disabled);
        }
        $('#common-entity-modal-submit-btn').prop("disabled", disabled);
        $('#common-entity-modal-cancel-btn').prop("disabled", disabled);
        $('#common-entity-modal-delete-btn').prop("disabled", disabled);
    },
}