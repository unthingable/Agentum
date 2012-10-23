/**
 * Created with JetBrains PhpStorm.
 * Author: Kirill Cherkashin
 * Date: 10/18/12
 * Time: 2:03 PM
 *
 * This is a global object, which can be used across the modules.
 */
define( "agentum_sim", ["backbone"], function ( Backbone) {
    "use strict";

    var Agentum = Backbone.Model.extend({});
    return  new Agentum();

} );