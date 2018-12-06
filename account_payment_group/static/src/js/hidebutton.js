odoo.define('account_payment_group.hidebutton.js', function(require) {"use_strict";
    $("button > span:contains('Guardar y Nuevo')").parent().addClass("hide_button");
})
