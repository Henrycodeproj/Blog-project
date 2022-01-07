var button = document.getElementById('following')
var check = document.getElementById('check')
 
 function getUserID(ID){
  return followUnfollow(ID)
 }

//  button.addEventListener('click', ()=>{
//   followUnfollow(getUserID)
// });

function followUnfollow(ID){
 if(button.classList.contains('follow')){
    button.classList.remove('btn', 'btn-dark', 'btn-sm','follow')
    button.classList.add('btn', 'btn-secondary', 'btn-sm','following')
    button.innerText = "Following"
    button.appendChild(check)
    check.classList.add('fas','fa-check-circle')
    check.style.marginLeft = "5px"
    follow(ID)
   }
  else if(button.classList.contains('following')){
    button.classList.remove('btn', 'btn-secondary', 'btn-sm','following')
    button.classList.add('btn', 'btn-dark', 'btn-sm','follow')
    button.innerText = "Follow"
    check.classList.remove('fas', 'fa-check-circle')
    unfollow(ID)
  }
};
function unfollow(ID) {  //sends to python route for dislikes without updating
    const url = `/unfollow/${ID}`;
  fetch(url, {
    method: 'POST',
  }).then((response) => {
    var unfollow =response.json
    var following = document.getElementById('following')
 });
}
function follow(ID) {  //sends to python route for dislikes without updating
    const url = `/follow/${ID}`;
  fetch(url, {
    method: 'POST',
  }).then((response) => {
 });
}