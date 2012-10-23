/**
 * Created with JetBrains PhpStorm.
 * Author: Kirill Cherkashin
 * Date: 10/18/12
 * Time: 8:34 PM
 *
 */
define( "agentum_grid", ["agentum_sim", "agentum_layout", "underscore"], function ( app, view, _ ) {
    "use strict";

    var Grid = Backbone.View.extend( {

        el:       view.$grid,
        width: 10,
        height: 10,
        zoom: 1,

        events : {
            'click canvas' : 'handle_click'
        },
        /**
         * Resizes the canvas based on the values given.
         * @param width
         * @param height
         */
        set_size: function ( width, height ) {

            if( !_.isNumber( width )  || !_.isNumber( height ) ) {
                throw "Width and height must be a number. width:" + width + " and height:" + height + " given.";
            }
            this.width = width;
            this.height = height;
            this.render();
        },
        handle_click: function ( e ) {
            console.log( this.zoom );
            var x = Math.floor(( e.hasOwnProperty('offsetX') ? e.offsetX : e.layerX) / this.zoom );
            var y = Math.floor(( e.hasOwnProperty('offsetY') ? e.offsetY : e.layerY) / this.zoom );
            this.trigger( "click", x, y );
        },

        set_zoom: function ( zoom ) {
            if( !_.isNumber( zoom ) ) {
                throw "zoom must be numeric. 1 is for 100%";
            }
            this.zoom = zoom;
            this.render_display();
            this.draw();
            
        },

        render_display: function () {

            this.$canvas = $( "<canvas></canvas>" )
                .attr( "width", this.width*this.zoom )
                .attr( "height", this.height*this.zoom );

            this.display_context = this.$canvas[0].getContext("2d");
            this.display_context.scale( this.zoom ,this.zoom );

            $( this.el ).html( this.$canvas );

        },



        initialize: function () {
            this.render();
        },

        render: function () {
            this.render_display();
            this.buffer = document.createElement('canvas');
            this.buffer.width = this.width;
            this.buffer.height = this.height;
            this.context = this.buffer.getContext( '2d' );
            this.image_data = this.context.createImageData( this.width, this.height);

        },

        set_pixel: function ( position, colors ) {
            colors[3] = colors[3] || 255;
            var index = (position[0] + position[1] * this.width ) * 4;
            for( var i = 0; i < colors.length; i++ ) {
                this.image_data.data[ index + i] = colors[i];
            }
        },
        refresh: function () {
            this.display_context.drawImage(this.buffer, 0, 0);
        },

        clear:     function ( color ) {

            this.context.fillStyle = color ;
            this.context.fillRect( 0, 0, 100, 100);
            this.refresh();


        },

        draw: function () {
            this.context.putImageData(this.image_data, 0, 0);
            this.refresh();
        },

        update: function ( ) {
             throw "not implemented";
        }


    } );

    return new Grid();


} );
