/**
 * Created with JetBrains PhpStorm.
 * Author: Kirill Cherkashin
 * Date: 10/18/12
 * Time: 2:03 PM
 *
 *
 */

define( "agentum_api", function () {
    "use strict";


    var _Socket = WebSocket || MozWebSocket;


    return {

        "listen": function ( url ) {
            var _callbacks = {};
            var _queue = [];
            var socket = new _Socket( url );

            socket.onopen = function (  ) {
                for( var i in _queue ) {
                    if( _queue.hasOwnProperty( i ) ) {
                        socket.send(_queue[i]);
                    }
                }

            };

            socket.onmessage = function ( event ) {
                var message = JSON.parse( event.data );
                var scope = message.shift();

                var callback_type = typeof _callbacks[scope];
                if( callback_type === "function" ) {
                    _callbacks[scope]( message.shift(), message );
                } else if( callback_type === "object" ) {
                    if( typeof _callbacks[scope].trigger === "function" ) {
                        _callbacks[scope].trigger.apply(_callbacks[scope], message );
                    }
                }
            };


            return {
                on:   function ( scope, model ) {
                    _callbacks[scope] = model;
                    return this;
                },
                send: function ( message ) {
                    if( socket.readyState ){
                        socket.send( message );
                    } else {
                        _queue.push( message );
                    }

                    return this;
                }

            }


        }
    }


} )
;