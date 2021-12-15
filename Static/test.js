function test(fun){
    console.log(fun)
  let id = 1;
  console.log('function test ran')
  fetch(`/likes/${id}`, {
      method: 'POST',
      //body: JSON.stringify({likes: 1}),
  }).then((response) => {
  console.log(response)
  });
}

/**
fetch(url, {
  method: 'post',
  headers: {},
  body: JSON.stringify(data),
}) 
*/
var tree = "{{fun|safe}}"
console.log(tree)
const toggle = document.querySelector('.fa-thumbs-up')
let clicked = false

toggle.addEventListener('click', () =>{
  if (!clicked){
  clicked = true;
  toggle.classList.remove('far')
  toggle.classList.remove('fa-thumbs-up')
  toggle.classList.add('fa')
  toggle.classList.add('fa-thumbs-up')
  }
  else{
    clicked = false;
    toggle.classList.remove('fa')
    toggle.classList.remove('fa-thumbs-down')
    toggle.classList.add('far')
    toggle.classList.add('fa-thumbs-up')
  }
});