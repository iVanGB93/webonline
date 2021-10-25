let navbar = document.querySelector('.barra');
let boton = document.querySelector('#menu-btn');

boton.onclick = () =>{
  navbar.classList.toggle('active');
  boton.classList.toggle('fa-times');
}

// scroll spy 
let section = document.querySelectorAll('section');
let navLinks = document.querySelectorAll('.header .navbar a');

window.onscroll = () =>{
  navbar.classList.remove('active');
  boton.classList.remove('fa-times');

  if(window.scrollY > 0){
    document.querySelector('.header').classList.add('active');
  }else{
    document.querySelector('.header').classList.remove('active');
  }

  /* section.forEach(sec =>{
    let top = window.scrollY;
    let offset = sec.offsetTop - 200;
    let height = sec.offsetHeight;
    let id = sec.getAttribute('id');

    if(top >= offset && top < offset + height){
      navLinks.forEach(link =>{
        link.classList.remove('active');
        document.querySelector('.header .navbar a[href*='+id+']').classList.add('active');
      });
    };
  }); */
};

function loader() {
  document.querySelector('.loader-container').classList.add('active')
}
function fadeOut() {
  setTimeout(loader, 1000);
}

window.onload = () =>{
  fadeOut();
  if(window.scrollY > 0){
    document.querySelector('.header').classList.add('active');
  }else{
    document.querySelector('.header').classList.remove('active');
  }
}

document.querySelector('#login-icon').onclick = () => {
  document.querySelector('.login-form-container').classList.toggle('active');
  document.querySelector('#login-form').style.display = 'block';
  document.querySelector('#register-form').style.display = 'none';
}

var boton_login = document.getElementById('login-btn');
if (boton_login != null) {
  document.querySelector('#login-btn').onclick = () => {
    document.querySelector('.login-form-container').classList.toggle('active');
    document.querySelector('#login-form').style.display = 'block';
    document.querySelector('#register-form').style.display = 'none';
  }
  document.querySelector('#register-btn').onclick = () => {
    document.querySelector('.login-form-container').classList.toggle('active');
    document.querySelector('#login-form').style.display = 'none';
    document.querySelector('#register-form').style.display = 'block';
  }
}
document.querySelector('#close-login-form').onclick = () => {
  document.querySelector('.login-form-container').classList.remove('active');
}
document.querySelector('#boton-registro').onclick = () => {
  document.querySelector('#login-form').style.display = 'none';
  document.querySelector('#register-form').style.display = 'block';
}
document.querySelector('#boton-login').onclick = () => {
  document.querySelector('#login-form').style.display = 'block';
  document.querySelector('#register-form').style.display = 'none';
}