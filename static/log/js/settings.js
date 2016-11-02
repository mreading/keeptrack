$("input[type=password]").keyup(function(){
    var ucase = new RegExp("[A-Z]+");
  	var lcase = new RegExp("[a-z]+");
  	var num = new RegExp("[0-9]+");

    if($("#password1").val() == $("#password2").val()){
      $("#pwmatch").removeClass("glyphicon-remove");
      $("#pwmatch").addClass("glyphicon-ok");
      $("#pwmatch").css("color","#00A41E");
    }else{
      $("#pwmatch").removeClass("glyphicon-ok");
      $("#pwmatch").addClass("glyphicon-remove");
      $("#pwmatch").css("color","#FF0004");
}
