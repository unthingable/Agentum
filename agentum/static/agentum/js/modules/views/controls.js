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
 * Time: 8:34 PM
 *
 * Controls model uses dat-gui library to organize control for the simulation.
 *
 */
define( "agentum_controls", ["dat_gui", "agentum_layout"], function ( Dat, view ) {


    var controls = new Dat.GUI({
        autoPlace: false,
        hideable: false,
        showCloseButton: false,
        width: 900
    });

    view.$control.prepend(controls.domElement);

    return controls;


} );