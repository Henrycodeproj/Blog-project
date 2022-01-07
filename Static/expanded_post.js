  //let idJSON='{{json_postid|tojson}}';
  //let parsedObj = JSON.parse(idJSON);
  //let { postID } = parsedObj
  function like(id) { // sends to python route for likes without updating
    let idJSON='{{json_postid|tojson}}';
    let parsedObj = JSON.parse(idJSON);
    let { postID } = parsedObj
      const url = `/likes/${postID}`;
      //console.log(url);
      fetch(url, {
        method: 'POST',
      }).then((response) => {
      //console.log(response)
     });
    }
  
    function dislike(id) {  //sends to python route for dislikes without updating 
    let idJSON='{{json_postid|tojson}}';
    let parsedObj = JSON.parse(idJSON);
    let { postID } = parsedObj
      const url = `/dislikes/${postID}`;
      //console.log(url);
      fetch(url, {
        method: 'POST',
      }).then((response) => {
      //console.log(response)
     });
    }
  
    function test() {  //sends to python route for dislikes without updating 
      const url = `/random`;
      //console.log(url);
      fetch(url, {
        method: "GET",
      }).then((response) => {
      console.log(response.json())
     });
    }
  
    function deleteComment(id) {  //sends to python route for dislikes without updating
      if (confirm("Are you sure you want to delete your comment?")){
        const url = `/comment_delete/${id}`;
      console.log(url);
      fetch(url, {
        method: 'POST',
      }).then((response) => {
        var commentIDRef = document.getElementById(id+'wrap').remove();
     });
      }
    }
  
   var commentID = 0
   const submit = document.querySelector('#comment_submit')
  
   submit.addEventListener('click', () =>{ 
      editComment(commentID)
    })
  
  
  
    function getComment(id) {  //gets comment data and inputs it into the textbox
      const url = `/get_comment/${id}`;
      //console.log(url);
      fetch(url, {
        method: 'POST',
      }).then(response => {
      return response.json();
     }).then (response_data => {
      let data = response_data
      var x = document.getElementById("message-text").value = data;
    commentID = id
     })
    }
  
  
  
    function editComment(commentID) {  //sends to python route for dislikes without updating
      const url = `/edit_comment/${commentID}`;
      var returnedNewComment = document.getElementById("message-text").value;
      //console.log(url);
      fetch(url, {
        method: 'POST',
        body: JSON.stringify(returnedNewComment),
      }).then((response) => {
      return response.json();
      }).then (response_data => {  // returns a comment from server which we then replace and once refreshes it'll be saved
      let editedComment = response_data
      var newComment = document.getElementById(commentID).innerText = editedComment;
      });
    }
  
  const toggle = document.querySelector('.fa-thumbs-up')
  const numUpdate = document.querySelector('#count')
  var current_user_is_anony = '{{current_user_check|safe}}'
  
    toggle.addEventListener('click', () =>{ // checks status for users
    if (current_user_is_anony == "True"){
      likeDislike()
    }
    else{
      likeDislike() // returns handler for likes and dislikes
    }
  
  
    function likeDislike(){
    if (toggle.classList.contains('far')){ 
    toggle.classList.remove('far')
    toggle.classList.add('fa')
    numUpdate.textContent++
    //toggle.style.color = "blue"
    like()
    }
    else if(toggle.classList.contains('fa')){
      toggle.classList.remove('fa')
      toggle.classList.add('far')
      dislike()
      numUpdate.textContent--
      //toggle.style.color = "black"
    }
    }
  });