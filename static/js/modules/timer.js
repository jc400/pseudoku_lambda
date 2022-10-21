"use strict";

/*  
    Timer.js
    Holds JS object that implements timer functionality. We save this object
    to the window so we can control timer externally (with window.timer.stop(), etc)
*/

class Timer {
    constructor() {
        this.timeEl = document.getElementById("timer");
        this.running = false;
        this.handle = null;
    }

    increment() {
        let timeStr = this.timeEl.value; 
        let hrs = parseInt(timeStr.substring(0, 2));
        let min = parseInt(timeStr.substring(3, 5));
        let sec = parseInt(timeStr.substring(6, 8));

        // increment total seconds
        let totalSec = (hrs * 3600) + (min * 60) + sec;
        totalSec += 1;

        // convert back to string, put into time element
        hrs = Math.floor(totalSec / 3600);
        min = Math.floor((totalSec % 3600) / 60);
        sec = totalSec % 60;
        let pad = function (x) {
            if (x < 10)
                return '0' + x;
            else
                return '' + x;
        };
        this.timeEl.value = pad(hrs) + ':' + pad(min) + ':' + pad(sec);
    };
    boundincrement = this.increment.bind(this);

    start() {
        if (!this.running) {
            this.handle = setInterval(this.boundincrement, 1000);
            this.running = true;
        }
    };

    stop() {
        this.running = false;
        clearInterval(this.handle);
    };
}

export {Timer};

/*
document.addEventListener("DOMContentLoaded", function() {
    window.timer = new Timer();
    window.timer.start();
}, false);
*/