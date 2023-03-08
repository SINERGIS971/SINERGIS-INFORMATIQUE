/* -- EN COURS DE DEV -- */

odoo.define('sinergis.dialog_popup', function (require) {
    "use strict";
    
    /*var Dialog = require('web.Dialog');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;

    var CustomDialog = Widget.extend({
        events: {
            'click .btn-primary': 'on_button_click',
        },
        start: function() {
            var self = this;
            var options = {
                title: "Titre de la fenêtre dialog",
                size: 'medium',
                buttons: [{
                    text: "Fermer",
                    classes: 'btn-primary',
                    close: true,
                }],
                //$content: QWeb.render('nom_de_votre_template'),
            };
            this.dialog = new Dialog(this, options).open();
            return this._super.apply(this, arguments);
        },
        on_button_click: function() {
            this.dialog.close();
        },
    });
    
    var custom_dialog = new CustomDialog(null);
    custom_dialog.appendTo($('body'));
    console.log("yoyo");*/
    
    
    
    
    window.onload = function() {
        $(document).on('click', '.btn-popover', function(){
             f();
         });
    };
    
    function f () {
        self=this;
        console.log("TEST2");
        var Dialog = require('web.Dialog');
        var rpc = require('web.rpc');

        Dialog.alert(
           this,
           "Dialog Alert",
           {
               onForceClose: function(){
                   console.log("Click Close");
               },
               confirm_callback: function(){
                   console.log("Click Ok");
                   
                   var seen = [];
                   var data = JSON.stringify(this, function(key, val) {
                       if (val != null && typeof val == "object") {
                            if (seen.indexOf(val) >= 0) {
                                return;
                            }
                            seen.push(val);
                        }
                        return val;
                    });
                    rpc.query({
                         model: "sale.order",
                         method: "test_debug",
                         args: [data],
                     }).then(function (result) { 
                                console.log(result);
                    });
               }
           }
        );
    }
    //dialog.open();

    });
    