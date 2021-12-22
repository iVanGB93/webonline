let botonUsuarios = document.querySelector('#usuarios-btn');
let botonSmallBar = document.querySelector('#minimenu-btn');
let panelLateral = document.querySelector('.panel-lateral');
let contenedorChat = document.querySelector('.contenedor-chat');
let smallLinkBar = document.querySelector('.small-link-bar');

botonUsuarios.onclick = () => {
    panelLateral.classList.toggle('active');
    smallLinkBar.classList.remove('active')
    contenedorChat.classList.toggle('deactive');
}

botonSmallBar.onclick = () => {
    smallLinkBar.classList.toggle('active');
    panelLateral.classList.remove('active');
    contenedorChat.classList.toggle('deactive');
}