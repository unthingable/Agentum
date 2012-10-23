/**
 * Created with JetBrains PhpStorm.
 * Author: Kirill Cherkashin
 * Date: 10/17/12
 * Time: 10:50 PM
 *
 * This is just a basic router. We don't need to use in is basic models
 *
 */

define( "agentum_router", ["backbone"], function ( Backbone ) {
    "use strict";

    var Router = Backbone.Router.extend({
        routes: {
            "": "index",
            "about":"about"
        },

        about: function() {
            alert("Agentum v 0.1");
        }

    });

    var router = new Router();
    Backbone.history.start();
    return router;

} );