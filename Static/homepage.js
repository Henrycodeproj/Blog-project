// alert function to delete, will get back to later
function myfunction() {
    var txt;
    if (confirm("Are you sure you want to delete this post?")) {
      {{ redirect(url_for('post'))}}
    } else {
      txt = "You pressed Cancel!";
    }
    document.getElementById("demo").innerHTML = txt;
  }

function deletecheck(){
  
}