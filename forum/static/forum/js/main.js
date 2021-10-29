
var header = document.querySelector(".header-default");
window.onscroll = () => {
    var fromTop = window.scrollY;
    if (fromTop > 0) {
        header.classList.add("clone");
    } else {
        header.classList.remove("clone");
    }
    document.querySelector('body').classList.toggle("down", (fromTop > 300));
};

    /* var list = document.getElementByClassName('data-bg-image');
    for(var i =0; i<list.lenth; i++) {
        var bging = list[i].getAttribute('data-bg-image');
        list[i].style.backgroundImage = 
    } */

var botonTab1 = document.querySelector('#popular-tab');
var botonTab2 = document.querySelector('#recent-tab');
if (botonTab1 != null && botonTab2 != null ) {
    botonTab1.onclick = () => {
        document.querySelector(".tab-pane").classList.add("loading");
        document.querySelector(".lds-dual-ring").classList.add("loading");
        setTimeout(function() {
            document.querySelector(".tab-pane").classList.remove("loading");
            document.querySelector(".lds-dual-ring").classList.remove("loading");
        }, 500);
    };
    botonTab2.onclick = () => {
        document.querySelector(".tab-pane").classList.add("loading");
        document.querySelector(".lds-dual-ring").classList.add("loading");
        setTimeout(function() {
            document.querySelector(".tab-pane").classList.remove("loading");
            document.querySelector(".lds-dual-ring").classList.remove("loading");
        }, 500);
    };
};

var tema = document.getElementById('tema');
if (tema != null) {
    var tema = JSON.parse(document.getElementById('tema').textContent)
    document.querySelector('#'+tema).classList.add('active');
}