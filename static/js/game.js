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

    // set up skip button
    document.getElementById("nextpuzzleControl").onclick = function () {
        getpuzzle(clientState['difficulty']);
    }

    // callbacks for changing difficulty
    document.querySelectorAll("#difficulty a.dropdown-item").forEach(function(item){
        item.onclick = changeDifficulty;
    })

    // set difficulty button to correct diff
    setDifficultyCircles();

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

function changeDifficulty(event) {
    // get difficulty from selected menu item
    let newDiff = event.target.dataset["diff"];

    // save and get new puzzle
    clientState["difficulty"] = newDiff;
    getpuzzle(clientState["difficulty"]);

    // update circles
    setDifficultyCircles();
}

function setDifficultyCircles() {
    let empty = '<img src="images/empty_circle2.png" class="diff_circle">';
    let solid = '<img src="images/solid_circle.png" class="diff_circle">';
    let content = "";

    if (clientState["difficulty"] === "one"){ content = solid + empty + empty + empty; }
    if (clientState["difficulty"] === "two"){ content = solid + solid + empty + empty; }
    if (clientState["difficulty"] === "three"){ content = solid + solid + solid + empty; }
    if (clientState["difficulty"] === "four"){ content = solid + solid + solid + solid; }    
    
    document.getElementById("difficulty_button").innerHTML = content;
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

    // get reference to modal
    let modal = new bootstrap.Modal("#completeModal");

    // update content, set up event handler
    TIMER.stop();
    document.getElementById("yourtime").innerText = "Your time was: " + indata.body.data.usertime;
    document.getElementById("newpuzzleModal").onclick = () => {
        modal.hide();
        getpuzzle(clientState['difficulty']);
    }

    // display modal
    modal.show();
}
