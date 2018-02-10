//Side nav button

$(".button-collapse").sideNav();

//init for select button
$(document).ready(function() {
    $('select').material_select();


    $('.datepicker').pickadate({
       format: "yyyy-mm-dd",
       selectMonths: true, // Creates a dropdown to control month
       selectYears: 15, // Creates a dropdown of 15 years to control year,
       today: 'Today',
       clear: 'Clear',
       close: 'Ok',
       closeOnSelect: false, // Close upon selecting a date,


     });

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
