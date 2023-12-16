let botonUsuarios = document.querySelector('#usuarios-btn');
let botonSmallBar = document.querySelector('#minimenu-btn');
let botonContactos = document.querySelector('#contactos-btn');


let panelLateral = document.querySelector('.panel-lateral');
let contenedorChat = document.querySelector('.contenedor-chat');
let smallLinkBar = document.querySelector('.small-link-bar');

let tabContactos = document.querySelector('.tab-contactos');
let tabUsuarios = document.querySelector('.tab-usuarios');


botonContactos.onclick = () => {
    if (botonContactos.classList.contains('active')) {
        botonContactos.classList.remove('active');
        tabContactos.classList.remove('active');
        contenedorChat.classList.remove('deactive');
        panelLateral.classList.remove('active');
    } else {
        botonContactos.classList.add('active');
        tabContactos.classList.add('active');
        contenedorChat.classList.add('deactive');
        panelLateral.classList.add('active');
    };
    if (botonUsuarios.classList.contains('active')) {
        botonUsuarios.classList.remove('active');
    };
    if (botonSmallBar.classList.contains('active')) {
        botonSmallBar.classList.remove('active');
    };
    
    tabUsuarios.classList.remove('active');
    smallLinkBar.classList.remove('active');
};
 
botonUsuarios.onclick = () => {
    if (botonUsuarios.classList.contains('active')) {
        botonUsuarios.classList.remove('active');
        tabUsuarios.classList.remove('active');
        contenedorChat.classList.remove('deactive');
        panelLateral.classList.remove('active');
    } else {
        botonUsuarios.classList.add('active');
        tabUsuarios.classList.add('active');
        contenedorChat.classList.add('deactive');
        panelLateral.classList.add('active');
    };
    if (botonContactos.classList.contains('active')) {
        botonContactos.classList.remove('active');
    };
    if (botonSmallBar.classList.contains('active')) {
        botonSmallBar.classList.remove('active');
    };

    tabContactos.classList.remove('active');
    smallLinkBar.classList.remove('active');
};

botonSmallBar.onclick = () => {
    if (botonSmallBar.classList.contains('active')) {
        botonSmallBar.classList.remove('active');
        smallLinkBar.classList.remove('active');
        contenedorChat.classList.remove('deactive');
        panelLateral.classList.remove('active');
    } else {
        botonSmallBar.classList.add('active');
        smallLinkBar.classList.add('active');
        contenedorChat.classList.add('deactive');
        panelLateral.classList.add('active');
    };
    if (botonContactos.classList.contains('active')) {
        botonContactos.classList.remove('active');
    };
    if (botonUsuarios.classList.contains('active')) {
        botonUsuarios.classList.remove('active');
    };

    tabUsuarios.classList.remove('active');
    tabContactos.classList.remove('active');


};