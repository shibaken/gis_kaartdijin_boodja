var common_entity_modal = { 
    var: {
        type: "submit",
    },
    init : function(title, type="submit"){
        $('#common-entity-modal-error').hide();
        $('#common-entity-modal-label').text(title);
        if(type=="submit"){
            $('#common-entity-modal-submit-btn').show();
            $('#common-entity-modal-cancel-btn').hide();
            $('#common-entity-modal-delete-btn').hide();
        } else if(type=="delete"){
            $('#common-entity-modal-submit-btn').hide();
            $('#common-entity-modal-cancel-btn').show();
            $('#common-entity-modal-delete-btn').show();
        }
        this.var.type = type;

        // remove all previous fields
        $('#common-entity-modal-content').empty();
    },
    add_field: function(label, type="text", value=null, option_map={}){
        let contents = $('#common-entity-modal-content');
        
        //label
        contents.append($('<label>').text(label));
        
        //field
        let field = this.maker[type](label, value, option_map);
        contents.append(field);
        // return field.attr("id");
        return this.get_id(field);
    },
    maker : {
        make_common_field : (label, value, type="text", element="<input>") => {
            let field = $(element);
            field.attr("type", type);
            field.attr("class", "form-control");
            field.attr("id", "common-entity-modal-"+label.replace(' ', '-').toLowerCase());
            if(value != null) 
                field.val(value);
            if (common_entity_modal.var.type == "delete") 
                field.prop("disabled", true);
            return field;
        },
        text : (label, value) => {
            value = value ? value : "";
            return common_entity_modal.maker.make_common_field(label, value=value);
        },
        number : (label, value) => {
            value = value ? value : "";
            let field = common_entity_modal.maker.make_common_field(label, value=value, type="number");
            field.on('input',function(){
                $(this).val($(this).val().replace(/\D/g, ""));
            });
            return field;
        },
        email : (label, value) => {
            return common_entity_modal.maker.make_common_field(label, value=value, type="email");
        },
        select : (label, value, option_map) => {
            let field = common_entity_modal.maker.make_common_field(label, value, type="text", element="<select>");
            for(let key in option_map)
                field.append('<option value="'+key+'">'+option_map[key]+'</option>');
            return field;

        },
        switch : (label, value) => {
            let div = $('<div>');
            div.attr("class", "form-check form-switch");

            let field = common_entity_modal.maker.make_common_field(label, value, type="checkbox", element="<input>");
            field.attr("role", "switch");
            field.attr("class", "form-check-input");
            field.prop('checked', value);

            div.append(field);
            return div;
        },
    },
    get_id: function(element){
        if(element.is('input') || element.is('select')){
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
        let callback_with_close = async () =>{
            try{
                response = await submit_callback();
                success_callback();
                common_entity_modal.hide();
            } catch(error){
                if('status' in error && error.status == 400){
                    let error_obj = JSON.parse(error.responseText);
                    let msg;
                    for(let key in error_obj)
                        msg = error_obj[key];
                    common_entity_modal.show_error_modal(msg);
                }
                else
                    common_entity_modal.show_error_modal(error.message);
            }
        }
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
}