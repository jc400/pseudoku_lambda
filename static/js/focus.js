"use strict";

function init() {

    // add move() to keydown event
    window.addEventListener("keydown", move);

    // start focus on board
    document.querySelector("#a00 > input").focus();

}
window.addEventListener("load", init);



function move(event){

    let k = event.key;
    if (k === 'ArrowRight' || k === 'ArrowLeft' || k === 'ArrowUp' || k === 'ArrowDown'){ 

        // get currently focused input
        let current = getCurrent();
        if (current) {

            let row = parseInt(current.substring(1,2));
            let col = parseInt(current.substring(2,3));
        
            // calculate new coords based on arrow
            if (k === 'ArrowRight') { col = (col + 1) % 9 }
            if (k === 'ArrowDown')  { row = (row + 1) % 9 }
            if (k === 'ArrowLeft')  { 
                col = (col === 0)? 8 : col-1;
            }
            if (k === 'ArrowUp'){
                row = (row === 0)? 8 : row-1;
            }

            // reconstruct the id, select it and focus it
            current = 'a' + row + col;
            document.querySelector('#' + current + '> input').focus();
        }
    }
}

function getCurrent() {
    // <td id="a84"><input name="a84">
    // input has actual focus, so we retrieve tag from its name
    return document.activeElement.name;
}
