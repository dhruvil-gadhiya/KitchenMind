// minor UX: pressing Enter inside search input submits form; nothing heavy
document.addEventListener('DOMContentLoaded', function(){
  const searchBox = document.getElementById('search-box');
  if(searchBox){
    searchBox.addEventListener('keydown', function(e){
      if(e.key === 'Enter'){
        // allow form submit
      }
    });
  }
});
