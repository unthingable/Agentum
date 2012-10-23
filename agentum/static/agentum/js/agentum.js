/**
 * Created with JetBrains PhpStorm.
 * Author: Kirill Cherkashin
 * Date: 10/17/12
 * Time: 7:58 PM
 *
 * This is the main part of the program which loads all modules and puts everything together.
 */

require.config( {
    paths: {
        jquery:           'agentum/js/libs/jquery',
        underscore:       'agentum/js/libs/underscore-min',
        backbone:         'agentum/js/libs/backbone-min',
        dat_gui:          'agentum/js/libs/dat.gui',
        agentum_router:   'agentum/js/modules/router',
        agentum_layout:   'agentum/js/modules/layout',
        agentum_api:      'agentum/js/modules/api',
        agentum_sim:      'agentum/js/modules/sim',
        agentum_grid:     'agentum/js/modules/grid',
        agentum_controls: 'agentum/js/modules/controls'
    }
} );

define( "agentum/js/agentum", [ "agentum_router", "agentum_layout" , "agentum_api", "agentum_grid", "agentum_controls", "agentum_sim" ], function ( router, layout, api, grid, controls, sim ) {
    "use strict";


    /**
     * Connect to the socket
     */
    var url = location.protocol.replace( "http", "ws" ) + location.host + "/data";
    /* New let's attach some events to the socket. */
    sim.socket = api.listen( url )
    /*e.g. if socket receives "sim action params params2 params3", method "action" of the sim object will be called with (params, [params2, params3]) as arguements   */
        .on( "sim", sim )
    /*e.g. Now we pass a function, not an object, so for "cell params", this function will be called     */
        .on( "cell", grid.update.bind( grid ) );



    sim.on( "space", function ( type, size ) {
        grid.set_size( size[0], size[1] );
    } );

    sim.step = function () {
        sim.socket.send( "step" );
    };


    controls.add( sim, "step" );
    controls.add( grid, "draw" );


    sim.grid = grid;
    sim.controls = controls;


    return sim;


} );