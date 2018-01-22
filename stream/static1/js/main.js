$(document).ready(function() {
            var sideslider = $('[data-toggle=collapse-side]');
            var sel = sideslider.attr('data-target');
            var sel2 = sideslider.attr('data-target-2');
            sideslider.click(function(event){
                $(sel).toggleClass('in');
                $(sel2).toggleClass('out');
            });
        });

$().alert('close')

$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
});

$(function () {
  $('[data-toggle="tooltip"]').tooltip({html: true})
})
            // $(function () {
            //     $('.datetime-input').datetimepicker({
            //         format:'YYYY-MM-DD HH:mm:ss'
            //     });
            // })
            
// Submit post on submit
$('#post-form').on('submit', function(event){
    event.preventDefault();
    console.log("form submitted!")  // sanity check
    create_post();
});
