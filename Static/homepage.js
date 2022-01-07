
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


let reportingUser = JSON.stringify('{{current_user.username}}')
var post = document.getElementById('message-text')
var reason = document.getElementById('recipient-name')

const getReport = (postid) => {
  console.log(postid)
  console.log(reportingUser)
  var entry = {
    postID: postid,
    reportingUser: reportingUser,
    title:post.value,
    reason:reason.value
  };
  console.log(entry)
  report(entry)
}

const generateGetReport = (event) => {
  const e = document.getElementById('id-tracker');
  const id = e.innerHTML;
  getReport(id);
}

function getCurrentPost(id){
  var reportSubmit = document.getElementById('reportSubmit');
  const e = document.getElementById('id-tracker');
  e.innerHTML = `${id}`;
  reportSubmit.removeEventListener('click', generateGetReport); 
  reportSubmit.addEventListener('click', generateGetReport);
}

function report(entry) {  //send reports without leaving current page
    const url = `/report`;
  fetch(url, {
    method: 'POST',
    body: JSON.stringify(entry),
    contentType: "application/json"
  }).then((response) => {
    post.value=''
    reason.value=''
    alert('Thank you. Your report has been submitted.')
    return response.text();
  }).then(function(entry){
    //console.log(text);
  });
}
