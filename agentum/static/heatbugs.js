/**
 * Created with JetBrains PhpStorm.
 * Author: Kirill Cherkashin
 * Date: 10/17/12
 * Time: 8:23 PM
 *
 *  Heatbugs model
 */
require( ["agentum/js/agentum"], function ( agentum ) {
    /**
     * Some shortcuts
     */
    var grid = agentum.grid;


    /**
     * An example of how we can handle "name" event to see, if we're connected to the correct instance of the model.
     */
    agentum.on( "name", function ( name ) {
        if( name !== "heatbugs" ) {
            alert( "Looks like were connected to a wrong instance. " + name + " instead of heatbugs" );
        }
    } );


    /**
     * An example of how we can add a control.
     *
     * We'll add "zoom" control to allow the user scale the grid.
     * max() doesn't work properly for some reason
     */

    grid.set_zoom( 3 );
    agentum.controls.add( grid, "zoom" ).min( 1 ).onChange( grid.set_zoom.bind( grid ) );


    /**
     * An example of how we can handle clicks and send data back to the server.
     */

    grid.on( "click", function ( x, y ) {
        agentum.socket.send( "sim click [" + x + ", " + y + "]" );
    } );




    /**
     * Since we receive heat values instead of colors, we have to write our own Handler
     */

    /**
     * Maximum heat on the map
     * @type {Number}
     * @private
     */
    var _max = 0;

    var steps = 0;


    /**
     * Transforms heat into color representation
     * @param heat
     * @return {Array} Color
     */
    var _calculate_color = function ( heat ) {
        _max = Math.max( heat, _max );
        return [ Math.round( heat * 255 / _max ), 0, 0]
    };



    agentum.socket.on( "cell", function ( cell, heat ) {
        if( cell == "all" ) {
            return this.clear( "black" );
        }


        this.set_pixel( cell, _calculate_color( heat[1] ) );

        // We only update the canvas after we receive all cells.
        if( ++steps % 10030 == 0 ) {
            this.draw();
        }

        return true;
    }.bind( grid ) );


    /**
     * Let's do the first step
     */

    agentum.step();


} );