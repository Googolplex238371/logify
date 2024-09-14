window.onload = function(){wifi = document.getElementById("wifi").value
ban = document.getElementById("ban").value //selects element
document.getElementById("content").innerHTML += '<div id="main" style = "display:none"><div id="wifi"> <h1 class = "fa">'+wifi+'</h1> </div><div id="ban"> <h1 class = "fa" style="color :red">'+ban+'</h1> </div></div><style>#main {position:relative; z-index: 1;  height: 400px; width:400px;   } #wifi {font-size:100px;position:absolute; z-index: -1; height: 80px; width:200px;   } #ban {font-size:100px;z-index: -1;position: absolute;left:16px;opacity:0}</style>'
}
a = 0
setInterval(function(){
  if(window.navigator.onLine){
    document.getElementById("main").style.display="block";
    document.getElementById("ban").style.opacity = Math.abs(Math.sin(a)).toString();
    a+=Math.PI/135}
},10) //shows the main screen and hides the animation
