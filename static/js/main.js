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


     $('.like-comment').click(function(ev){
           comment_id = $(this).attr('id')
           liked_id = "liked_"+comment_id
           liked_value = $("#"+liked_id).text()
           //console.log(liked_value)

           $.ajax({

                    type: "POST",
                    url: "/comments/like/"+comment_id+"/",
                    data: {'comment_id': $(this).attr('id'), 'csrfmiddlewaretoken': '{{ csrf_token }}'},
                    dataType: "json",
                    success: function(response) {
                      //I could only update it using the error function
                           //liked_value = liked_value + 1
                           //$("#"+liked_id).text(response.total_comment_like);
                     },
                     error: function(rs, e) {
                         //console.log(rs.responseText);
                           if($('.like-comment').hasClass("liked")){
                               liked_value = Number(liked_value) - 1
                               if (liked_value == -1){ liked_value = 0};
                                $('.like-comment').removeClass("liked");

                           }else{
                               liked_value = Number(liked_value) + 1
                               $('.like-comment').addClass("liked");
                             };
                         $("#"+liked_id).text(liked_value);
                         }
               });
     });

     $('.dislike-comment').click(function(ev){
           comment_id = $(this).attr('id')
           disliked_id = "disliked_"+comment_id
           liked_value = $("#"+disliked_id).text()
           //console.log(liked_value)

           $.ajax({

                    type: "POST",
                    url: "/comments/dislike/"+comment_id+"/",
                    data: {'comment_id': $(this).attr('id'), 'csrfmiddlewaretoken': '{{ csrf_token }}'},
                    dataType: "json",
                    success: function(response) {
                      //I could only update it using the error function
                           //liked_value = liked_value + 1
                           //$("#"+liked_id).text(response.total_comment_like);
                     },
                     error: function(rs, e) {
                         //console.log(rs.responseText);
                           if($('.dislike-comment').hasClass("disliked")){
                               liked_value = Number(liked_value) - 1
                               if (liked_value == -1){ liked_value = 0};
                                $('.dislike-comment').removeClass("disliked");

                           }else{
                               liked_value = Number(liked_value) + 1
                               $('.dislike-comment').addClass("disliked");
                             };
                         $("#"+disliked_id).text(liked_value);
                         }
               });
     });

 });
