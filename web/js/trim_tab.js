
{
    // Get a reference to the canvas element
let canvas = document.getElementById('trimTabCanvas');
let barCanvas = document.getElementById('trimTabBarCanvas');
let image = document.getElementById('wing_container')
canvas.width = image.getBoundingClientRect().width;
console.log("width: "+String(canvas.width))

// Get a 2D drawing context
let ctx = canvas.getContext('2d');
let barCtx = barCanvas.getContext('2d');

barCtx.strokeStyle = 'black';  // Line color
barCtx.lineWidth = 2;         // Line width

// Draw the line
barCtx.beginPath();
let barBox = canvas.getBoundingClientRect();
barCtx.moveTo(barBox.width/2, 0);
barCtx.lineTo(barBox.width/2, barBox.height);
barCtx.setLineDash([5, 5]);
barCtx.stroke();

// Set line properties (optional)
ctx.strokeStyle = 'blue';  // Line color
ctx.lineWidth = 2;         // Line width

// Draw the line
ctx.beginPath();
let box = canvas.getBoundingClientRect();
let len = 40
let theta = Math.PI/2
ctx.moveTo(box.width/2, 0);
let currentTargetX = box.width/2+len*Math.cos(theta);
let currentTargetY = len*Math.sin(theta)
ctx.lineTo(currentTargetX, currentTargetY);
ctx.stroke();

var isDragging = false;
var offsetX, offsetY;

function drawCircle(x, y, radius) {
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.fillStyle = 'red';
    ctx.fill();
    ctx.closePath();
}

// Draw an initial circle
var circleRadius = 5;
drawCircle(currentTargetX, currentTargetY, circleRadius);

function checkCollision(x, y) {
    var dx = x - currentTargetX;
    var dy = y - currentTargetY;
    return Math.sqrt(dx * dx + dy * dy) < circleRadius;
}

canvas.addEventListener('mousedown', function (e) {
    var mouseX = e.clientX - canvas.getBoundingClientRect().left;
    var mouseY = e.clientY - canvas.getBoundingClientRect().top;

    if (checkCollision(mouseX, mouseY)) {
        isDragging = true;
        offsetX = mouseX - currentTargetX;
        offsetY = mouseY - currentTargetY;
    }
});

function set_trimtab_angle_internal(currentTheta){
    currentTargetX = box.width/2+len*Math.cos(currentTheta)
    currentTargetY = len*Math.sin(currentTheta)
    console.log("current x: "+String(currentTargetX+" Current y: "+String(currentTargetY)))
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
    ctx.beginPath()
    ctx.strokeStyle = 'blue';  // Line color
    ctx.lineWidth = 2;         // Line width
    ctx.moveTo(box.width/2, 0);
    ctx.lineTo(currentTargetX, currentTargetY);
    ctx.stroke();
    ctx.closePath();
    drawCircle(currentTargetX, currentTargetY, circleRadius);
}

function set_trimtab_angle(currentTheta){
    set_trimtab_angle_internal(currentTheta+Math.PI/2)
}
eel.expose(set_trimtab_angle)

canvas.addEventListener('mousemove', function (e) {
    if (isDragging) {
        var mouseX = e.clientX - canvas.getBoundingClientRect().left;
        var mouseY = e.clientY - canvas.getBoundingClientRect().top;
        currentTargetX = mouseX - offsetX;
        currentTargetY = mouseY - offsetY;
        console.log("currentx/len: "+String(currentTargetX/len))
        let secondQuadrant = false
        if(currentTargetX>len){
            currentTargetX-=canvas.getBoundingClientRect().width/2
            if(currentTargetX>len){
                currentTargetX = len
            }
            secondQuadrant=true
        }
        currentTheta = Math.PI-Math.asin(currentTargetX/len)
        if(secondQuadrant){
            currentTheta-=Math.PI/2
        }
        eel.set_trimtab_angle(currentTheta)
        set_trimtab_angle_internal(currentTheta)
        console.log("Current theta: "+currentTheta)
       
    }
});

window.addEventListener('mouseup', function () {
    isDragging = false;
});
}