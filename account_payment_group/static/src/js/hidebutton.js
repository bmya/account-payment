odoo.define('account_payment_group.hidebutton.js', function(require) {"use_strict";
    console.log( "hide button js loaded (1)" );
    /* $( document ).ready(function() {
        console.log( "hide button js loaded (2)" );
        $(".btn > span:contains('Guardar y Nuevo')").hide ();
        $(".btn > span:contains('Save & New')").hide ();*/

        /*$("button > span:contains('Guardar y Nuevo')").parent().addClass("hide_button");
        $("button > span:contains('Save & New')").parent().addClass("hide_button");*/
    /*});*/
    /*$('.modal .modal-footer button:eq(1)').click(){
        console.log( "click detected" );
        alert("No usar este boton porque no recalcula. Use guardar y cerrar en su lugar.");
        return false;

    };*/
    var FormViewDialog = ViewDialog.extend({
    /**
     * @param {Widget} parent
     * @param {Object} [options]
     * @param {string} [options.parentID] the id of the parent record. It is
     *   useful for situations such as a one2many opened in a form view dialog.
     *   In that case, we want to be able to properly evaluate domains with the
     *   'parent' key.
     * @param {integer} [options.res_id] the id of the record to open
     * @param {Object} [options.form_view_options] dict of options to pass to
     *   the Form View @todo: make it work
     * @param {Object} [options.fields_view] optional form fields_view
     * @param {boolean} [options.readonly=false] only applicable when not in
     *   creation mode
     * @param {function} [options.on_saved] callback executed after saving a
     *   record.  It will be called with the record data, and a boolean which
     *   indicates if something was changed
     * @param {BasicModel} [options.model] if given, it will be used instead of
     *  a new form view model
     * @param {string} [options.recordID] if given, the model has to be given as
     *   well, and in that case, it will be used without loading anything.
     * @param {boolean} [options.shouldSaveLocally] if true, the view dialog
     *   will save locally instead of actually saving (useful for one2manys)
     */
    init: function (parent, options) {
        var self = this;

        this.res_id = options.res_id || null;
        this.on_saved = options.on_saved || (function () {});
        this.context = options.context;
        this.model = options.model;
        this.parentID = options.parentID;
        this.recordID = options.recordID;
        this.shouldSaveLocally = options.shouldSaveLocally;

        var multi_select = !_.isNumber(options.res_id) && !options.disable_multiple_selection;
        var readonly = _.isNumber(options.res_id) && options.readonly;

        if (!options || !options.buttons) {
            options = options || {};
            options.buttons = [{
                text: (readonly ? _t("Close") : _t("Discard")),
                classes: "btn-default o_form_button_cancel",
                close: true,
                click: function () {
                    if (!readonly) {
                        self.form_view.model.discardChanges(self.form_view.handle, {
                            rollback: self.shouldSaveLocally,
                        });
                    }
                },
            }];

            if (!readonly) {
                options.buttons.unshift({
                    text: _t("Save") + ((multi_select)? " " + _t(" & Close") : ""),
                    classes: "btn-primary",
                    click: function () {
                        this._save().then(self.close.bind(self));
                    }
                });

                if (multi_select) {
                    options.buttons.splice(1, 0, {
                        text: _t("Save & New"),
                        classes: "btn-primary",
                        click: function () {

                        }
                            /*this._save().then(self.form_view.createRecord.bind(self.form_view, self.parentID));*/
                            alert("No usar este boton porque no recalcula. Use guardar y cerrar en su lugar.");
                        },
                    });
                }
            }
        }
        this._super(parent, options);
    },
});