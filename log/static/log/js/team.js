$("tr.athletes").hover(function() {
    $(this).css({"cursor": "pointer"})
});

$("tr.athletes").click(function() {
    window.location.href = "/log/athlete/"+$(this).attr('id');
})