$(document).ready(function() {
            var sideslider = $('[data-toggle=collapse-side]');
            var sel = sideslider.attr('data-target');
            var sel2 = sideslider.attr('data-target-2');
            sideslider.click(function(event){
                $(sel).toggleClass('in');
                $(sel2).toggleClass('out');
            });
        });

$(document).ready(function(){
  $().alert('close')
});

$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
});

$(document).ready(function () {
  $('[data-toggle="tooltip"]').tooltip({html: true})
});

$(document).ready(function () {
                $('.datetime-input').datetimepicker({
                    format:'YYYY-MM-DD HH:mm:ss'
                });
            });

            // To style all <select>s
      $(document).ready(function(){
         $('select').selectpicker();
       });
