odoo.define('account_payment_group.hidebutton.js', function(require) {"use_strict";
    console.log( "hide button js loaded (1)" );
    $( document ).ready(function() {
        console.log( "hide button js loaded (2)" );
        $(".btn > span:contains('Guardar y Nuevo')").hide ();
        $(".btn > span:contains('Save & New')").hide ();

        /*$("button > span:contains('Guardar y Nuevo')").parent().addClass("hide_button");
        $("button > span:contains('Save & New')").parent().addClass("hide_button");*/
    });
    $(".btn > span:contains('Guardar y Nuevo')").click(function () {
        console.log( "click detected" );
        alert("No usar este boton porque no recalcula. Use guardar y cerrar en su lugar.");
        return false;
    });
});