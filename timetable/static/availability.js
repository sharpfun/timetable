var days = new Array(
    "Mon",
    "Tue",
    "Wed",
    "Thu",
    "Fri"
);
var timeslots = new Array(
    " 8-10",
    "10-12",
    "12-14",
    "14-16",
    "16-18",
    "18-20"
);
var state = new Array(days.length);
for (var d = 0; d < days.length; d++) {
    state[d] = new Array(timeslots.length);
    for (var t = 0; t < timeslots.length; t++) {
        state[d][t] = 0;
    }
}
function decodeState(availability) {
    availability = availability.split(":");
    for (var d = 0; d < days.length; d++) {
        for (var t = 0; t < timeslots.length; t++) {
            state[d][t] = availability[2*d+1].charAt(t)
        }
    }
}
function readState() {
    availabilityField = document.getElementById("availability");
    decodeState(availabilityField.value);
}
function writeState() {
    var result = "";
    for (var d = 0; d < days.length; d++) {
        result += days[d] + ":";
        for (var t = 0; t < timeslots.length; t++) {
            result += state[d][t]
        }
        result += ":"
    }
    availabilityField.value = result;
}
var state_red = "0";
var state_yellow = "5";
var state_green = "+";
var black = "rgb(0,0,0)";
var red = "rgb(220,0,0)";
var yellow = "rgb(255,255,0)";
var green = "rgb(120,255,120)";


var normalFont = "10px sans-serif";
var xOffset = 30;
var xResolution = 35;
var yOffset = 14;
var fontOffset = 10;
var yResolution = 30;


function drawCanvas() {
    readState();
    
    var canvas = document.getElementById("availability_canvas");
    ctxt = canvas.getContext("2d");
    //ctxt.fillStyle = "rgb(230,230,230)";
    //ctxt.fillRect(0,0,xOffset+days.length*xResolution,yOffset+timeslots.length*yResolution);
    
    ctxt.fillStyle = black;
    ctxt.lineWidth = 1;
    ctxt.font = normalFont;
    for (var d = 0; d < days.length; d++) {
        ctxt.fillText(days[d], xOffset + d*xResolution+5, 10);
    }
    for (var t = 0; t < timeslots.length; t++) {
        ctxt.fillText(timeslots[t], 0, yOffset+t*yResolution+fontOffset);
    }
    for (var d = 0; d < days.length; d++) {
        for (var t = 0; t < timeslots.length; t++) {
            drawCell(d, t);
        }
    }
}

function drawCell(d, t) {
    ctxt.save();
    ctxt.beginPath();
    ctxt.rect(xOffset+d*xResolution, yOffset+t*yResolution, xResolution, yResolution);
    ctxt.clip()
    ctxt.transform(1,0,0,1,xOffset+d*xResolution,yOffset+t*yResolution)
    switch(state[d][t]) {
        case state_red:
            ctxt.fillStyle = black;
            ctxt.fillRect(0,0,xResolution,yResolution)
            ctxt.lineCap = "round";
            ctxt.lineWidth = 5;
            ctxt.strokeStyle = red;
            ctxt.beginPath();
            ctxt.moveTo(xResolution/6,yResolution/6);
            ctxt.lineTo((5*xResolution)/6,(5*yResolution)/6);
            ctxt.moveTo((5*xResolution)/6,yResolution/6);
            ctxt.lineTo(xResolution/6,(5*yResolution)/6);
            ctxt.stroke();
            break;
        case state_green:
            ctxt.fillStyle = green;
            ctxt.fillRect(0,0,xResolution,yResolution)
            ctxt.lineCap = "round";
            ctxt.lineJoin = "round";
            ctxt.lineWidth = 5;
            ctxt.strokeStyle = black;
            ctxt.beginPath();
            ctxt.moveTo(6,(2*yResolution)/3);
            ctxt.lineTo(xResolution/3,(5*yResolution)/6)
            ctxt.lineTo(xResolution-6,yResolution/6)
            ctxt.stroke();
            break;
        case state_yellow:
            ctxt.fillStyle = green;
            ctxt.fillRect(0,0,xResolution,yResolution)
            ctxt.lineWidth = 5;
            ctxt.strokeStyle = black;
            ctxt.fillStyle = yellow;
            ctxt.beginPath();
            var r = xResolution;
            if (yResolution < r) r = yResolution;
            r = r/4;
            ctxt.arc(xResolution/2,yResolution/2,r,0,2*Math.PI);
            ctxt.fill();
            ctxt.stroke();
            break;
    }
    ctxt.restore()
}

function changeAvailability(event) {
    var x,y;
    if (event.offsetX) { // IE and other broswers which have it
        x = event.offsetX;
        y = event.offsetY;
    } else { // Firefox and other browsers which have it
        x = event.pageX - event.originalTarget.offsetLeft;
        y = event.pageY - event.originalTarget.offsetTop;
    }
    var d = Math.floor((x-xOffset)/xResolution);
    if (d < 0 || d >= days.length) return;
    var t = Math.floor((y-yOffset)/yResolution);
    if (t < 0 || t >= timeslots.length) return;
    switch (state[d][t]) {
        case state_green:
            state[d][t] = state_yellow;
            break;
        case state_yellow:
            state[d][t] = state_red;
            break;
        case state_red:
            state[d][t] = state_green;
            break;
    }
    writeState();
    drawCell(d,t);
}

var xResolutionInline = 20;
var yResolutionInline = 5;
function drawInlineCanvases() {
    var canvases = document.getElementsByTagName("canvas");
    for (var i = 0; i < canvases.length; i++) {
        var c = canvases[i].getContext("2d");
        //c.fillStyle = "rgb(230,230,230)";
        //c.fillRect(0,0,xOffset+days.length*xResolution,yOffset+timeslots.length*yResolution);
        decodeState(canvases[i].textContent.trim());
        for (var d = 0; d < days.length; d++) {
            for (var t = 0; t < timeslots.length; t++) {
                switch (state[d][t]) {
                    case state_red:
                        c.fillStyle = black;
                        c.fillRect(xResolutionInline*d, yResolutionInline*t, xResolutionInline-1, yResolutionInline-1);
                        c.fillStyle = red;
                        c.fillRect(xResolutionInline*d+4, yResolutionInline*t+1, xResolutionInline-9, yResolutionInline-3);
                        break;
                    case state_yellow:
                        c.fillStyle = green;
                        c.fillRect(xResolutionInline*d, yResolutionInline*t, xResolutionInline-1, yResolutionInline-1);
                        c.fillStyle = black;
                        c.fillRect(xResolutionInline*d+7, yResolutionInline*t, xResolutionInline-15, yResolutionInline-1);
                        c.fillStyle = yellow;
                        c.fillRect(xResolutionInline*d+8, yResolutionInline*t+1, xResolutionInline-17, yResolutionInline-3);
                        break;
                    case state_green:
                        c.fillStyle = green;
                        c.fillRect(xResolutionInline*d, yResolutionInline*t, xResolutionInline-1, yResolutionInline-1);
                        break;
                }
            }
        }
    }
}

