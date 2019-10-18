
var imageLoader = document.getElementById('imageLoader');
var canvas = document.getElementById('imageCanvas');
var context = canvas.getContext('2d');
var startImg = new Image();

document.getElementById("imageLoader").onchange = function(e) {
loadImage(
    e.target.files[0],
    function(img) {
    context.drawImage(img, 0, 0, 225, 225);
    sendImg();
    },
    { 
    aspectRatio: 1,
    orientation: true,
    canvas: true
    }
);
};

function sendImg(){
document.getElementById("spinner-loading").hidden = false;
document.getElementById("banner-pinehead").hidden = true;
document.getElementById("banner-notpinehead").hidden = true;
document.getElementById("banner-placeholder").hidden = true;
imgData = canvas.toDataURL("image/png")

$.ajax({
    type: "POST",
    xhrFields: {
        withCredentials: false
    },
    url: apiUrl,
    data: imgData.substr(22),
    contentType: "application/json",
    success: function(data){displayResponse(data);},
    failure: function(errMsg) {
        alert(errMsg);
    }
});
}

function displayResponse(data){
if (data=="Pinehead"){
    document.getElementById("spinner-loading").hidden = true;
    document.getElementById("banner-pinehead").hidden = false;
    document.getElementById("banner-notpinehead").hidden = true;
    document.getElementById("banner-placeholder").hidden = true;
} else {
    document.getElementById("spinner-loading").hidden = true;
    document.getElementById("banner-pinehead").hidden = true;
    document.getElementById("banner-notpinehead").hidden = false;
    document.getElementById("banner-placeholder").hidden = true;
}
}

startImg.onload = function(){
context.drawImage(startImg, 0, 0, 225, 225);
}

startImg.src = 'logo.png';

document.getElementById("spinner-loading").hidden = true;
document.getElementById("banner-pinehead").hidden = true;
document.getElementById("banner-notpinehead").hidden = true;
document.getElementById("banner-placeholder").hidden = false;


