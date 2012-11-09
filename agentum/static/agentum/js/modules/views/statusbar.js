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
define( "agentum_statusbar", ["dat_gui", "agentum_layout"], function ( Dat, view ) {


    var statusbar = new Dat.GUI({
        autoPlace: false,
        hideable: false,
        showCloseButton: false,
        width: 900
    });

    view.$statusbar.prepend(statusbar.domElement);

    return statusbar;


} );