/**
 * Created with JetBrains PhpStorm.
 * Author: Kirill Cherkashin
 * Date: 11/9/12
 * Time: 1:59 PM
 *
 */
/**
 * Created with JetBrains PhpStorm.
 * Author: Kirill Cherkashin
 * Date: 10/18/12
 * Time: 2:03 PM
 *
 * This module provides the layout for the application.
 * If we want to tweak the layout we can include this module and play with it.
 */

define( "agentum_layout", ["backbone", "agentum_sim"], function ( Backbone, App ) {
    "use strict";

    var _div = "<div/>";
    var _selector = "#agentum";
    var ListView = Backbone.View.extend( {

        el:         $( 'body' ),

        /**
         * Constructor
         */
        initialize: function () {

            _.bindAll( this, 'render' );
            this.render();
        },

        /**
         *  Creating the layout
         */
        render: function () {
            this.$header = $( _div ).attr( "id", "header" );
            this.$control = $( _div ).attr( "id", "controls" );
            this.$sidebar = $( _div ).attr( "id", "sidebar" );
            this.$statusbar = $( _div ).attr( "id", "statusbar" );
            this.$grid = $( _div ).attr( "id", "grid" );
            this.$data = $( _div ).attr( "id", "data" )
                .append( this.$sidebar )
                .append( this.$grid );

            $( this.el )
                .append(
                $( _div ).attr( "id", "simulation" )
                    .append( this.$header )
                    .append( this.$control )
                    .append( this.$data )
                    .append( this.$statusbar  )

            );

        }
    } );

    var layout = new ListView();

    /**
     * On name change update name.
     */
    App.on( "name", function ( name ) {
        layout.$header.html( "<h1>" + name + "</h1>" )
    } );


    return layout;

} );