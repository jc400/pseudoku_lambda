"use strict";

/*
    main.js

    This holds the client-side puzzle logic. Has functionality to 
    populate/clear/reset puzzle, and it makes backend fetch() calls
    to API to get new puzzles/submit puzzles

*/

import * as timer     from "./modules/timer.js";

const ENDPOINT = 'https://5kcv9tmm3k.execute-api.us-east-2.amazonaws.com/dev'; 
const TIMER = new timer.Timer(); 

let clientState = {
    puzzleid: null,
    difficulty: 'one',
    username: 'anonymous',
    darkmode: false,
};


function init() {
    // initialize with a game
    getpuzzle(clientState['difficulty']);

    document.getElementById("nextpuzzleControl").onclick = function () {
        getpuzzle(clientState['difficulty']);
    }
}
window.onload = init;


// --------- HIGH LEVEL ---------- //

function getpuzzle(puzzleid) {
    // fetch() from API and populate(). puzzleid can be int or one/two/three/four (which is 
    // probably not the best choice). Also saves info to clientState, and sets up submit button callback

    let myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    let requestOptions = {
        method: 'GET',
        headers: myHeaders,
        //body: raw,
        redirect: 'follow'
    };

    fetch(ENDPOINT + "/getpuzzle/" + puzzleid, requestOptions)
    .then( (indata) => indata.json() )
    .then( (indata) => populate(indata) )
    .then( (indata) => savePuzzleIdToClientState(indata) )
    .then( (indata) => setUpSubmitButton(indata) );
}

function submitpuzzle(outdata) {
    // collects and submits the current puzzle. Conditionally handles json response from server.
    outdata.submission = collect();
    outdata.username = clientState['username'];
    fetch(ENDPOINT + "/submitpuzzle", {
        method: "POST",
        mode: "cors",
        cache: "no-cache",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify(outdata),
    })
    .then( (indata) => indata.json() )
    .then( (indata) => {
        if      (!indata.body.data.complete)       handleIncorrectSubmission();
        else                                  handleCorrectSubmission(indata);
    });
}


// ---------- LOW LEVEL ---------- //

// for getpuzzle()
function populate(indata) {
    // populates puzzle table using data from response object. Also resets and starts timer.
    // If no arg, it will clear the puzzle 
    let cell;
    for (let y=0; y<9; y++){
        for (let x=0; x<9; x++){
            cell = document.getElementById('a' + y + x).children[0];
            if (indata && indata.data.bitmap[y][x]){
                cell.value = indata.data.board[y][x];
                cell.className = "serverCell";
                cell.readOnly = true;
            } else {
                cell.value = "";
                cell.className = "cellinput";
                cell.readOnly = false;
            }
        }
    }
    document.getElementById("timer").value = "00:00:00";
    TIMER.start();
    return indata // so that later functions in .then() chain can work
}
function savePuzzleIdToClientState(indata){
    clientState['puzzleid'] = indata['data']['puzzleid'];
    return indata;
}
function setUpSubmitButton(indata) {
    function submitButtonCallback() {
        submitpuzzle(indata);
    }
    document.getElementById("submitbutt").onclick = submitButtonCallback;
    return indata;
}

// for submitpuzzle()
function collect() {
    // pulls board into 2D array and returns
    let out = [[],[],[],[],[],[],[],[],[]];
    let cell;
    for (let y=0; y<9; y++){
        for (let x=0; x<9; x++){
            cell = document.getElementById('a' + y + x).children[0];
            if (cell.value === "") out[y][x] = 0;
            else out[y][x] = parseInt(cell.value);
        }
    }
    return out;
}
function handleIncorrectSubmission() {
    // If submitted puzzle is wrong, change submit button to "not quite!". Clear on new input
    let sub = document.getElementById("submitbutt");
    sub.innerText = "Not quite...";
    sub.setAttribute("style", "background:red;");
    document.getElementById("puzzle").oninput = function () {
        this.oninput = "";
        sub.innerText = "Submit!";
        sub.removeAttribute("style");
    }
}
function handleCorrectSubmission(indata) {
    TIMER.stop();

    // display completeModal, show users time
    let modal = new bootstrap.Modal("#completeModal");
    modal.show();

    document.getElementById("yourtime").innerText = "Your time was: " + indata.body.data.usertime;

    // set up event handler for button
    document.getElementById("newpuzzleModal").onclick = () => {
        modal.hide();
        getpuzzle(clientState['difficulty']);
    }
}
