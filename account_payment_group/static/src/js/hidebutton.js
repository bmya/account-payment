odoo.define('account_payment_group.hidebutton.js', function(require) {"use_strict";
    console.log( "hide button js loaded (1)" );
    $("button > span:contains('Guardar y Nuevo')").parent().addClass("hide_button");*/
    $( document ).ready(function() {
        console.log( "hide button js loaded (2)" );
        /*$("button > span:contains('Guardar y Nuevo')").parent().addClass("hide_button");
        $("button > span:contains('Save & New')").parent().addClass("hide_button");*/
    });
});