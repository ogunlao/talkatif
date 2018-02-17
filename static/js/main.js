//init for select button
$(document).ready(function() {

     $(".datetimepicker").flatpickr(
       {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        altInput: true,
        altFormat: "F j, Y H:i",
        disableMobile: "true",
    }
     );

 });

 $(document).ready(function(){
	$('.right.menu.open').on("click",function(e){
        e.preventDefault();
		$('.ui.vertical.menu').toggle();
	});

	$('.ui.dropdown').dropdown();

  $('.ui.checkbox')
  .checkbox();

  $('.message .close')
  .on('click', function() {
    $(this)
      .closest('.message')
      .transition('fade')
    ;
  });

  $('.ui .item').on('click', function() {
   $('.ui .item').removeClass('active');
   $(this).addClass('active');
});

  $('.ui.accordion')
  .accordion();

  $('#multi-select')
  .dropdown();


});
