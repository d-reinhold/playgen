$(document).ready(function() {
  $(".container").fadeIn("fast")
  
  $("#submit-query").click(function() {
    $(".container").slideUp("slow", function(){
      $("#searching").fadeIn("slow")
      $("#searching").slideDown(1000)
      $("#create-playlist").submit();
      setTimeout(function() {
         $("#more-searching-text").fadeIn(1000)
      }, 5000);
      
    })
    
  });
  
});